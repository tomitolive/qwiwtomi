#!/usr/bin/env python3
"""
fix_short_descriptions_bot.py
------------------------------
بوت إصلاح الأوصاف والحقول الناقصة.
- يفحص جميع ملفات JSON في data/content/
- يحدد الصفحات ذات meta_desc خارج النطاق 150-160 حرف
- يحدد الصفحات التي تنقصها حقول مطلوبة
- يعالج دفعة محددة كل تشغيل (BATCH_SIZE)
- يعيد توليد الصفحة باستخدام AI مع الحقول الموحدة
- يتتبع الصفحات المعالجة لتجنب التكرار
- يستخدم البيانات المحلية كـ fallback عند فشل TMDB API
"""

import os
import json
import logging
import time
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
PROCESSED_FILE = os.path.join(BASE_PATH, 'data', 'fixed_pages.json')
PAGES_TO_FIX_FILE = os.path.join(BASE_PATH, 'data', 'pages_to_fix.json')
PRIORITY_PAGES_FILE = os.path.join(BASE_PATH, 'data', 'priority_pages.json')
BATCH_SIZE = 25

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Import project modules
import mega_bot

REQUIRED_FIELDS = ['desc_ar', 'desc_en', 'meta_desc', 'seo_title_ar', 'opinion_ar', 'opinion_en', 'faq', 'keywords', 'intro', 'outro']


def load_fixed_pages():
    """تحميل قائمة الصفحات التي تم إصلاحها."""
    if not os.path.exists(PROCESSED_FILE):
        return []
    try:
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('fixed_pages', [])
    except Exception as e:
        log.warning(f"Could not load fixed pages: {e}")
        return []


def save_fixed_pages(fixed_pages):
    """حفظ قائمة الصفحات التي تم إصلاحها."""
    try:
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'fixed_pages': fixed_pages,
                'last_updated': datetime.now().isoformat(),
                'total_fixed': len(fixed_pages)
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Could not save fixed pages: {e}")


