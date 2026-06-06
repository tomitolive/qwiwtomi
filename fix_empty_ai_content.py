#!/usr/bin/env python3
import os
import json
import logging
import time
import argparse
from ai_engine import generate_bilingual_description

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

CONTENT_DIR = "data/content"

def fix_empty_ai_content(limit=None):
    files = [f for f in os.listdir(CONTENT_DIR) if f.endswith(".json")]
    
    # Filter files that need fixing
    to_fix = []
    for f in files:
        path = os.path.join(CONTENT_DIR, f)
        with open(path, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                ai = data.get("ai_content", {})
                if not ai.get("desc_en", "").strip() or not ai.get("desc_ar", "").strip():
                    to_fix.append(path)
            except Exception as e:
                pass
                
    log.info(f"Found {len(to_fix)} files with empty ai_content out of {len(files)} total files.")
    
    if limit is not None:
        to_fix = to_fix[:limit]
        log.info(f"Limiting to {limit} files for this run.")
        
    log.info("Starting patch process...")
    
    success = 0
    for idx, path in enumerate(to_fix):
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as file:
            data = json.load(file)
            
        title_ar = data.get("title_ar") or data.get("title", "")
        title_en = data.get("title_en") or data.get("title", "")
        overview = data.get("overview", "")
        media_type = data.get("media_type", "movie")
        release_date = data.get("release_date", "2026")
        
        # safely get year
        year = str(release_date)[:4] if release_date else "2026"
        
        genres_raw = data.get("genres", [])
        genres_ar = [g.get("name", "") for g in genres_raw if isinstance(g, dict)] if genres_raw else []
        
        log.info(f"[{idx+1}/{len(to_fix)}] Generating content for: {title_ar} ({filename})")
        
        try:
            ai_data = generate_bilingual_description(
                 title_ar, title_en, overview, overview, year, genres_ar, media_type
            )
            
            if ai_data and ai_data.get("desc_ar") and ai_data.get("desc_en"):
                current_ai = data.get("ai_content", {})
                current_ai["desc_ar"] = ai_data.get("desc_ar", current_ai.get("desc_ar", ""))
                current_ai["desc_en"] = ai_data.get("desc_en", current_ai.get("desc_en", ""))
                current_ai["meta_desc"] = ai_data.get("meta_desc", current_ai.get("meta_desc", ""))
                current_ai["keywords"] = ai_data.get("keywords", current_ai.get("keywords", ""))
                current_ai["seo_title_ar"] = ai_data.get("seo_title_ar", current_ai.get("seo_title_ar", ""))
                current_ai["opinion"] = ai_data.get("opinion", current_ai.get("opinion", ""))
                if "faq" in ai_data:
                     current_ai["faq"] = ai_data["faq"]
                     
                data["ai_content"] = current_ai
                
                with open(path, "w", encoding="utf-8") as out_file:
                    json.dump(data, out_file, ensure_ascii=False, indent=2)
                    
                success += 1
                log.info(f"  ✅ Fixed {filename}")
            else:
                log.warning(f"  ❌ Generation returned empty or invalid data for {filename}")
                
        except Exception as e:
            log.error(f"  ❌ Error processing {filename}: {e}")
            
        time.sleep(2)  # Mandatory rate limit compliance
        
    log.info(f"Process complete. Successfully fixed {success}/{len(to_fix)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fix empty ai_content in JSON files")
    parser.add_argument("--limit", type=int, default=None, help="Number of pages to fix in this run")
    args = parser.parse_args()
    
    fix_empty_ai_content(limit=args.limit)
