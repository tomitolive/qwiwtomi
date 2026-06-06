import os
import json
import glob
import time
import ai_engine
from concurrent.futures import ThreadPoolExecutor, as_completed

def process_file(f):
    try:
        with open(f, "r", encoding="utf-8") as fp:
            d = json.load(fp)
    except:
        return False
        
    ai = d.get("ai_content", {})
    desc_ar = ai.get("desc_ar", "")
    
    if not desc_ar or desc_ar.startswith("مشاهدة وتحميل") or "مترجم بجودة عالية" in desc_ar:
        title_ar = d.get('title_ar') or d.get('title')
        title_en = d.get('title_en') or d.get('title')
        overview = d.get("overview", "")
        if not overview or len(overview) < 5:
            overview = "قصة مشوقة ومثيرة للمتابعة."
            
        media_type = "tv" if "tv" in f or "مسلسل" in desc_ar else "movie"
        genres = [g.get("name", "") for g in d.get("genres", [])]
        year = d.get("release_date", d.get("first_air_date", "2026"))[:4]
        
        # Retry loop to withstand 429 Rate Limits from Groq API
        for attempt in range(5):
            res = ai_engine.generate_bilingual_description(
                title_ar, title_en, overview, overview, year, genres, media_type
            )
            if res and "desc_ar" in res:
                # Merge backwards compat in case certain fields are empty
                if not res.get("intro"): res["intro"] = ""
                if not res.get("outro"): res["outro"] = ""
                d["ai_content"] = res
                with open(f, "w", encoding="utf-8") as fw:
                    json.dump(d, fw, ensure_ascii=False, indent=2)
                return True
            time.sleep(4)
            
        return False
    return None

def main():
    files = glob.glob("data/content/*.json")
    print(f"Starting patch loop for {len(files)} files...")
    fixed = 0
    errors = 0
    
    with ThreadPoolExecutor(max_workers=2) as ex:
        futures = [ex.submit(process_file, f) for f in files]
        for idx, future in enumerate(as_completed(futures)):
            res = future.result()
            if res is True:
                fixed += 1
                if fixed % 10 == 0:
                    print(f"🚀 Fixed {fixed} pages so far...")
            elif res is False:
                errors += 1
            if idx % 100 == 0 and idx > 0:
                print(f"--- Processed {idx}/{len(files)}. Fixed: {fixed}. Errors: {errors} ---")
                
    print(f"\n✅ Patching complete! Fixed {fixed} pages successfully. (Failed: {errors})")

if __name__ == "__main__":
    main()
