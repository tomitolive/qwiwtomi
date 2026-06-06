#!/usr/bin/env python3
"""Downloads all missing backdrop images from TMDB to local storage."""
import json, glob, os, requests, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE, 'data', 'content')
BACKDROP_DIR = os.path.join(BASE, 'public', 't', 'p', 'original')
os.makedirs(BACKDROP_DIR, exist_ok=True)

def download_one(backdrop_path):
    filename = backdrop_path.lstrip('/')
    local_path = os.path.join(BACKDROP_DIR, filename)
    if os.path.exists(local_path):
        return None  # already exists
    
    url = f"https://image.tmdb.org/t/p/original/{filename}"
    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            with open(local_path, 'wb') as f:
                f.write(resp.content)
            return filename
    except Exception as e:
        print(f"❌ Failed: {filename}: {e}")
    return None

def main():
    files = glob.glob(os.path.join(CONTENT_DIR, '*.json'))
    missing = []
    
    for f in files:
        try:
            d = json.load(open(f, 'r', encoding='utf-8'))
            bp = d.get('backdrop_path', '')
            if bp:
                local_path = os.path.join(BACKDROP_DIR, bp.lstrip('/'))
                if not os.path.exists(local_path):
                    missing.append(bp)
        except:
            pass
    
    print(f"🖼️  Found {len(missing)} missing backdrops. Downloading...")
    
    done = 0
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(download_one, bp): bp for bp in missing}
        for future in as_completed(futures):
            result = future.result()
            if result:
                done += 1
                if done % 20 == 0 or done == len(missing):
                    pct = (done / len(missing)) * 100
                    print(f"  ✅ {done}/{len(missing)} ({pct:.1f}%)")
    
    print(f"\n🏁 Done! Downloaded {done} backdrops.")

if __name__ == '__main__':
    main()
