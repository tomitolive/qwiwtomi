#!/usr/bin/env python3
"""
migrate_to_supabase.py
----------------------
Migration script: Copies data from JSON files to Supabase.
Does NOT delete any JSON files - safe to run.

Usage:
  python migrate_to_supabase.py

Requirements:
  pip install supabase
"""

import os
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
GENRE_DIR = os.path.join(BASE_PATH, 'data', 'genre')
CAROUSEL_FILE = os.path.join(BASE_PATH, 'data', 'carousel_data.json')

# Supabase config
SUPABASE_URL = "https://apsfzuzvtglhhhnakjnt.supabase.co"
SUPABASE_KEY = "sb_publishable_-f_OPA_jcwhY1RZi1PnoUg_WO2RmuG1"

from supabase import create_client, Client

def get_supabase() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def normalize_poster_path(poster_path: str) -> str:
    """Normalize poster_path to format: /xxxxx.jpg"""
    if not poster_path:
        return ""
    if poster_path.startswith("/t/p/w500"):
        # Remove prefix: /t/p/w500/xTI42...jpg → /xTI42...jpg
        return poster_path.replace("/t/p/w500", "")
    if poster_path.startswith("http"):
        # Full URL: https://image.tmdb.org/t/p/w500/xxx.jpg → /xxx.jpg
        return poster_path.replace("https://image.tmdb.org/t/p/w500", "")
    if poster_path.startswith("/t/p/"):
        # Other size: /t/p/original/xxx.jpg → /xxx.jpg
        parts = poster_path.split("/")
        return "/" + "/".join(parts[3:]) if len(parts) > 3 else poster_path
    # Already just /xxx.jpg
    return poster_path


