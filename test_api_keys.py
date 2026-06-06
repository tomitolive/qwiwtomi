import requests
import json

# Test step-3.7-flash
print("Testing step-3.7-flash...")
try:
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "stepfun-ai/step-3.7-flash",
        "messages": [
            {"role": "system", "content": "Say 'Hello'"},
            {"role": "user", "content": "Say 'Hello'"}
        ],
        "max_tokens": 10,
        "temperature": 0.1,
        "stream": False
    }
    res = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test mistral-large-3
print("\nTesting mistral-large-3...")
try:
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "mistralai/mistral-large-3-675b-instruct-2512",
        "messages": [
            {"role": "system", "content": "Say 'Hello'"},
            {"role": "user", "content": "Say 'Hello'"}
        ],
        "max_tokens": 10,
        "temperature": 0.1,
        "stream": False
    }
    res = requests.post(url, headers=headers, json=payload, timeout=10)
    print(f"Status: {res.status_code}")
    print(f"Response: {res.text[:200]}")
except Exception as e:
    print(f"Error: {e}")

# Test glm-5.1
print("\nTesting glm-5.1...")
try:
    from openai import OpenAI
    client = OpenAI(
        base_url="https://integrate.api.nvidia.com/v1",
        api_key="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"
    )
    completion = client.chat.completions.create(
        model="z-ai/glm-5.1",
        messages=[
            {"role": "system", "content": "Say 'Hello'"},
            {"role": "user", "content": "Say 'Hello'"}
        ],
        temperature=0.1,
        max_tokens=10,
        stream=False
    )
    print(f"Success: {completion.choices[0].message.content}")
except Exception as e:
    print(f"Error: {e}")
