#!/usr/bin/env python3
import json
import re
import os
from pathlib import Path

# Country translation map
COUNTRIES_MAP = {
    'Thailand': 'تايلاند',
    'Japan': 'اليابان',
    'South Korea': 'كوريا الجنوبية',
    'France': 'فرنسا',
    'Germany': 'ألمانيا',
    'United States': 'الولايات المتحدة',
    'USA': 'الولايات المتحدة',
    'United States of America': 'الولايات المتحدة',
    'United Kingdom': 'المملكة المتحدة',
    'UK': 'المملكة المتحدة',
    'Italy': 'إيطاليا',
    'Spain': 'إسبانيا',
    'China': 'الصين',
    'India': 'الهند',
    'Brazil': 'البرازيل',
    'Mexico': 'المكسيك',
    'Canada': 'كندا',
    'Australia': 'أستراليا',
    'Russia': 'روسيا',
    'Turkey': 'تركيا',
    'Egypt': 'مصر',
    'Saudi Arabia': 'السعودية',
    'United Arab Emirates': 'الإمارات العربية المتحدة',
    'UAE': 'الإمارات العربية المتحدة',
    'Indonesia': 'إندونيسيا',
    'Philippines': 'الفلبين',
    'Vietnam': 'فيتنام',
    'Malaysia': 'ماليزيا',
    'Singapore': 'سنغافورة',
    'Hong Kong': 'هونغ كونغ',
    'Taiwan': 'تايوان',
    'Poland': 'بولندا',
    'Sweden': 'السويد',
    'Norway': 'النرويج',
    'Denmark': 'الدنمارك',
    'Netherlands': 'هولندا',
    'Belgium': 'بلجيكا',
    'Switzerland': 'سويسرا',
    'Austria': 'النمسا',
    'Czech Republic': 'جمهورية التشيك',
    'Czechoslovakia': 'تشيكوسلوفاكيا',
    'Hungary': 'المجر',
    'Romania': 'رومانيا',
    'Bulgaria': 'بلغاريا',
    'Greece': 'اليونان',
    'Portugal': 'البرتغال',
    'Argentina': 'الأرجنتين',
    'Colombia': 'كولومبيا',
    'Chile': 'تشيلي',
    'Peru': 'بيرو',
    'Bolivia': 'بوليفيا',
    'South Africa': 'جنوب أفريقيا',
    'Nigeria': 'نيجيريا',
    'Kenya': 'كينيا',
    'Morocco': 'المغرب',
    'Algeria': 'الجزائر',
    'Tunisia': 'تونس',
    'Libya': 'ليبيا',
    'Sudan': 'السودان',
    'Iraq': 'العراق',
    'Syria': 'سوريا',
    'Jordan': 'الأردن',
    'Lebanon': 'لبنان',
    'Kuwait': 'الكويت',
    'Qatar': 'قطر',
    'Bahrain': 'البحرين',
    'Oman': 'عمان',
    'Yemen': 'اليمن',
    'Pakistan': 'باكستان',
    'Bangladesh': 'بنغلاديش',
    'Sri Lanka': 'سريلانكا',
    'Nepal': 'نيبال',
    'Myanmar': 'ميانمار',
    'Cambodia': 'كمبوديا',
    'Laos': 'لاوس',
    'New Zealand': 'نيوزيلندا',
    'Ireland': 'أيرلندا',
    'Finland': 'فنلندا',
    'Iceland': 'آيسلندا',
    'Estonia': 'إستونيا',
    'Latvia': 'لاتفيا',
    'Lithuania': 'ليتوانيا',
    'Ukraine': 'أوكرانيا',
    'Belarus': 'بيلاروسيا',
    'Kazakhstan': 'كازاخستان',
    'Uzbekistan': 'أوزبكستان',
    'Afghanistan': 'أفغانستان',
    'Iran': 'إيران',
    'Israel': 'إسرائيل',
    'North Korea': 'كوريا الشمالية',
    'Mongolia': 'منغوليا',
    'Georgia': 'جورجيا',
    'Armenia': 'أرمينيا',
    'Azerbaijan': 'أذربيجان',
    'Cyprus': 'قبرص',
    'Malta': 'مالطا',
    'Luxembourg': 'لوكسمبورغ',
    'Monaco': 'موناكو',
    'San Marino': 'سان مارينو',
    'Vatican City': 'الفاتيكان',
    'Liechtenstein': 'ليختنشتاين',
    'Andorra': 'أندورا',
    'Croatia': 'كرواتيا',
    'Serbia': 'صربيا',
    'Bolivia': 'بوليفيا',
    'Dominican Republic': 'جمهورية الدومينيكان',
    'Soviet Union': 'الاتحاد السوفيتي',
    'Yugoslavia': 'يوغوسلافيا',
    'East Germany': 'ألمانيا الشرقية',
    'Aruba': 'أروبا',
}

def fix_jack_joker_errors(file_path):
    """إصلاح أخطاء Jack Joker و country في ملف JSON واحد"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        modified = False
        
        # 1. تصحيح "Jack Joker:  Steal" -> "Jack Joker: U Steal"
        def fix_jack_joker(text):
            if not text:
                return text
            return re.sub(r'Jack Joker:\s+Steal', 'Jack Joker: U Steal', text)
        
        # الحقول في ai_content
        if 'ai_content' in data:
            ai_content = data['ai_content']
            
            # الحقول المفردة
            for field in ['desc_ar', 'opinion_ar', 'seo_title_ar', 'meta_desc', 'keywords']:
                if field in ai_content:
                    original = ai_content[field]
                    corrected = fix_jack_joker(original)
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
                            corrected = fix_jack_joker(original)
                            if corrected != original:
                                print(f"  تصحيح faq.{field}: '{original[:50]}...' -> '{corrected[:50]}...'")
                                faq_item[field] = corrected
                                modified = True
        
        # 2. تصحيح country بالعربية
        if 'country' in data:
            original_country = data['country']
            if original_country in COUNTRIES_MAP:
                corrected_country = COUNTRIES_MAP[original_country]
                if corrected_country != original_country:
                    print(f"  تصحيح country: '{original_country}' -> '{corrected_country}'")
                    data['country'] = corrected_country
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
        if fix_jack_joker_errors(json_file):
            fixed_count += 1
    
    print(f"\n{'='*50}")
    print(f"✅ تم إصلاح {fixed_count} ملف من أصل {len(json_files)} ملف")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
