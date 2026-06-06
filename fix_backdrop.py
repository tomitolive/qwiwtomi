import json
import glob
import os

count = 0
for filepath in glob.glob('data/content/*.json'):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # If no backdrop_path, but there is a poster_path, replace it.
        if not data.get('backdrop_path') and data.get('poster_path'):
            data['backdrop_path'] = data['poster_path']
            # Save the updated data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            count += 1
    except Exception as e:
        print(f"Error in {filepath}: {e}")

print(f"تم بنجاح تحديث {count} ملف: استبدال backdrop_path بـ poster_path.")
