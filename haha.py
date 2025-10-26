python3 - <<'PY'
from openai import OpenAI
client = OpenAI()
r = client.chat.completions.create(
    model="gpt-5",
    messages=[{"role": "user", "content": "Say hi"}]
)
print(r.choices[0].message.content)
PY
