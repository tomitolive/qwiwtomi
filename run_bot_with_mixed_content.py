#!/usr/bin/env python3
"""Run bot with mixed content (1 trending + 1 random high-rated per type)
- Skips already-processed content
- Submits new pages to Google Indexing API automatically
"""

from ai_engine import fetch_mixed_content
from mega_bot import fetch_details, create_page
from google_indexer import index_new_page
import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
SITE_URL = 'https://tomito.xyz'

print("Running bot with mixed content...")
print("=" * 50)

# Load existing index
all_index = []
if os.path.exists(INDEX_FILE):
    try:
        with open(INDEX_FILE, 'r', encoding='utf-8') as f:
            all_index = json.load(f)
        print(f"📚 Loaded {len(all_index)} existing items from index")
    except Exception as e:
        print(f"⚠️  Could not load index: {e}")

# Build set of existing IDs for fast lookup
existing_ids = set(str(item.get('tmdb_id', '')) for item in all_index)

def is_already_processed(tmdb_id):
    """Check if content already exists either in index or as a JSON file"""
    if str(tmdb_id) in existing_ids:
        return True
    content_file = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
    return os.path.exists(content_file)

# Fetch mixed content for movies (2 items)
print("\n🎬 Fetching mixed content for movies...")
movies = fetch_mixed_content('movie')
# Ensure we get exactly 2 movies by retrying if needed
max_attempts = 3
attempt = 0
while len(movies) < 2 and attempt < max_attempts:
    attempt += 1
    if attempt > 1:
        print(f"  🔄 Retry attempt {attempt} to get more movies...")
        more_movies = fetch_mixed_content('movie')
        # Add only new movies not already in the list
        existing_ids = {m['tmdb_id'] for m in movies}
        for m in more_movies:
            if m['tmdb_id'] not in existing_ids:
                movies.append(m)
                existing_ids.add(m['tmdb_id'])
                if len(movies) >= 2:
                    break
movies = movies[:2]
print(f"✅ Movies fetched: {len(movies)} (required: 2)")

# Fetch mixed content for tv (3 items)
print("\n📺 Fetching mixed content for tv...")
tv_shows = fetch_mixed_content('tv')
# Ensure we get exactly 3 TV shows by retrying if needed
attempt = 0
while len(tv_shows) < 3 and attempt < max_attempts:
    attempt += 1
    if attempt > 1:
        print(f"  🔄 Retry attempt {attempt} to get more TV shows...")
        more_tv = fetch_mixed_content('tv')
        # Add only new TV shows not already in the list
        existing_ids = {t['tmdb_id'] for t in tv_shows}
        for t in more_tv:
            if t['tmdb_id'] not in existing_ids:
                tv_shows.append(t)
                existing_ids.add(t['tmdb_id'])
                if len(tv_shows) >= 3:
                    break
tv_shows = tv_shows[:3]
print(f"✅ TV shows fetched: {len(tv_shows)} (required: 3)")

# Create pages for movies
print("\n📄 Creating pages for movies...")
for item in movies:
    tmdb_id = item.get('tmdb_id')
    if is_already_processed(tmdb_id):
        print(f"  ⏭️  Skipping movie (already exists): {item.get('title')} (ID: {tmdb_id})")
        continue
    print(f"  Processing movie: {item.get('title')} (ID: {tmdb_id})")
    try:
        details = fetch_details(tmdb_id, 'movie')
        if details:
            page_path, entry = create_page(details, 'movie', is_trend=True)
            if entry:
                all_index.append(entry)
                existing_ids.add(str(tmdb_id))
                # Submit new page to Google Indexing API
                slug = entry.get('slug', f"{tmdb_id}")
                page_url = f"{SITE_URL}/movie/{slug}"
                print(f"  📡 Submitting to Google Index: {page_url}")
                index_new_page(page_url)
            print(f"  ✅ Created: {page_path}")
        else:
            print(f"  ❌ Failed to fetch details")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Create pages for tv shows
print("\n📄 Creating pages for tv shows...")
for item in tv_shows:
    tmdb_id = item.get('tmdb_id')
    if is_already_processed(tmdb_id):
        print(f"  ⏭️  Skipping tv (already exists): {item.get('title')} (ID: {tmdb_id})")
        continue
    print(f"  Processing tv: {item.get('title')} (ID: {tmdb_id})")
    try:
        details = fetch_details(tmdb_id, 'tv')
        if details:
            page_path, entry = create_page(details, 'tv', is_trend=True)
            if entry:
                all_index.append(entry)
                existing_ids.add(str(tmdb_id))
                # Submit new page to Google Indexing API
                slug = entry.get('slug', f"{tmdb_id}")
                page_url = f"{SITE_URL}/tv/{slug}"
                print(f"  📡 Submitting to Google Index: {page_url}")
                index_new_page(page_url)
            print(f"  ✅ Created: {page_path}")
        else:
            print(f"  ❌ Failed to fetch details")
    except Exception as e:
        print(f"  ❌ Error: {e}")

# Deduplicate index before saving
seen = set()
unique_index = []
for item in all_index:
    tid = str(item.get('tmdb_id', ''))
    if tid not in seen:
        seen.add(tid)
        unique_index.append(item)

# Save updated index
print("\n💾 Updating content_index.json...")
try:
    os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(unique_index, f, ensure_ascii=False, indent=2)
    print(f"✅ Index updated with {len(unique_index)} total items")
except Exception as e:
    print(f"❌ Failed to save index: {e}")

# Generate Sitemaps
print("\n🗺️ Generating HTML-independent Sitemaps...")
try:
    import generate_full_sitemap
    generate_full_sitemap.generate_sitemaps()
except Exception as e:
    print(f"❌ Failed to generate sitemaps: {e}")

print("\n" + "=" * 50)
print("✅ Bot run complete!")
