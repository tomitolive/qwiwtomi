#!/usr/bin/env python3
"""Test the new trending functions in ai_engine.py"""

from ai_engine import fetch_mixed_content, fetch_trending, fetch_random_high_rated
import json

print("Testing ai_engine.py trending functions...")
print("=" * 50)

# Test fetch_mixed_content for movies
print("\n🎬 Testing fetch_mixed_content for movies...")
movies = fetch_mixed_content('movie')
print(f"Movies fetched: {len(movies)}")
print(json.dumps(movies, indent=2, ensure_ascii=False))

# Test fetch_mixed_content for tv
print("\n📺 Testing fetch_mixed_content for tv...")
tv_shows = fetch_mixed_content('tv')
print(f"TV shows fetched: {len(tv_shows)}")
print(json.dumps(tv_shows, indent=2, ensure_ascii=False))

print("\n" + "=" * 50)
print("✅ Test complete!")
