#!/usr/bin/env python3
"""
fix_short_descriptions_bot.py
------------------------------
بوت شامل - إصلاح الأوصاف وتوليد صفحات جديدة.
- يفحص جميع ملفات JSON في data/content/
- يحدد الصفحات ذات meta_desc خارج النطاق 150-160 حرف
- يعالج جميع الصفحات أو دفعة محددة كل تشغيل
- يعيد توليد الوصف باستخدام AI مع الحقول الموحدة
- يتتبع الصفحات المعالجة لتجنب التكرار
- يعمل مع نفس الحقول مثل run_bot_with_mixed_content.py
- يولد صفحات جديدة (أفلام ومسلسلات من US مع تقييم >= 7.5)
"""

import os
import json
import logging
import time
import random
from datetime import datetime

# Import AI engine for new content generation
from ai_engine import fetch_mixed_content
from google_indexer import index_new_page

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
PROCESSED_FILE = os.path.join(BASE_PATH, 'data', 'fixed_pages.json')
PAGES_TO_FIX_FILE = os.path.join(BASE_PATH, 'data', 'pages_to_fix.json')
PRIORITY_PAGES_FILE = os.path.join(BASE_PATH, 'data', 'priority_pages.json')
BATCH_SIZE = 25
SITE_URL = 'https://tomito.xyz'

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Import project modules
import mega_bot

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

