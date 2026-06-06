#!/usr/bin/env python3
"""Regenerate AI content for a specific file"""

import json
import os
from ai_engine import generate_bilingual_description

# Load the file
file_path = 'data/content/64197.json'
with open(file_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract data for AI generation
title_ar = data.get('title_ar', data.get('title', ''))
title_en = data.get('title_en', data.get('title', ''))
overview_ar = data.get('overview', '')
overview_en = data.get('overview', '')  # Using same overview for both since we don't have separate
year = data.get('release_date', '2015')[:4]
genres_ar = [g.get('name', '') for g in data.get('genres', [])]
media_type = 'tv'  # Based on the file structure

print(f"Regenerating AI content for: {title_en}")
print(f"Arabic overview: {overview_ar}")
print(f"English overview: {overview_en}")

# Generate new AI content
ai_content = generate_bilingual_description(
    title_ar=title_ar,
    title_en=title_en,
    overview_ar=overview_ar,
    overview_en="Weakened by illness but strong in mind, Mei Changsu enters court politics to seek justice for a tragedy long forgotten.",
    year=year,
    genres_ar=genres_ar,
    media_type=media_type
)

# Update the data
data['ai_content'] = ai_content

# Save back
with open(file_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"✅ AI content regenerated and saved to {file_path}")
print(f"New desc_ar: {ai_content.get('desc_ar', '')[:100]}...")
print(f"New desc_en: {ai_content.get('desc_en', '')[:100]}...")
