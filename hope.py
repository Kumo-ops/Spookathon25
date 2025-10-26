

from serpapi import GoogleSearch
import os

api_key = os.getenv("SERPAPI_API_KEY")

def query_search_costumes(budget,age):
    query = f"send me exact links to listings(for example https://www.etsy.com/listing/....(dont show me pages or catagories, just exact links) to a {age} halloween costumes equal to or under ${budget} site:spirithalloween.com"
    params = {
        "q": query,
        "engine": "google",
        "api_key": api_key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    products = []
    for item in results.get("organic_results", []):
        title = item.get("title")
        link = item.get("link")
        products.append({"name": title, "link": link})
    return products

def main():
    print("Halloween Costume Finder")
    budget_input = input("Enter your budget in USD(only numbers): $")
    age_input = input("Adult or kid?")
    
    try:
        if age_input not in ["adult", "kid"]:
            raise ValueError("Invalid age category")
        age = age_input
    except ValueError:
        print("Type 'adult' or 'kid' again.")
        return

    try:
        budget = float(budget_input)
    except ValueError:
        print("Invalid Input: use a number(1..2..3..ect)")
        return
    costumes = query_search_costumes(budget,age)
    if not costumes:
        print(f"No costumes found under ${budget}. Increase budget for more results.")
        return
    print(f"\nHere are some Halloween costumes under ${budget}:")
    for idx, c in enumerate(costumes, start=1):
        print(f"{idx}. {c['name']} -> {c['link']}")
if __name__ == "__main__":
    main()