def find_short_descriptions():
    """البحث عن جميع الصفحات ذات الأوصاف القصيرة أو الطويلة - استخدام JSON المعد مسبقاً."""
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
    short_desc_pages = []
    
    if not os.path.exists(CONTENT_DIR):
        log.error(f"Content directory not found: {CONTENT_DIR}")
        return short_desc_pages
    
    # قراءة جميع ملفات JSON
    json_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('.json')]
    log.info(f"📂 Found {len(json_files)} JSON files in content directory")
    
    for json_file in json_files:
        file_path = os.path.join(CONTENT_DIR, json_file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # فحص ai_content.meta_desc
            ai_content = data.get('ai_content', {})
            meta_desc = ai_content.get('meta_desc', '')
            
            # Check if meta_desc is outside the 150-160 range
            if meta_desc and (len(meta_desc) < 150 or len(meta_desc) > 160):
                tmdb_id = data.get('tmdb_id') or data.get('id')
                media_type = data.get('type') or data.get('media_type', 'movie')
                title = data.get('title_ar') or data.get('title', '')
                
                # Skip if tmdb_id is missing or invalid
                if not tmdb_id or tmdb_id == 'None' or tmdb_id == None:
                    log.debug(f"Skipping {json_file} - invalid tmdb_id: {tmdb_id}")
                    continue
                
                short_desc_pages.append({
                    'tmdb_id': tmdb_id,
                    'media_type': media_type,
                    'title': title,
                    'file': json_file,
                    'current_length': len(meta_desc),
                    'current_desc': meta_desc
                })
                
        except Exception as e:
            log.warning(f"Error reading {json_file}: {e}")
    
    log.info(f"🔍 Found {len(short_desc_pages)} pages with descriptions outside 150-160 range")
    return short_desc_pages

def process_batch(short_pages, fixed_pages):
    """معالجة دفعة من الصفحات - مع الحقول الموحدة."""
    # استبعاد الصفحات التي تم معالجتها بالفعل
    fixed_ids = {str(p['tmdb_id']) for p in fixed_pages}
    available_pages = [p for p in short_pages if str(p['tmdb_id']) not in fixed_ids]
    
    if not available_pages:
        log.info("✅ All short descriptions have been fixed!")
        return 0, fixed_pages
    
    # تحميل الصفحات ذات الأولوية
    priority_pages = load_priority_pages()
    priority_ids = {str(p['tmdb_id']) for p in priority_pages}
    
    # ترتيب الصفحات: الأولوية أولاً ثم الباقي
    priority_available = [p for p in available_pages if str(p['tmdb_id']) in priority_ids]
    regular_available = [p for p in available_pages if str(p['tmdb_id']) not in priority_ids]
    
    if priority_available:
        log.info(f"⭐ Found {len(priority_available)} priority pages to process first")
    
    # دمج القوائم: الأولوية أولاً
    available_pages = priority_available + regular_available
    
    # اختيار دفعة من الصفحات (BATCH_SIZE)
    batch = available_pages[:BATCH_SIZE]
    log.info(f"📋 Processing {len(batch)} pages (batch size: {BATCH_SIZE})")
    
    success = 0
    for i, page in enumerate(batch):
        tmdb_id = str(page['tmdb_id'])
        media_type = page['media_type']
        title = page['title']
        json_file = page['file']
        
        log.info(f"[{i+1}/{len(batch)}] Fixing: {title} (ID: {tmdb_id}, current length: {page['current_length']})")
        
        try:
            # جلب بيانات TMDB
            details = mega_bot.fetch_details(tmdb_id, media_type)
            if not details:
                log.warning(f"   ⚠️ Could not fetch TMDB details for {tmdb_id}")
                continue
            
            # إعادة إنشاء الصفحة (سيتم توليد وصف جديد مع الحقول الموحدة)
            page_path, entry = mega_bot.create_page(details, media_type, is_trend=True, force=True)
            
            if entry:
                success += 1
                
                # إضافة إلى قائمة الصفحات المُصلحة
                fixed_pages.append({
                    'tmdb_id': tmdb_id,
                    'file': json_file,
                    'title': title,
                    'fixed_at': datetime.now().isoformat()
                })
                
                log.info(f"   ✅ Fixed: {page_path}")
                
                # التحقق من الطول الجديد والحقول الموحدة
                try:
                    json_path = os.path.join(CONTENT_DIR, json_file)
                    with open(json_path, 'r', encoding='utf-8') as f:
                        new_data = json.load(f)
                    new_meta_desc = new_data.get('ai_content', {}).get('meta_desc', '')
                    new_length = len(new_meta_desc) if new_meta_desc else 0
                    log.info(f"   📏 New meta_desc length: {new_length} chars")
                    
                    # التحقق من الحقول الموحدة
                    ai_content = new_data.get('ai_content', {})
                    required_fields = ['desc_ar', 'desc_en', 'meta_desc', 'seo_title_ar', 'opinion_ar', 'opinion_en', 'faq', 'keywords', 'intro', 'outro']
                    missing_fields = [f for f in required_fields if f not in ai_content]
                    if missing_fields:
                        log.warning(f"   ⚠️ Missing fields: {missing_fields}")
                    else:
                        log.info(f"   ✅ All required fields present")
                    
                    # إذا كان الطول الجديد بين 150-160، احذف الملف من القائمة
                    if 150 <= new_length <= 160:
                        log.info(f"   🗑️  Removing from short description list (length OK)")
                except Exception as e:
                    log.warning(f"   ⚠️ Could not verify fixed page: {e}")
            else:
                log.warning(f"   ❌ AI generation failed for {title}")
                
        except Exception as e:
            log.error(f"   ❌ Error processing {title}: {e}")
        
        # استراحة قصيرة بين الطلبات
        time.sleep(2)
    
    return success, fixed_pages

def is_already_processed(tmdb_id):
    """Check if content already exists either in index or as a JSON file"""
    # Load existing index
    all_index = []
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                all_index = json.load(f)
        except Exception as e:
            log.warning(f"Could not load index: {e}")
    
    # Build set of existing IDs for fast lookup
    existing_ids = set(str(item.get('tmdb_id', '')) for item in all_index)
    
    if str(tmdb_id) in existing_ids:
        return True
    content_file = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
    return os.path.exists(content_file)

def generate_new_content(media_type, count=2):
    """توليد صفحات جديدة من US مع تقييم >= 7.5"""
    log.info(f"\n🎬 Generating new {media_type} content (US region, rating >= 7.5)...")
    
    # Fetch mixed content
    items = fetch_mixed_content(media_type)
    
    if not items:
        log.warning(f"⚠️ No new {media_type} items found")
        return 0
    
    # Limit to requested count
    items = items[:count]
    log.info(f"📋 Processing {len(items)} new {media_type} items")
    
    success = 0
    for item in items:
        tmdb_id = item.get('tmdb_id')
        if is_already_processed(tmdb_id):
            log.info(f"  ⏭️  Skipping (already exists): {item.get('title')} (ID: {tmdb_id})")
            continue
        
        log.info(f"  Processing: {item.get('title')} (ID: {tmdb_id})")
        try:
            details = mega_bot.fetch_details(tmdb_id, media_type)
            if details:
                page_path, entry = mega_bot.create_page(details, media_type, is_trend=True)
                if entry:
                    success += 1
                    
                    # Validate meta_desc length
                    content_file = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
                    if os.path.exists(content_file):
                        with open(content_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        meta_desc = data.get('ai_content', {}).get('meta_desc', '')
                        if len(meta_desc) < 150 or len(meta_desc) > 160:
                            log.warning(f"  ⚠️ meta_desc length {len(meta_desc)} outside 150-160 range")
                            # Adjust meta_desc
                            if len(meta_desc) < 150:
                                padding = " استمتع بمشاهدة هذا العمل بجودة عالية وترجمة احترافية بدون إعلانات مزعجة."
                                meta_desc = meta_desc + padding[:150 - len(meta_desc)]
                            else:
                                meta_desc = meta_desc[:160]
                            data['ai_content']['meta_desc'] = meta_desc
                            with open(content_file, 'w', encoding='utf-8') as f:
                                json.dump(data, f, ensure_ascii=False, indent=2)
                            log.info(f"  ✅ Adjusted meta_desc to {len(meta_desc)} characters")
                    
                    # Submit new page to Google Indexing API
                    slug = entry.get('slug', f"{tmdb_id}")
                    page_url = f"{SITE_URL}/{media_type}/{slug}"
                    log.info(f"  📡 Submitting to Google Index: {page_url}")
                    index_new_page(page_url)
                    
                    log.info(f"  ✅ Created: {page_path}")
                else:
                    log.warning(f"  ❌ Failed to create page")
            else:
                log.warning(f"  ❌ Failed to fetch details")
        except Exception as e:
            log.error(f"  ❌ Error: {e}")
        
        time.sleep(2)
    
    return success

def update_index():
    """تحديث content_index.json بعد توليد صفحات جديدة"""
    log.info("\n💾 Updating content_index.json...")
    try:
        # Scan content directory for all JSON files
        all_index = []
        if os.path.exists(CONTENT_DIR):
            json_files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('.json')]
            for json_file in json_files:
                file_path = os.path.join(CONTENT_DIR, json_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    tmdb_id = data.get('tmdb_id') or data.get('id')
                    if tmdb_id:
                        # Extract poster path
                        poster_path = data.get('poster_path')
                        if poster_path:
                            if poster_path.startswith('/'):
                                poster = f"/t/p/w500{poster_path}"
                            elif poster_path.startswith('http'):
                                poster = poster_path.replace('https://image.tmdb.org/t/p/w500', '/t/p/w500')
                            else:
                                poster = f"/t/p/w500/{poster_path}"
                        else:
                            poster = ''
                        
                        # Extract genres
                        genres = []
                        genre_ids = []
                        if data.get('genres'):
                            for g in data['genres']:
                                if isinstance(g, dict):
                                    genres.append(g.get('name', ''))
                                    if g.get('id'):
                                        genre_ids.append(g['id'])
                        
                        # Determine folder/type
                        media_type = data.get('type') or data.get('media_type') or data.get('folder', 'movie')
                        folder = 'tv' if media_type == 'tv' else 'movie'
                        
                        # Extract year
                        year = data.get('year', '')
                        if not year:
                            release_date = data.get('release_date') or data.get('first_air_date', '')
                            year = release_date[:4] if release_date else ''
                        
                        # Extract rating
                        rating = data.get('vote_average', 0)
                        
                        # Extract titles
                        title_ar = data.get('title_ar') or data.get('title', '')
                        title_en = data.get('title_en', '')
                        title = f"{title_ar} / {title_en}" if title_en else title_ar
                        
                        all_index.append({
                            'tmdb_id': tmdb_id,
                            'slug': data.get('slug', f"{tmdb_id}"),
                            'title': title,
                            'title_ar': title_ar,
                            'title_en': title_en if title_en else None,
                            'type': folder,
                            'folder': folder,
                            'poster': poster,
                            'rating': rating,
                            'year': year,
                            'genres': genres if genres else None,
                            'genre_ids': genre_ids if genre_ids else None,
                            'timestamp': int(time.time())
                        })
                except Exception as e:
                    log.warning(f"Error reading {json_file}: {e}")
        
        # Deduplicate
        seen = set()
        unique_index = []
        for item in all_index:
            tid = str(item.get('tmdb_id', ''))
            if tid not in seen:
                seen.add(tid)
                unique_index.append(item)
        
        # Sort by timestamp (newest first)
        unique_index.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
        
        # Save
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(unique_index, f, ensure_ascii=False, indent=2)
        log.info(f"✅ Index updated with {len(unique_index)} total items")
    except Exception as e:
        log.error(f"❌ Failed to save index: {e}")

def generate_sitemaps():
    """توليد Sitemaps"""
    log.info("\n🗺️ Generating Sitemaps...")
    try:
        import generate_full_sitemap
        generate_full_sitemap.generate_sitemaps()
        log.info("✅ Sitemaps generated successfully")
    except Exception as e:
        log.error(f"❌ Failed to generate sitemaps: {e}")

def main():
    log.info("🚀 Starting Comprehensive Bot (Fix Descriptions + Generate New Content)...")
    log.info("=" * 60)
    
    # Part 1: Fix short descriptions
    log.info("\n📝 PART 1: Fixing Short Descriptions")
    log.info("-" * 60)
    
    # تحميل قائمة الصفحات التي تم إصلاحها
    fixed_pages = load_fixed_pages()
    log.info(f"📊 Already fixed: {len(fixed_pages)} pages")
    
    # البحث عن أوصاف قصيرة
    short_pages = find_short_descriptions()
    
    fixed_count = 0
    if short_pages:
        # معالجة دفعة
        fixed_count, fixed_pages = process_batch(short_pages, fixed_pages)
        
        # حفظ قائمة الصفحات المحدثة
        save_fixed_pages(fixed_pages)
        
        # الإحصائيات
        fixed_ids = {str(p['tmdb_id']) for p in fixed_pages}
        remaining = len([p for p in short_pages if str(p['tmdb_id']) not in fixed_ids])
        log.info("=" * 60)
        log.info(f"📈 Fix Statistics:")
        log.info(f"   ✅ Fixed in this run: {fixed_count}")
        log.info(f"   📊 Total fixed: {len(fixed_pages)}")
        log.info(f"   ⏳ Remaining to fix: {remaining}")
    else:
        log.info("✅ No short descriptions found. All pages are compliant!")
    
    # Part 2: Generate new content
    log.info("\n🎬 PART 2: Generating New Content")
    log.info("-" * 60)
    
    new_movies = generate_new_content('movie', count=2)
    new_tv = generate_new_content('tv', count=3)
    
    log.info("=" * 60)
    log.info(f"� New Content Statistics:")
    log.info(f"   ✅ New movies: {new_movies}")
    log.info(f"   ✅ New TV shows: {new_tv}")
    log.info(f"   ✅ Total new pages: {new_movies + new_tv}")
    
    # Part 3: Update index and sitemaps
    if new_movies > 0 or new_tv > 0:
        update_index()
        generate_sitemaps()
    
    log.info("\n" + "=" * 60)
    log.info("✅ Bot run complete!")
    log.info("=" * 60)

if __name__ == "__main__":
    main()
