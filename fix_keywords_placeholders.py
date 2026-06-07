#!/usr/bin/env python3
import json
import os
from pathlib import Path

def clean_keywords_placeholders(file_path):
    """تنظيف الفراغات المتكررة في keywords في ملف JSON واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # تنظيف الفراغات المتكررة في keywords
        def clean_keywords(text):
            if not text:
                return text
            # Split by comma, strip each part, filter empty strings, join back
            parts = [k.strip() for k in text.split(',') if k.strip()]
            return ', '.join(parts)
        
        # الحقول في ai_content
        if 'ai_content' in data:
            ai_content = data['ai_content']
            
            if 'keywords' in ai_content:
                original = ai_content['keywords']
                corrected = clean_keywords(original)
                if corrected != original:
                    print(f"  تنظيف keywords: '{original[:50]}...' -> '{corrected[:50]}...'")
                    ai_content['keywords'] = corrected
                    modified = True
        
        # حفظ التعديلات
        if modified:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ تم إصلاح {file_path}")
            return True
        else:
            print(f"⏭️ لا يحتاج إصلاح: {file_path}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في {file_path}: {e}")
        return False

def main():
    content_dir = Path("/home/tomito/tomito seo (copy 1)/data/content")
    
    if not content_dir.exists():
        print(f"❌ المجلد غير موجود: {content_dir}")
        return
    
    print("🔍 البحث عن ملفات JSON في data/content...")
    json_files = list(content_dir.glob("*.json"))
    print(f"📁 وجد {len(json_files)} ملف JSON")
    
    fixed_count = 0
    for json_file in json_files:
        print(f"\n🔍 فحص {json_file.name}...")
        if clean_keywords_placeholders(json_file):
            fixed_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ تم إصلاح {fixed_count} ملف من أصل {len(json_files)} ملف")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
