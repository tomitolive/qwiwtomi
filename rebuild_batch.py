#!/usr/bin/env python3
import os
import json
import logging
import mega_bot
import time

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')

def rebuild_missing(limit=5):
    if not os.path.exists(INDEX_FILE):
        log.error("Index file not found.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    os.makedirs(CONTENT_DIR, exist_ok=True)
    
    missing = []
    for item in data:
        tmdb_id = item.get('tmdb_id')
        if not tmdb_id: continue
        
        json_path = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
        is_fixed = False
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if content.get('fixed'):
                        is_fixed = True
            except:
                pass
        
        if not is_fixed:
            missing.append(item)

    log.info(f"Found {len(missing)} pages that need fixing or generation. Processing limit of {limit}...")
    
    # Create a mapping of tmdb_id to index for quick update
    index_map = {str(item.get('tmdb_id')): i for i, item in enumerate(data)}
    
    count = 0
    for item in missing[:limit]:
        tmdb_id = str(item.get('tmdb_id'))
        media_type = 'movie' if item.get('folder') == 'movie' else 'tv'
        
        try:
            log.info(f"Processing {media_type} ID: {tmdb_id} ({item.get('slug')})")
            # fetch_details handles cache/fetching
            details = mega_bot.fetch_details(tmdb_id, media_type)
            if details:
                # create_page handles mirroring images and creating JSON/HTML
                _, index_entry = mega_bot.create_page(details, media_type)
                
                # Update the main data list
                if tmdb_id in index_map:
                    idx = index_map[tmdb_id]
                    data[idx].update(index_entry)
                else:
                    data.append(index_entry)
                    index_map[tmdb_id] = len(data) - 1
                
                count += 1
                
                # Save index every few items or at least at the end
                if count % 5 == 0:
                    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    log.info(f"💾 Index saved after {count} items.")
                
                time.sleep(1) # Graceful pause
            else:
                log.error(f"Failed to fetch details for {item.get('slug')}")
        except Exception as e:
            log.error(f"Failed to rebuild {item.get('slug')}: {e}")

    # Final save
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    log.info(f"✅ Batch complete. Generated {count} pages and updated index.")

if __name__ == '__main__':
    # Increase limit for a significant batch
    rebuild_missing(limit=50)
