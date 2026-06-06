#!/usr/bin/env python3
import os
import json
import time
import argparse
from ai_engine import generate_bilingual_description

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')

def process_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    ai = data.get('ai_content', {})
    desc_ar = ai.get('desc_ar', '')
    
    # Check if generic description
    if "مشاهدة وتحميل" in desc_ar and "مترجم بجودة" in desc_ar:
        title_ar = data.get('title_ar') or data.get('title', '')
        title_en = data.get('title_en') or data.get('title', '')
        overview = data.get('overview', '')
        year = (data.get('release_date') or data.get('first_air_date') or '2026')[:4]
        genres_ar = [g.get('name', '') for g in data.get('genres', [])]
        media_type = data.get('media_type', 'movie')
        
        print(f"Refactoring AI Content for: {title_ar}...")
        
        try:
            result = generate_bilingual_description(
                title_ar=title_ar,
                title_en=title_en,
                overview_ar=overview,
                overview_en=overview,
                year=year,
                genres_ar=genres_ar,
                media_type=media_type
            )
            
            if result and "desc_ar" in result:
                data['ai_content'] = result
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                print(f"✅ Successfully updated: {os.path.basename(filepath)}")
                time.sleep(0.1) # 0.1 seconds wait, max speed using 5 keys
                return True
            else:
                print(f"❌ Failed to generate valid AI content for: {title_ar}")
                time.sleep(0.1)
        except Exception as e:
            print(f"❌ Exception processing {title_ar}: {e}")
            time.sleep(0.1)
            
    return False

def main(limit=10):
    files = [f for f in os.listdir(CONTENT_DIR) if f.endswith('.json')]
    count = 0
    refactored = 0
    print(f"Found {len(files)} total JSON files.")
    
    for filename in files:
        if refactored >= limit:
            break
            
        filepath = os.path.join(CONTENT_DIR, filename)
        if process_file(filepath):
            refactored += 1

    print(f"🏁 Finished! Refactored {refactored} pages.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=10, help="Number of pages to refactor")
    args = parser.parse_args()
    main(limit=args.limit)
