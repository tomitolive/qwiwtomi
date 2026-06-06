import json, glob, os
import build_homepage

content_dir = 'data/content'
index_file = 'data/content_index.json'

files = glob.glob(f'{content_dir}/*.json')
deleted_ids = set()

# 1. Delete empty files
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            if data.get('overview') == '':
                # Extract TMDB ID from filename (assuming filename is {tmdb_id}.json or {id}-{slug}.json)
                fid = os.path.basename(f).split('.')[0].split('-')[0]
                deleted_ids.add(fid)
                os.remove(f)
    except Exception as e:
        print(f"Error reading {f}: {e}")

print(f"Deleted {len(deleted_ids)} empty JSON files.")

# 2. Update index
if os.path.exists(index_file):
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    new_index = []
    for item in index_data:
        tmdb_id = str(item.get('tmdb_id'))
        if tmdb_id not in deleted_ids:
            new_index.append(item)
            
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(new_index, f, ensure_ascii=False, indent=2)
    print(f"Updated index: {len(index_data)} -> {len(new_index)} items.")

# 3. Rebuild Homepage
print("Rebuilding homepage...")
build_homepage.build()
print("Done!")
