#!/usr/bin/env python3
"""
fix_short_descriptions_bot.py
------------------------------
بوت إصلاح أوصاف Meta Description القصيرة.
- يفحص جميع ملفات JSON في data/content/
- يحدد الصفحات ذات meta_desc خارج النطاق 150-160 حرف
- يعالج جميع الصفحات أو دفعة محددة كل تشغيل
- يعيد توليد الوصف باستخدام AI مع الحقول الموحدة
- يتتبع الصفحات المعالجة لتجنب التكرار
- يعمل مع نفس الحقول مثل run_bot_with_mixed_content.py
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
PROCESSED_FILE = os.path.join(BASE_PATH, 'data', 'fixed_pages.json')
PAGES_TO_FIX_FILE = os.path.join(BASE_PATH, 'data', 'pages_to_fix.json')
BATCH_SIZE = 7

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
            page_path, entry = mega_bot.create_page(details, media_type, is_trend=True)
            
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

def main():
    log.info("🚀 Starting Fix Short Descriptions Bot...")
    log.info("=" * 60)
    
    # تحميل قائمة الصفحات التي تم إصلاحها
    fixed_pages = load_fixed_pages()
    log.info(f"📊 Already fixed: {len(fixed_pages)} pages")
    
    # البحث عن أوصاف قصيرة
    short_pages = find_short_descriptions()
    
    if not short_pages:
        log.info("✅ No short descriptions found. All pages are compliant!")
        return
    
    # معالجة دفعة
    success, fixed_pages = process_batch(short_pages, fixed_pages)
    
    # حفظ قائمة الصفحات المحدثة
    save_fixed_pages(fixed_pages)
    
    # الإحصائيات
    fixed_ids = {str(p['tmdb_id']) for p in fixed_pages}
    remaining = len([p for p in short_pages if str(p['tmdb_id']) not in fixed_ids])
    log.info("=" * 60)
    log.info(f"📈 Statistics:")
    log.info(f"   ✅ Fixed in this run: {success}")
    log.info(f"   📊 Total fixed: {len(fixed_pages)}")
    log.info(f"   ⏳ Remaining to fix: {remaining}")
    
    if remaining > 0:
        log.info(f"💡 Next run will process up to {BATCH_SIZE} more pages.")

if __name__ == "__main__":
    main()