def migrate_content(sb: Client):
    """Migrate content_index.json + content/*.json to Supabase."""
    log.info("📁 Loading content_index.json...")
    
    if not os.path.exists(INDEX_FILE):
        log.error(f"❌ {INDEX_FILE} not found!")
        return
    
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    log.info(f"📊 Found {len(index_data)} entries in content_index.json")
    
    # Build lookup from index
    index_by_tmdb = {}
    for item in index_data:
        tid = item.get('tmdb_id')
        if tid:
            index_by_tmdb[str(tid)] = item
    
    # Collect all content files
    content_files = []
    if os.path.exists(CONTENT_DIR):
        for filename in os.listdir(CONTENT_DIR):
            if filename.endswith('.json'):
                content_files.append(filename)
    
    log.info(f"📁 Found {len(content_files)} content files")
    
    # Merge index + content files
    all_content = {}
    
    # First: from index (lightweight data)
    for item in index_data:
        tid = str(item.get('tmdb_id', ''))
        if not tid:
            continue
        
        # Convert index entry to Supabase format
        record = {
            "tmdb_id": int(tid),
            "slug": item.get("slug", ""),
            "title": item.get("title", ""),
            "title_ar": item.get("title_ar", ""),
            "title_en": item.get("title_en", ""),
            "type": item.get("type", "movie"),
            "folder": item.get("folder", "movie"),
            "poster": item.get("poster", ""),
            "poster_path": normalize_poster_path(item.get("poster", "")),
            "vote_average": item.get("rating"),
            "year": item.get("year"),
            "genres": item.get("genres", []),
            "genre_ids": item.get("genre_ids", []),
            "timestamp": item.get("timestamp"),
            "fixed": item.get("fixed", False),
        }
        all_content[tid] = record
    
    # Second: from content files (full data - overwrites index data)
    loaded = 0
    skipped = 0
    for filename in content_files:
        tmdb_id_str = filename.replace('.json', '')
        filepath = os.path.join(CONTENT_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tid = str(data.get('id', tmdb_id_str))
            if not tid:
                skipped += 1
                continue
            
            # Determine folder
            folder = data.get('folder', 'movie')
            if folder not in ('movie', 'tv'):
                folder = data.get('media_type', 'movie')
            
            # Normalize genres to list of objects
            raw_genres = data.get('genres', [])
            if raw_genres and isinstance(raw_genres[0], dict):
                genres = raw_genres
            elif raw_genres and isinstance(raw_genres[0], str):
                # Convert from index format (strings) to content format (objects)
                genres = [{"id": i, "name": g} for i, g in enumerate(raw_genres)]
            else:
                genres = []
            
            # Build poster fields
            poster_path_raw = data.get('poster_path', '')
            poster_path = normalize_poster_path(poster_path_raw)
            poster_full = f"/t/p/w500{poster_path}" if poster_path else ""
            
            record = {
                "tmdb_id": int(tid),
                "slug": data.get("slug", f"{tid}"),
                "title": data.get("title", ""),
                "title_ar": data.get("title_ar", ""),
                "title_en": data.get("title_en", ""),
                "type": data.get("type", folder),
                "folder": folder,
                "poster": poster_full,
                "poster_path": poster_path,
                "backdrop_path": data.get("backdrop_path", ""),
                "release_date": data.get("release_date", ""),
                "first_air_date": data.get("first_air_date", ""),
                "vote_average": data.get("vote_average"),
                "vote_count": data.get("vote_count"),
                "genres": genres,
                "genre_ids": [g.get("id") for g in genres if g.get("id")] if genres and isinstance(genres[0], dict) else data.get("genre_ids", []),
                "ai_content": data.get("ai_content", {}),
                "overview": data.get("overview", ""),
                "overview_en": data.get("overview_en", ""),
                "section": data.get("section", ""),
                "quality": data.get("quality", ""),
                "duration": data.get("duration", ""),
                "language": data.get("language", ""),
                "country": data.get("country", ""),
                "cast_members": data.get("cast", ""),
                "imdb_id": data.get("imdb_id", ""),
                "status": data.get("status", ""),
                "number_of_seasons": data.get("number_of_seasons"),
                "seasons": data.get("seasons", []),
                "number_of_episodes": data.get("number_of_episodes"),
                "timestamp": all_content.get(tid, {}).get("timestamp") or int(time.time()),
                "fixed": data.get("fixed", False),
                "name": data.get("name", ""),
                "media_type": data.get("media_type", folder),
            }
            
            all_content[tid] = record
            loaded += 1
            
        except Exception as e:
            log.warning(f"⚠️ Error reading {filename}: {e}")
            skipped += 1
    
    log.info(f"📊 Prepared {len(all_content)} records ({loaded} from files, {skipped} skipped)")
    
    # Batch upsert to Supabase
    records = list(all_content.values())
    batch_size = 100
    total = len(records)
    upserted = 0
    
    log.info(f"🚀 Starting upsert to Supabase ({total} records)...")
    
    for i in range(0, total, batch_size):
        batch = records[i:i + batch_size]
        try:
            sb.table("content").upsert(batch).execute()
            upserted += len(batch)
            log.info(f"   ✅ Upserted {upserted}/{total}")
        except Exception as e:
            log.error(f"   ❌ Batch {i//batch_size + 1} failed: {e}")
            # Try one by one for this batch
            for record in batch:
                try:
                    sb.table("content").upsert(record).execute()
                    upserted += 1
                except Exception as e2:
                    log.error(f"      ❌ Failed tmdb_id={record['tmdb_id']}: {e2}")
        
        time.sleep(0.1)  # Rate limit
    
    log.info(f"✅ Content migration complete: {upserted}/{total} records")


def migrate_genres(sb: Client):
    """Migrate genre/*.json to Supabase."""
    log.info("📁 Loading genre files...")
    
    if not os.path.exists(GENRE_DIR):
        log.warning("⚠️ Genre directory not found")
        return
    
    records = []
    for filename in os.listdir(GENRE_DIR):
        if not filename.endswith('.json'):
            continue
        
        slug = filename.replace('.json', '')
        filepath = os.path.join(GENRE_DIR, filename)
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            record = {
                "slug": slug,
                "name": data.get("name", ""),
                "name_ar": data.get("name_ar", ""),
                "description": data.get("description", ""),
                "items": data.get("items", []),
            }
            records.append(record)
        except Exception as e:
            log.warning(f"⚠️ Error reading {filename}: {e}")
    
    log.info(f"📊 Found {len(records)} genre records")
    
    # Upsert
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            sb.table("genres").upsert(batch).execute()
            log.info(f"   ✅ Upserted genres batch {i//batch_size + 1}")
        except Exception as e:
            log.error(f"   ❌ Genre batch failed: {e}")
    
    log.info(f"✅ Genre migration complete: {len(records)} records")


def migrate_carousel(sb: Client):
    """Migrate carousel_data.json to Supabase."""
    log.info("📁 Loading carousel_data.json...")
    
    if not os.path.exists(CAROUSEL_FILE):
        log.warning("⚠️ carousel_data.json not found")
        return
    
    with open(CAROUSEL_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if not data:
        log.warning("⚠️ carousel_data.json is empty")
        return
    
    records = []
    for item in data:
        poster_path = item.get("poster_path", "")
        record = {
            "tmdb_id": item.get("tmdb_id"),
            "title": item.get("title", ""),
            "title_en": item.get("title_en", ""),
            "overview": item.get("overview", ""),
            "overview_en": item.get("overview_en", ""),
            "poster_path": poster_path,
            "backdrop_path": item.get("backdrop_path", ""),
            "release_date": item.get("release_date", ""),
            "vote_average": item.get("vote_average"),
            "genre_ids": item.get("genre_ids", []),
            "genres": item.get("genres", []),
            "youtube_key": item.get("youtube_key", ""),
            "youtube_url": item.get("youtube_url", ""),
            "local_video_path": item.get("local_video_path", ""),
            "age_rating": item.get("age_rating", ""),
            "folder": item.get("folder", "movie"),
        }
        records.append(record)
    
    log.info(f"📊 Found {len(records)} carousel records")
    
    # Delete existing and insert new
    try:
        sb.table("carousel").delete().neq("id", 0).execute()
        sb.table("carousel").insert(records).execute()
        log.info(f"✅ Carousel migration complete: {len(records)} records")
    except Exception as e:
        log.error(f"❌ Carousel migration failed: {e}")


def main():
    log.info("🚀 Starting Supabase Migration...")
    log.info("=" * 60)
    
    sb = get_supabase()
    
    # Test connection
    try:
        result = sb.table("content").select("tmdb_id").limit(1).execute()
        log.info("✅ Connected to Supabase successfully")
    except Exception as e:
        log.error(f"❌ Cannot connect to Supabase: {e}")
        log.error("   Make sure you've run the SQL migration first!")
        return
    
    migrate_content(sb)
    migrate_genres(sb)
    migrate_carousel(sb)
    
    log.info("\n" + "=" * 60)
    log.info("✅ Migration complete! JSON files are NOT deleted.")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
