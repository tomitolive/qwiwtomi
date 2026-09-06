#!/usr/bin/env python3
"""
trending_bot.py
---------------
بوت جلب المحتوى التريند من TMDB وإنشاء صفحات جديدة.
- يجلب التريند اليومي (movies + tv) من TMDB
- يتحقق من وجود كل صفحة في data/content/
- ينشئ صفحات جديدة فقط لل הפריטات اللي ماشي موجودة
- يحدّث content_index.json
- يعيد بناء الصفحة الرئيسية + listing + search index + sitemap
"""

import os
import sys
import json
import logging
import time
import subprocess
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
BATCH_SIZE = 35

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

from mega_bot import get_tmdb_data, fetch_details, create_page, submit_to_bing_indexnow, build_listing_pages
from google_indexer import index_new_page
from googletrans import Translator
import generate_search_index

try:
    import build_homepage
except ImportError:
    build_homepage = None


def load_content_index():
    """تحميل الفهرس + استخراج IDs الموجودة."""
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            seen = set()
            for item in data:
                tid = str(item.get('tmdb_id', ''))
                m_type = item.get('folder', 'movie')
                if tid:
                    seen.add(f"{m_type}-{tid}")
            return data, seen
        except Exception:
            pass
    return [], set()


def check_page_exists(tmdb_id):
    """التحقق من وجود الصفحة في data/content/."""
    json_path = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
    return os.path.exists(json_path)


def translate_to_arabic(text):
    """ترجمة نص من الإنجليزية للعربية."""
    try:
        translator = Translator()
        result = translator.translate(text, src='en', dest='ar')
        return result.text
    except:
        return text
def fetch_trending(media_type, min_popularity=40, min_rating=7.0, min_votes=2):
    """جلب التريند اليومي من TMDB مع فلترة."""
    log.info(f"🔥 Fetching trending {media_type}...")
    data = get_tmdb_data(f'trending/{media_type}/day', {'language': 'ar-SA'})
    if not data or 'results' not in data:
        log.warning(f"   No trending data returned for {media_type}")
        return []

    results = []
    for item in data['results']:
        tid = item.get('id')
        pop = item.get('popularity', 0)
        rating = item.get('vote_average', 0)
        votes = item.get('vote_count', 0)
        title = item.get('title') or item.get('name') or 'Unknown'

        if not tid:
            continue
        if pop < min_popularity:
            continue
        if rating < min_rating or votes < min_votes:
            continue

        results.append({
            'tmdb_id': str(tid),
            'media_type': media_type,
            'title': title,
            'popularity': pop,
            'rating': rating,
            'votes': votes
        })

    for item in results:
        item['title_ar'] = translate_to_arabic(item['title'])
    log.info(f"   Found {len(results)} trending {media_type} items (filtered)")
    return results


def main():
    log.info("🚀 Starting Trending Bot...")
    log.info("=" * 60)

    all_index, seen_ids = load_content_index()
    log.info(f"📊 Existing pages: {len(all_index)}")

    trending_movies = fetch_trending('movie')
    trending_tv = fetch_trending('tv')
    all_trending = trending_movies + trending_tv

    new_items = []
    for item in all_trending:
        unique_key = f"{item['media_type']}-{item['tmdb_id']}"
        if unique_key in seen_ids:
            log.debug(f"   Skipping {item['title']} (already exists)")
            continue
        if check_page_exists(item['tmdb_id']):
            log.debug(f"   Skipping {item['title']} (file exists)")
            seen_ids.add(unique_key)
            continue
        new_items.append(item)

    if not new_items:
        log.info("✅ All trending items already have pages!")
        log.info("=" * 60)
        return

    log.info(f"🆕 New trending items to create: {len(new_items)}")
    batch = new_items[:BATCH_SIZE]
    log.info(f"📋 Processing batch of {len(batch)} pages")

    created = 0
    for i, item in enumerate(batch):
        tmdb_id = item['tmdb_id']
        media_type = item['media_type']
        title = item.get('title_ar') or item['title']

        log.info(f"[{i+1}/{len(batch)}] 📥 {media_type.upper()} ID: {tmdb_id} - {title}")

        try:
            details = fetch_details(tmdb_id, media_type, bypass_adult_check=True)
            if not details:
                log.warning(f"   ❌ TMDB fetch failed — skipping")
                continue

            page_path, entry = create_page(details, media_type, is_trend=True, force=True, skip_images=True)

            if entry:
                all_index.append(entry)
                created += 1
                seen_ids.add(f"{media_type}-{tmdb_id}")
                log.info(f"   ✅ Created: {page_path}")

                try:
                    full_url = f"https://tomit.click/{page_path}"
                    submit_to_bing_indexnow(full_url)
                    google_status = index_new_page(full_url)
                    log.info(f"   📡 Google: {google_status}")
                except Exception as e:
                    log.warning(f"   ⚠️ Indexing failed: {e}")
            else:
                log.warning(f"   ❌ AI generation failed for {title}")

        except Exception as e:
            log.error(f"   ❌ Error processing {title}: {e}")

        time.sleep(2)

    log.info("=" * 60)
    log.info(f"📈 Statistics:")
    log.info(f"   ✅ Created: {created}/{len(batch)}")
    log.info(f"   📊 Total pages: {len(all_index)}")

    if created > 0:
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_index, f, ensure_ascii=False, indent=2)
        log.info(f"💾 content_index.json updated ({len(all_index)} entries)")

        try:
            if build_homepage:
                build_homepage.build()
                if hasattr(build_homepage, 'build_all_pages'):
                    build_homepage.build_all_pages()
            build_listing_pages()
            log.info("🏗️  Homepage and listing pages rebuilt.")
        except Exception as e:
            log.warning(f"Rebuild warning: {e}")

        try:
            generate_search_index.generate()
            log.info("🔍 Search index updated.")
        except Exception as e:
            log.warning(f"Search index warning: {e}")

        try:
            from generate_full_sitemap import generate_sitemaps
            generate_sitemaps()
            log.info("🗺️  Sitemaps regenerated.")
        except Exception as e:
            log.warning(f"Sitemap warning: {e}")

        git_sync = os.path.join(BASE_PATH, 'git_sync.sh')
        if os.path.exists(git_sync):
            try:
                subprocess.run(['bash', git_sync], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    log.info("\n" + "=" * 60)
    log.info("✅ Trending Bot run complete!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
