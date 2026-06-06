#!/usr/bin/env python3
"""Test NVIDIA API directly"""

from openai import OpenAI
import time

API_KEY = "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"

print("Testing NVIDIA API...")
print("=" * 50)

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=API_KEY
)

start_time = time.time()

try:
    completion = client.chat.completions.create(
        model="z-ai/glm-5.1",
        messages=[
            {"role": "system", "content": "You are a JSON generator. Return ONLY valid JSON object."},
            {"role": "user", "content": "Generate a simple JSON: {\"test\": \"hello\"}"}
        ],
        temperature=0.3,
        max_tokens=100,
        stream=False,
        timeout=30
    )
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    if completion and len(completion.choices) > 0:
        text = completion.choices[0].message.content
        print(f"✅ SUCCESS in {elapsed:.2f} seconds")
        print(f"Response: {text}")
    else:
        print("❌ No response")
        
except Exception as e:
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"❌ ERROR after {elapsed:.2f} seconds: {e}")

print("=" * 50)
