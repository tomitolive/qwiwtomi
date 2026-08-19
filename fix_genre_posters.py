import json
import os
import glob

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
GENRE_DIR = os.path.join(BASE_PATH, 'data', 'genre')

def build_content_poster_map():
    """Build a mapping of ID -> correct poster_path from content files"""
    poster_map = {}
    content_files = glob.glob(os.path.join(CONTENT_DIR, '*.json'))
    
    print(f"📖 Reading {len(content_files)} content files...")
    for fp in content_files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            item_id = data.get('id')
            poster_path = data.get('poster_path')
            if item_id and poster_path:
                poster_map[item_id] = poster_path
        except Exception as e:
            print(f"❌ Error reading {fp}: {e}")
    
    print(f"✅ Built poster map with {len(poster_map)} entries")
    return poster_map

def fix_genre_files(poster_map):
    """Update poster paths in genre files using the correct paths from content"""
    genre_files = glob.glob(os.path.join(GENRE_DIR, '*.json'))
    
    print(f"📖 Processing {len(genre_files)} genre files...")
    updated_count = 0
    
    for fp in genre_files:
        try:
            with open(fp, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if 'items' not in data:
                continue
            
            file_updated = False
            for item in data['items']:
                item_id = item.get('id')
                current_poster = item.get('poster_path')
                correct_poster = poster_map.get(item_id)
                
                # Update if correct poster exists and current is different
                if item_id and correct_poster:
                    # Remove leading slash from current for comparison
                    current_normalized = current_poster.lstrip('/') if current_poster else ''
                    correct_normalized = correct_poster.lstrip('/') if correct_poster else ''
                    
                    if current_normalized != correct_normalized:
                        print(f"🔄 Updating ID {item_id} in {os.path.basename(fp)}: {current_poster} -> {correct_poster}")
                        item['poster_path'] = correct_poster
                        file_updated = True
            
            if file_updated:
                with open(fp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                updated_count += 1
                print(f"✅ Updated {os.path.basename(fp)}")
                
        except Exception as e:
            print(f"❌ Error processing {fp}: {e}")
    
    print(f"🎉 Updated {updated_count} genre files")

def main():
    print("🚀 Starting genre poster fix...")
    poster_map = build_content_poster_map()
    fix_genre_files(poster_map)
    print("✨ Done!")

if __name__ == '__main__':
    main()
