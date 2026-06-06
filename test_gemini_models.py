import requests

GEMINI_API_KEY = "AIzaSyC2Q8gXvNGnQLQjqkagtQduNewKibZrJb8"

models = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest"
]

for model in models:
    print(f"Testing {model}...")
    res = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": "Say Hi"}]}],
        }
    )
    print(f"  Status: {res.status_code}")
    if res.status_code != 200:
        print(f"  {res.text}")

