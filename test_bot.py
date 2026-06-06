#!/usr/bin/env python3
"""Test script for ai_engine on page 454639 only"""

import json
from ai_engine import generate_bilingual_description

# Load page 454639
with open("data/content/454639.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Extract data
title_ar = data.get("title_ar", "")
title_en = data.get("title_en", "")
overview_ar = data.get("overview", "")
overview_en = data.get("overview", "")
year = data.get("release_date", "2026")[:4]
genres_ar = [g["name"] for g in data.get("genres", [])]
media_type = "movie"  # Based on the data

print(f"Testing on: {title_ar} ({year})")
print(f"Genres: {', '.join(genres_ar)}")
print("-" * 50)

# Generate AI content
ai_content = generate_bilingual_description(
    title_ar=title_ar,
    title_en=title_en,
    overview_ar=overview_ar,
    overview_en=overview_en,
    year=year,
    genres_ar=genres_ar,
    media_type=media_type
)

print("\nGenerated AI Content:")
print(json.dumps(ai_content, indent=2, ensure_ascii=False))

# Verify 8 fields (including model_used)
print("\n" + "=" * 50)
print("Field Count Check:")
expected_fields = ["desc_ar", "desc_en", "meta_desc", "seo_title_ar", "opinion", "faq", "keywords", "model_used"]
actual_fields = list(ai_content.keys())
print(f"Expected: {len(expected_fields)} fields")
print(f"Actual: {len(actual_fields)} fields")
print(f"Fields: {actual_fields}")

if set(actual_fields) == set(expected_fields):
    print("✅ All 8 fields present!")
    print(f"Model Used: {ai_content.get('model_used', 'Unknown')}")
else:
    print("❌ Missing or extra fields!")
    missing = set(expected_fields) - set(actual_fields)
    extra = set(actual_fields) - set(expected_fields)
    if missing:
        print(f"Missing: {missing}")
    if extra:
        print(f"Extra: {extra}")
