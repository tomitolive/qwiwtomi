#!/usr/bin/env python3
import json
import re
import os
from pathlib import Path

def fix_la_casa_de_los_famosos_errors(file_path):
    """إصلاح أخطاء La Casa de los Famosos في ملف JSON واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # تصحيح "La Casa   Famosos" -> "La Casa de los Famosos"
        def fix_la_casa_de_los_famosos(text):
            if not text:
                return text
            return re.sub(r'La Casa\s+Famosos', 'La Casa de los Famosos', text)
        
        # الحقول في ai_content
        if 'ai_content' in data:
            ai_content = data['ai_content']
            
            # الحقول المفردة
            for field in ['desc_ar', 'opinion_ar', 'seo_title_ar', 'meta_desc', 'keywords']:
                if field in ai_content:
                    original = ai_content[field]
                    corrected = fix_la_casa_de_los_famosos(original)
                    if corrected != original:
                        print(f"  تصحيح {field}: '{original[:50]}...' -> '{corrected[:50]}...'")
                        ai_content[field] = corrected
                        modified = True
            
            # تصحيح faq
            if 'faq' in ai_content:
                for faq_item in ai_content['faq']:
                    for field in ['q', 'a', 'q_en', 'a_en']:
                        if field in faq_item:
                            original = faq_item[field]
                            corrected = fix_la_casa_de_los_famosos(original)
                            if corrected != original:
                                print(f"  تصحيح faq.{field}: '{original[:50]}...' -> '{corrected[:50]}...'")
                                faq_item[field] = corrected
                                modified = True
        
        # تصحيح overview
        if 'overview' in data:
            original = data['overview']
            corrected = fix_la_casa_de_los_famosos(original)
            if corrected != original:
                print(f"  تصحيح overview: '{original[:50]}...' -> '{corrected[:50]}...'")
                data['overview'] = corrected
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
        if fix_la_casa_de_los_famosos_errors(json_file):
            fixed_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ تم إصلاح {fixed_count} ملف من أصل {len(json_files)} ملف")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
