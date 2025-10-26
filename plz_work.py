import base64
import hashlib
import json
import os
import re
import secrets
import sys
import time
import urllib.parse
from pathlib import Path

import requests

# =========================
# Config (hard-coded for now)
# =========================
CLIENT_ID = "pgphnp7qkzhfj2ifsxz7qoi9"          # <-- your API Key keystring
REDIRECT_URI = "https://spookathon.com/spooky"  # <-- your redirect URI
SCOPES = os.getenv("ETSY_SCOPES", "").strip()   # optional
TOKENS_PATH = Path("etsy_tokens.json")

API_BASE = "https://api.etsy.com"
AUTH_BASE = "https://www.etsy.com"
TOKEN_URL = f"{API_BASE}/v3/public/oauth/token"
LISTINGS_URL = f"{API_BASE}/v3/application/listings"  # marketplace-level search

UNWANTED = [
    "kids", "kid", "baby", "toddler",
    "best seller", "bestseller", "popular items", "trending",
    "accessory", "accessories only", "couples set", "couples costume"
]

# ==========
# Utilities
# ==========
def die(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)

def save_tokens(tokens: dict):
    TOKENS_PATH.write_text(json.dumps(tokens, indent=2))

def load_tokens():
    if TOKENS_PATH.exists():
        return json.loads(TOKENS_PATH.read_text())
    return None

def now() -> int:
    return int(time.time())

# ===========================
# PKCE + Authorization URL
# ===========================
def make_pkce_pair():
    # RFC 7636: code_verifier = 43..128 chars from [A-Za-z0-9-._~]
    verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).rstrip(b"=").decode("ascii")
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return verifier, challenge

def build_authorize_url(client_id, redirect_uri, scopes, state, code_challenge):
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,  # must be https and must match exactly
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    if scopes:
        params["scope"] = scopes  # space-separated string
    return f"{AUTH_BASE}/oauth/connect?{urllib.parse.urlencode(params)}"

# =========================
# Token exchange / refresh
# =========================
def exchange_code_for_tokens(code: str, code_verifier: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
        "code_verifier": code_verifier,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=20)
    r.raise_for_status()
    tokens = r.json()
    tokens["_obtained_at"] = now()
    tokens["_expires_at"] = tokens["_obtained_at"] + int(tokens.get("expires_in", 3600)) - 30
    return tokens

def refresh_tokens(refresh_token: str) -> dict:
    data = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": refresh_token,
    }
    r = requests.post(TOKEN_URL, data=data, timeout=20)
    r.raise_for_status()
    tokens = r.json()
    tokens["_obtained_at"] = now()
    tokens["_expires_at"] = tokens["_obtained_at"] + int(tokens.get("expires_in", 3600)) - 30
    if "refresh_token" not in tokens:
        tokens["refresh_token"] = refresh_token
    return tokens

def ensure_access_token() -> dict:
    if not CLIENT_ID or not REDIRECT_URI:
        die("CLIENT_ID and REDIRECT_URI must be set.")
    tokens = load_tokens()
    if tokens and now() < tokens.get("_expires_at", 0):
        return tokens

    if tokens and "refresh_token" in tokens:
        try:
            tokens = refresh_tokens(tokens["refresh_token"])
            save_tokens(tokens)
            return tokens
        except Exception as e:
            print(f"Refresh failed, falling back to new auth: {e}")

    # New authorization flow
    state = secrets.token_urlsafe(24)
    verifier, challenge = make_pkce_pair()
    auth_url = build_authorize_url(CLIENT_ID, REDIRECT_URI, SCOPES, state, challenge)

    print("\n=== 1) Authorize this app ===")
    print("Open this URL in your browser, sign in, and allow access:\n")
    print(auth_url)
    print("\nAfter you approve, Etsy redirects to your registered REDIRECT_URI.")
    print("Copy the FULL redirected URL from your browser's address bar and paste it here.\n")
    redirected = input("Paste the FULL redirect URL: ").strip()

    # Parse and validate state + code
    parsed = urllib.parse.urlparse(redirected)
    q = urllib.parse.parse_qs(parsed.query)
    returned_state = (q.get("state") or [""])[0]
    code = (q.get("code") or [""])[0]

    if not code:
        die("No 'code' found in the pasted URL.")
    if returned_state != state:
        die("State mismatch. Do the authorization again.")

    tokens = exchange_code_for_tokens(code, verifier)
    save_tokens(tokens)
    return tokens

# ================================
# Strict Etsy search (marketplace)
# ================================
def is_listing_ok(title_snippet: str) -> bool:
    t = title_snippet.lower()
    return not any(bad in t for bad in UNWANTED)

def search_costumes(budget: float, gender: str, limit: int = 100):
    """
    Calls marketplace listings search and filters results:
      - active listings
      - keywords: "{gender} adult halloween costume"
      - max_price: budget
      - sort by relevancy (score desc)
    Then removes unwanted phrases and returns exact listing URLs.
    """
    tokens = ensure_access_token()
    access_token = tokens["access_token"]

    headers = {
        "x-api-key": CLIENT_ID,                    # required on all v3 requests
        "Authorization": f"Bearer {access_token}", # include OAuth token
        "Accept": "application/json",
    }

    params = {
        "state": "active",
        "keywords": f"{gender} adult halloween costume",
        "max_price": int(budget),
        "limit": min(limit, 100),
        "offset": 0,
        "sort_on": "score",
        "sort_order": "down",
    }

    r = requests.get(LISTINGS_URL, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    results = data.get("results") or data.get("listings") or data.get("data") or []
    out = []
    for item in results:
        title = (item.get("title") or "").strip()
        url = item.get("url")
        listing_id = item.get("listing_id") or item.get("listingId") or item.get("id")
        if not url and listing_id:
            url = f"https://www.etsy.com/listing/{listing_id}"
        if not url:
            continue

        blob = title.lower()
        if not is_listing_ok(blob):
            continue
        if "adult halloween costume" not in blob:
            continue

        out.append({"name": title, "link": url})

    # Deduplicate by link while preserving order
    seen, deduped = set(), []
    for p in out:
        if p["link"] not in seen:
            seen.add(p["link"])
            deduped.append(p)
    return deduped

# ======
# CLI
# ======
def main():
    print("Etsy OAuth Search: Adult Halloween Costumes (Strict)")

    budget_input = input("Enter your budget in USD (numbers only): $").strip()
    gender_input = input("Gender (male/female/unisex): ").strip().lower()

    if gender_input not in ["male", "female", "unisex"]:
        die("Invalid gender. Use: male, female, or unisex.")

    try:
        budget = float(budget_input)
    except ValueError:
        die("Invalid budget: please enter a number (e.g., 50).")

    listings = search_costumes(budget, gender_input)
    if not listings:
        print(f"\nNo active Etsy listings matched your strict filters under ${int(budget)}.")
        return

    print(f"\nExact Etsy listing links for {gender_input} adult Halloween costumes under ${int(budget)}:")
    for i, it in enumerate(listings, 1):
        print(f"{i}. {it['name']} -> {it['link']}")

if __name__ == "__main__":
    main()