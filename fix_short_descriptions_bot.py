#!/usr/bin/env python3
"""
fix_short_descriptions_bot.py
------------------------------
بوت إصلاح أوصاف Meta Description القصيرة.
- يفحص جميع ملفات JSON في data/content/
- يحدد الصفحات ذات meta_desc < 150 حرف
- يعالج 15 صفحة عشوائية كل تشغيل
- يعيد توليد الوصف باستخدام AI
- يتتبع الصفحات المعالجة لتجنب التكرار
"""

import os
import json
import logging
import time
import random
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
PROCESSED_FILE = os.path.join(BASE_PATH, 'data', 'fixed_descriptions.json')
BATCH_SIZE = 15

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Import project modules
import mega_bot

def load_processed_ids():
    """تحميل قائمة المعرفات التي تم معالجتها."""
    if not os.path.exists(PROCESSED_FILE):
        return set()
    try:
        with open(PROCESSED_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('processed_ids', []))
    except Exception as e:
        log.warning(f"Could not load processed IDs: {e}")
        return set()

def save_processed_ids(processed_ids):
    """حفظ قائمة المعرفات التي تم معالجتها."""
    try:
        os.makedirs(os.path.dirname(PROCESSED_FILE), exist_ok=True)
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump({'processed_ids': list(processed_ids), 'last_updated': datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        log.error(f"Could not save processed IDs: {e}")

def find_short_descriptions():
    """البحث عن جميع الصفحات ذات الأوصاف القصيرة."""
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
            
            if meta_desc and len(meta_desc) < 150:
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
    
    log.info(f"🔍 Found {len(short_desc_pages)} pages with short descriptions (<150 chars)")
    return short_desc_pages

def process_batch(short_pages, processed_ids):
    """معالجة دفعة من الصفحات."""
    # استبعاد الصفحات التي تم معالجتها بالفعل
    available_pages = [p for p in short_pages if str(p['tmdb_id']) not in processed_ids]
    
    if not available_pages:
        log.info("✅ All short descriptions have been fixed!")
        return 0, processed_ids
    
    # اختيار 15 صفحة عشوائية
    batch = random.sample(available_pages, min(len(available_pages), BATCH_SIZE))
    log.info(f"📋 Processing {len(batch)} pages (batch size: {BATCH_SIZE})")
    
    success = 0
    for i, page in enumerate(batch):
        tmdb_id = str(page['tmdb_id'])
        media_type = page['media_type']
        title = page['title']
        
        log.info(f"[{i+1}/{len(batch)}] Fixing: {title} (ID: {tmdb_id}, current length: {page['current_length']})")
        
        try:
            # جلب بيانات TMDB
            details = mega_bot.fetch_details(tmdb_id, media_type)
            if not details:
                log.warning(f"   ⚠️ Could not fetch TMDB details for {tmdb_id}")
                continue
            
            # إعادة إنشاء الصفحة (سيتم توليد وصف جديد)
            page_path, entry = mega_bot.create_page(details, media_type, is_trend=True)
            
            if entry:
                success += 1
                processed_ids.add(tmdb_id)
                log.info(f"   ✅ Fixed: {page_path}")
                
                # التحقق من الطول الجديد
                try:
                    with open(page_path.replace('.html', '.json'), 'r', encoding='utf-8') as f:
                        new_data = json.load(f)
                    new_meta_desc = new_data.get('ai_content', {}).get('meta_desc', '')
                    new_length = len(new_meta_desc) if new_meta_desc else 0
                    log.info(f"   📏 New length: {new_length} chars")
                except:
                    pass
            else:
                log.warning(f"   ❌ AI generation failed for {title}")
                
        except Exception as e:
            log.error(f"   ❌ Error processing {title}: {e}")
        
        # استراحة قصيرة بين الطلبات
        time.sleep(2)
    
    return success, processed_ids

def main():
    log.info("🚀 Starting Fix Short Descriptions Bot...")
    log.info("=" * 60)
    
    # تحميل قائمة المعرفات التي تم معالجتها
    processed_ids = load_processed_ids()
    log.info(f"📊 Already processed: {len(processed_ids)} pages")
    
    # البحث عن أوصاف قصيرة
    short_pages = find_short_descriptions()
    
    if not short_pages:
        log.info("✅ No short descriptions found. All pages are compliant!")
        return
    
    # معالجة دفعة
    success, processed_ids = process_batch(short_pages, processed_ids)
    
    # حفظ قائمة المعرفات المحدثة
    save_processed_ids(processed_ids)
    
    # الإحصائيات
    remaining = len([p for p in short_pages if str(p['tmdb_id']) not in processed_ids])
    log.info("=" * 60)
    log.info(f"📈 Statistics:")
    log.info(f"   ✅ Fixed in this run: {success}")
    log.info(f"   📊 Total processed: {len(processed_ids)}")
    log.info(f"   ⏳ Remaining to fix: {remaining}")
    
    if remaining > 0:
        log.info(f"💡 Next run will process up to {BATCH_SIZE} more pages.")

if __name__ == "__main__":
    main()