def load_priority_pages():
    """تحميل قائمة الصفحات ذات الأولوية."""
    if not os.path.exists(PRIORITY_PAGES_FILE):
        return []
    try:
        with open(PRIORITY_PAGES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('priority_pages', [])
    except Exception as e:
        log.warning(f"Could not load priority pages: {e}")
        return []


def build_details_from_local(tmdb_id, media_type):
    """بناء dict details من البيانات المحلية عند فشل TMDB API."""
    json_path = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
    if not os.path.exists(json_path):
        return None
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return None
    
    # Build a minimal TMDB-like response from local data
    title_ar = data.get('title_ar', '')
    title_en = data.get('title_en', '')
    overview = data.get('overview', '')
    
    ar_data = {
        'id': int(tmdb_id),
        'title': title_ar if media_type == 'movie' else None,
        'name': title_ar if media_type != 'movie' else None,
        'overview': overview,
        'poster_path': data.get('poster_path', ''),
        'backdrop_path': data.get('backdrop_path', ''),
        'release_date': data.get('release_date', ''),
        'first_air_date': data.get('first_air_date', data.get('release_date', '')),
        'vote_average': data.get('vote_average', 7.0),
        'vote_count': data.get('vote_count', 10),
        'genres': data.get('genres', []),
    }
    
    en_data = dict(ar_data)
    en_data['title'] = title_en if media_type == 'movie' else None
    en_data['name'] = title_en if media_type != 'movie' else None
    en_overview = data.get('ai_content', {}).get('desc_en', '')
    if en_overview:
        en_data['overview'] = en_overview
    
    # Build credits from local data if available
    credits = {'cast': [], 'crew': []}
    if data.get('cast'):
        credits['cast'] = data['cast'] if isinstance(data['cast'], list) else []
    if data.get('director'):
        credits['crew'] = [{'name': data['director'], 'job': 'Director'}]
    
    log.info(f"   📂 Using local data fallback for ID {tmdb_id}")
    return {'ar': ar_data, 'en': en_data, 'credits': credits, 'similar': {'results': []}}


def find_pages_to_fix():
    """البحث عن الصفحات ذات الأوصاف القصيرة/الطويلة أو الحقول الناقصة."""
    # Use pre-generated pages_to_fix.json if available
    if os.path.exists(PAGES_TO_FIX_FILE):
        try:
            with open(PAGES_TO_FIX_FILE, 'r', encoding='utf-8') as f:
                pages = json.load(f)
            log.info(f"📂 Loaded {len(pages)} pages from pages_to_fix.json")
            return pages
        except Exception as e:
            log.warning(f"Could not load pages_to_fix.json: {e}")

    # Fallback: scan all files
    pages_to_fix = []

    if not os.path.exists(CONTENT_DIR):
        log.error(f"Content directory not found: {CONTENT_DIR}")
        return pages_to_fix

    json_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('.json')]
    log.info(f"📂 Found {len(json_files)} JSON files in content directory")

    for json_file in json_files:
        file_path = os.path.join(CONTENT_DIR, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            ai_content = data.get('ai_content', {})
            meta_desc = ai_content.get('meta_desc', '')
            missing_fields = [fld for fld in REQUIRED_FIELDS if fld not in ai_content]

            needs_fix = bool(missing_fields)
            if meta_desc and (len(meta_desc) < 150 or len(meta_desc) > 160):
                needs_fix = True

            if needs_fix:
                tmdb_id = data.get('tmdb_id') or data.get('id')
                media_type = data.get('type') or data.get('media_type', 'movie')
                title = data.get('title_ar') or data.get('title', '')

                if not tmdb_id or tmdb_id == 'None':
                    log.debug(f"Skipping {json_file} - invalid tmdb_id: {tmdb_id}")
                    continue

                pages_to_fix.append({
                    'tmdb_id': tmdb_id,
                    'media_type': media_type,
                    'title': title,
                    'file': json_file,
                    'current_length': len(meta_desc) if meta_desc else 0,
                    'current_desc': meta_desc,
                    'missing_fields': missing_fields
                })

        except Exception as e:
            log.warning(f"Error reading {json_file}: {e}")

    log.info(f"🔍 Found {len(pages_to_fix)} pages needing fixes (short/long meta_desc or missing fields)")
    return pages_to_fix


def process_batch(pages_to_fix, fixed_pages):
    """معالجة دفعة من الصفحات."""
    fixed_ids = {str(p['tmdb_id']) for p in fixed_pages}
    available_pages = [p for p in pages_to_fix if str(p['tmdb_id']) not in fixed_ids]

    if not available_pages:
        log.info("✅ All pages have been fixed!")
        return 0, fixed_pages

    # ترتيب الصفحات: الأولوية أولاً
    priority_pages = load_priority_pages()
    priority_ids = {str(p['tmdb_id']) for p in priority_pages}
    priority_available = [p for p in available_pages if str(p['tmdb_id']) in priority_ids]
    regular_available = [p for p in available_pages if str(p['tmdb_id']) not in priority_ids]

    if priority_available:
        log.info(f"⭐ Found {len(priority_available)} priority pages to process first")

    available_pages = priority_available + regular_available
    batch = available_pages[:BATCH_SIZE]
    log.info(f"📋 Processing {len(batch)} pages (batch size: {BATCH_SIZE})")

    success = 0
    for i, page in enumerate(batch):
        tmdb_id = str(page['tmdb_id'])
        media_type = page['media_type']
        title = page['title']
        json_file = page['file']
        missing = page.get('missing_fields', [])

        reason = []
        if page['current_length'] and (page['current_length'] < 150 or page['current_length'] > 160):
            reason.append(f"meta_desc length={page['current_length']}")
        if missing:
            reason.append(f"missing fields={missing}")

        log.info(f"[{i+1}/{len(batch)}] Fixing: {title} (ID: {tmdb_id}) | {', '.join(reason)}")

        try:
            # Try TMDB first, fall back to local data
            details = mega_bot.fetch_details(tmdb_id, media_type, bypass_adult_check=True)
            if not details:
                details = build_details_from_local(tmdb_id, media_type)
            if not details:
                log.warning(f"   ⚠️ No TMDB data and no local data for {tmdb_id} — skipping")
                # Mark as fixed so we don't retry forever
                fixed_pages.append({
                    'tmdb_id': tmdb_id,
                    'file': json_file,
                    'title': title,
                    'fixed_at': datetime.now().isoformat(),
                    'status': 'skipped_no_data'
                })
                continue

            page_path, entry = mega_bot.create_page(details, media_type, is_trend=True, force=True, skip_images=True)

            if entry:
                success += 1
                fixed_pages.append({
                    'tmdb_id': tmdb_id,
                    'file': json_file,
                    'title': title,
                    'fixed_at': datetime.now().isoformat()
                })
                log.info(f"   ✅ Fixed: {page_path}")

                # التحقق من النتيجة
                try:
                    json_path = os.path.join(CONTENT_DIR, json_file)
                    with open(json_path, 'r', encoding='utf-8') as f:
                        new_data = json.load(f)
                    new_ai = new_data.get('ai_content', {})
                    new_meta_desc = new_ai.get('meta_desc', '')
                    new_length = len(new_meta_desc) if new_meta_desc else 0
                    log.info(f"   📏 New meta_desc length: {new_length} chars")

                    still_missing = [fld for fld in REQUIRED_FIELDS if fld not in new_ai]
                    if still_missing:
                        log.warning(f"   ⚠️ Still missing fields: {still_missing}")
                    else:
                        log.info(f"   ✅ All required fields present")
                except Exception as e:
                    log.warning(f"   ⚠️ Could not verify fixed page: {e}")
            else:
                log.warning(f"   ❌ AI generation failed for {title}")

        except Exception as e:
            log.error(f"   ❌ Error processing {title}: {e}")

        time.sleep(2)

    return success, fixed_pages


def main():
    log.info("🚀 Starting Fix Descriptions & Missing Fields Bot...")
    log.info("=" * 60)

    fixed_pages = load_fixed_pages()
    log.info(f"📊 Already fixed: {len(fixed_pages)} pages")

    pages_to_fix = find_pages_to_fix()

    if pages_to_fix:
        fixed_count, fixed_pages = process_batch(pages_to_fix, fixed_pages)
        save_fixed_pages(fixed_pages)

        fixed_ids = {str(p['tmdb_id']) for p in fixed_pages}
        remaining = len([p for p in pages_to_fix if str(p['tmdb_id']) not in fixed_ids])
        log.info("=" * 60)
        log.info(f"📈 Fix Statistics:")
        log.info(f"   ✅ Fixed in this run: {fixed_count}")
        log.info(f"   📊 Total fixed: {len(fixed_pages)}")
        log.info(f"   ⏳ Remaining to fix: {remaining}")
    else:
        log.info("✅ All pages are complete and compliant!")

    log.info("\n" + "=" * 60)
    log.info("✅ Bot run complete!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
