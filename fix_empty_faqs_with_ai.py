#!/usr/bin/env python3
print(">>> SCRIPT STARTING <<<", flush=True)
import os
import json
import logging
import time
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed

def load_env_manually():
    try:
        with open('.env') as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    os.environ[k] = v.strip('"\'')
    except Exception:
        pass
load_env_manually()

logging.basicConfig(level=logging.INFO, format='%(message)s')
log = logging.getLogger(__name__)

import ai_engine

GEMINI_API_KEY = "AIzaSyC2Q8gXvNGnQLQjqkagtQduNewKibZrJb8"

def generate_ai_faq(title, overview, media_type):
    prompt = f"""Generate an SEO-optimized Arabic FAQ section for the {"movie" if media_type == "movie" else "TV Show"} '{title}'.
Overview: {overview[:500]}
Provide exactly 3 distinct questions and answers about the story, release, or characters.
Output ONLY a raw JSON array of objects. Each object must have "q" for Question and "a" for Answer. 
Example format:
[
  {{"q": "ما هي قصة فيلم/مسلسل...؟", "a": "..."}},
  {{"q": "...", "a": "..."}}
]
DO NOT surround it with markdown, no ```json, just raw JSON array."""

    for _ in range(3):
        try:
            res = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.3}
                },
                timeout=30
            )
            if res.status_code == 200:
                data = res.json()
                try:
                    text = data['candidates'][0]['content']['parts'][0]['text'].strip()
                except (KeyError, IndexError):
                    print(f"Unexpected Gemini response structure: {data}", flush=True)
                    continue

                if text.startswith('```json'):
                    text = text.replace('```json', '', 1)
                text = text.replace('```', '')
                
                try:
                    parsed = json.loads(text.strip())
                    if isinstance(parsed, list) and len(parsed) > 0 and 'q' in parsed[0]:
                        return parsed
                except Exception as parse_e:
                    print(f"JSON Parsing Error: {parse_e}\nText was: {text}", flush=True)
            else:
                print(f"API Error {res.status_code}: {res.text}", flush=True)
                time.sleep(2)
                continue
        except Exception as e:
            print(f"Exception: {e}", flush=True)
            time.sleep(2)
            continue
    print(f"Failed to generate FAQ for {title}", flush=True)
    return None

data_dir = 'data/content'
def process_file(filename):
    filepath = os.path.join(data_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    ai = data.get('ai_content', {})
    faq = ai.get('faq', [])
    
    is_generic = False
    if faq and len(faq) > 0:
        first_q = faq[0].get('q', '')
        if first_q.startswith('متى يتوفر') or first_q.startswith('متى تتوفر'):
            is_generic = True
            
    if is_generic:
        title = data.get('title_ar') or data.get('title')
        overview = data.get('overview') or ai.get('desc_ar') or ""
        media_type = 'tv' if data.get('first_air_date') else 'movie'
        
        print(f"Processing generating AI info for {filename} ({title})...", flush=True)
        new_faq = generate_ai_faq(title, str(overview), media_type)
        if new_faq:
            data['ai_content']['faq'] = new_faq
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Successfully processed {filename}", flush=True)
            time.sleep(4) # Throttle to 15 RPM
            return True
            
    return False

def main():
    files = [f for f in os.listdir(data_dir) if f.endswith('.json')]
    count = 0
    print(f"Found {len(files)} files to check. Starting...", flush=True)
    for f in files:
        if process_file(f):
            count += 1
            if count % 2 == 0:
                print(f"✅ Fixed {count} pages with AI FAQs...", flush=True)
                    
    print(f"🎉 Finished! Replaced {count} generic FAQs with real AI generated ones.", flush=True)

if __name__ == '__main__':
    main()
