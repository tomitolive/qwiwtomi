#!/usr/bin/env python3
"""
Episode Content Bot - Generates SEO-friendly content for TV series episodes
"""
import json
import logging
import os
import random
import re
import time
from datetime import datetime
from typing import Dict, List, Optional

import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger(__name__)

# Configuration
TMDB_API_KEY = "882e741f7283dc9ba1654d4692ec30f6"
TMDB_BASE_URL = "https://api.themoviedb.org/3"
AI_API_KEY = "Q.Ab8RN6LsqD04OPTWaZMQIFuZuC23mctJGFhNW6nzR8YBmdtgZw"
CONTENT_INDEX_PATH = "data/content_index.json"
EPISODES_DIR = "data/episodes"
PROXY_FILE = "data/pro/proxies.txt"

def get_proxy_file_path():
    """Get the correct proxy file path"""
    possible_paths = [
        PROXY_FILE,
        "qwiwtomi/data/pro/proxies.txt",
        "data/pro/proxies.txt"
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return PROXY_FILE

def get_random_proxy():
    """Get a random proxy from the proxy file"""
    proxy_file = get_proxy_file_path()
    try:
        with open(proxy_file, 'r', encoding='utf-8') as f:
            proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                proxy = random.choice(proxies)
                # Format: ip:port:user:pass
                parts = proxy.split(':')
                if len(parts) == 4:
                    ip, port, user, pwd = parts
                    return f"http://{user}:{pwd}@{ip}:{port}"
    except Exception as e:
        log.warning(f"Error reading proxy file: {e}")
    return None

def fetch_trending_keywords(title, geo='SA'):
    """Fetch trending keywords using pytrends with proxy"""
    try:
        from pytrends.request import TrendReq
        
        proxy = get_random_proxy()
        proxies = [proxy] if proxy else []
        
        # Check if title has Arabic characters
        is_arabic = bool(re.search(r'[\u0600-\u06FF]', title))
        
        # Try without proxy first, then with proxy if needed
        for use_proxy in [False, True]:
            try:
                if use_proxy and proxies:
                    pytrends = TrendReq(
                        hl='ar' if is_arabic else 'en-US', 
                        tz=360, 
                        timeout=(10, 25), 
                        proxies=proxies, 
                        retries=2, 
                        backoff_factor=2
                    )
                else:
                    pytrends = TrendReq(
                        hl='ar' if is_arabic else 'en-US', 
                        tz=360, 
                        timeout=(10, 25), 
                        retries=2, 
                        backoff_factor=2
                    )
                
                pytrends.build_payload([title], cat=0, timeframe='now 7-d', geo=geo)
                data = pytrends.related_queries().get(title)
                
                keywords = []
                if data:
                    if data.get('rising') is not None and not data['rising'].empty:
                        keywords.extend(data['rising']['query'].tolist()[:10])
                    if data.get('top') is not None and not data['top'].empty:
                        keywords.extend(data['top']['query'].tolist()[:10])
                
                if keywords:
                    return ", ".join(keywords[:15])
                    
            except Exception as e:
                if use_proxy:
                    log.warning(f"Pytrends with proxy failed for '{title}': {e}")
                else:
                    log.debug(f"Pytrends without proxy failed, trying with proxy: {e}")
                continue
        
        # If all attempts fail, return some basic keywords based on title
        log.warning(f"Pytrends completely failed for '{title}', using fallback keywords")
        return f"{title}, مشاهدة, تحميل, مسلسل, حلقة"
        
    except Exception as e:
        log.warning(f"Pytrends failed for '{title}': {e}")
        return f"{title}, مشاهدة, تحميل, مسلسل, حلقة"

def generate_ai_content(series_title, episode_title, episode_overview, season, episode):
    """Generate SEO content using AI API"""
    keywords = fetch_trending_keywords(f"{series_title} {episode_title}")
    
    # Create a prompt for AI to generate bilingual content
    prompt = f"""
Generate SEO-optimized content for a TV episode in both Arabic and English.

Series: {series_title}
Episode: {episode_title} (Season {season}, Episode {episode})
Overview: {episode_overview}

Generate the following fields in JSON format:
- intro: Short Arabic intro (1-2 sentences)
- desc_ar: Arabic description (2-3 sentences)
- desc_en: English description (2-3 sentences)
- meta_desc: Arabic meta description (1 sentence)
- seo_title_ar: Arabic SEO title
- seo_title_en: English SEO title
- outro: Arabic outro (1 sentence)
- opinion_ar: Arabic opinion (1 sentence)
- opinion_en: English opinion (1 sentence)
- faq: Array of objects with q (Arabic question), a (Arabic answer), q_en (English question), a_en (English answer) - at least 2 FAQs
- keywords: SEO keywords (comma-separated)

Return ONLY valid JSON, no markdown formatting.
"""
    
    try:
        response = requests.post(
            "https://api.cohere.ai/v1/generate",
            headers={
                "Authorization": f"Bearer {AI_API_KEY}",
                "Content-Type": "application/json",
                "X-Client-Name": "episode-content-bot"
            },
            json={
                "model": "command-r-08-2024",
                "prompt": prompt,
                "max_tokens": 1000,
                "temperature": 0.7,
                "k": 0,
                "stop_sequences": [],
                "return_likelihoods": "NONE"
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result.get('generations', [{}])[0].get('text', '').strip()
            
            # Try to parse JSON from the response
            # Remove markdown code blocks if present
            content = content.replace('```json', '').replace('```', '').strip()
            
            try:
                ai_content = json.loads(content)
                ai_content['keywords'] = keywords  # Override with our fetched keywords
                return ai_content
            except json.JSONDecodeError:
                log.warning(f"Failed to parse AI response as JSON, using fallback")
                return get_fallback_content(series_title, episode_title, season, episode, keywords)
        else:
            log.warning(f"AI API returned status {response.status_code}, using fallback")
            return get_fallback_content(series_title, episode_title, season, episode, keywords)
            
    except Exception as e:
        log.warning(f"AI API error: {e}, using fallback")
        return get_fallback_content(series_title, episode_title, season, episode, keywords)

def get_fallback_content(series_title, episode_title, season, episode, keywords):
    """Generate fallback content when AI fails"""
    # Generate diverse FAQs related to the episode
    faqs = [
        {
            "q": f"ما هي قصة الحلقة {episode_title} من مسلسل {series_title}؟",
            "a": f"تدور أحداث الحلقة {episode_title} في إطار مشوق من مسلسل {series_title}",
            "q_en": f"What is the story of episode {episode_title} from {series_title}?",
            "a_en": f"The events of episode {episode_title} unfold in an exciting framework of {series_title}"
        },
        {
            "q": f"متى تم عرض الحلقة {episode} من الموسم {season}؟",
            "a": f"تم عرض الحلقة {episode} من الموسم {season} كجزء من مسلسل {series_title}",
            "q_en": f"When was episode {episode} of season {season} aired?",
            "a_en": f"Episode {episode} of season {season} was aired as part of {series_title}"
        },
        {
            "q": f"هل يمكن مشاهدة الحلقة {episode_title} مترجمة؟",
            "a": f"نعم، يمكنك مشاهدة الحلقة {episode_title} من {series_title} مترجمة بجودة عالية",
            "q_en": f"Can I watch episode {episode_title} with subtitles?",
            "a_en": f"Yes, you can watch episode {episode_title} from {series_title} with subtitles in high quality"
        },
        {
            "q": f"ما هو تقييم الحلقة {episode} من مسلسل {series_title}؟",
            "a": f"حلقة {episode} من مسلسل {series_title} حصلت على تقييم جيد من المشاهدين",
            "q_en": f"What is the rating of episode {episode} from {series_title}?",
            "a_en": f"Episode {episode} from {series_title} received a good rating from viewers"
        },
        {
            "q": f"كم مدة الحلقة {episode_title} من {series_title}؟",
            "a": f"تستمر الحلقة {episode_title} من مسلسل {series_title} لمدة عادية من الحلقات التلفزيونية",
            "q_en": f"How long is episode {episode_title} from {series_title}?",
            "a_en": f"Episode {episode_title} from {series_title} runs for a standard TV episode duration"
        }
    ]
    
    return {
        "intro": f"استمتع بمشاهدة الحلقة {episode} من الموسم {season} من مسلسل {series_title}",
        "desc_ar": f"حلقة {episode} من الموسم {season} من مسلسل {series_title}",
        "desc_en": f"Episode {episode} of season {season} from {series_title}",
        "meta_desc": f"شاهد الحلقة {episode} من الموسم {season} من مسلسل {series_title} مترجم بجودة عالية",
        "seo_title_ar": f"مشاهدة الحلقة {episode} الموسم {season} من {series_title} مترجم",
        "seo_title_en": f"Watch Episode {episode} Season {season} of {series_title}",
        "outro": "شاهد المزيد من الحلقات على توميتو",
        "opinion_ar": f"حلقة ممتعة من مسلسل {series_title}",
        "opinion_en": f"An enjoyable episode from {series_title}",
        "faq": faqs,
        "keywords": keywords
    }

def get_tv_series():
    """Get TV series from content index"""
    try:
        with open(CONTENT_INDEX_PATH, 'r', encoding='utf-8') as f:
            content_index = json.load(f)
        
        tv_series = []
        for item in content_index:
            if item.get('type') == 'tv':
                tv_series.append(item)
        
        return tv_series
    except Exception as e:
        log.error(f"Error reading content index: {e}")
        return []

def get_series_details(series_id):
    """Get series details from TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/tv/{series_id}"
        params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log.error(f"Error fetching series details: {e}")
    return None

def get_season_details(series_id, season_number):
    """Get season details from TMDB"""
    try:
        url = f"{TMDB_BASE_URL}/tv/{series_id}/season/{season_number}"
        params = {'api_key': TMDB_API_KEY, 'language': 'en-US'}
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        log.error(f"Error fetching season details: {e}")
    return None

def save_episode_data(series_id, season, episode, data):
    """Save episode data to JSON file"""
    try:
        os.makedirs(EPISODES_DIR, exist_ok=True)
        filename = f"{series_id}_s{season}_e{episode}.json"
        filepath = os.path.join(EPISODES_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        log.info(f"Saved: {filename}")
    except Exception as e:
        log.error(f"Error saving episode data: {e}")

def process_series(series_item):
    """Process a single TV series"""
    series_id = series_item.get('tmdb_id') or series_item.get('id')
    series_title = series_item.get('title_ar') or series_item.get('title_en') or series_item.get('title')
    # Remove duplicate titles (e.g., "Title / Title" -> "Title")
    if ' / ' in series_title:
        parts = series_title.split(' / ')
        if parts[0] == parts[1]:
            series_title = parts[0]
    series_slug = series_item.get('slug', f"{series_id}-{series_title.lower().replace(' ', '-')}")
    
    log.info(f"Processing series: {series_title} (ID: {series_id})")
    
    # Get series details
    series_details = get_series_details(series_id)
    if not series_details:
        log.error(f"Failed to get details for series {series_id}")
        return
    
    # Get seasons
    seasons = series_details.get('seasons', [])
    log.info(f"Series {series_id} has {len(seasons)} seasons")
    
    for season_data in seasons:
        season_number = season_data.get('season_number')
        if season_number == 0:  # Skip specials
            continue
        
        log.info(f"Season {season_number}: {season_data.get('episode_count', 0)} episodes")
        
        # Get season details
        season_details = get_season_details(series_id, season_number)
        if not season_details:
            log.warning(f"Failed to get details for season {season_number}")
            continue
        
        episodes = season_details.get('episodes', [])
        
        for i, episode_data in enumerate(episodes, 1):
            episode_number = episode_data.get('episode_number')
            episode_title = episode_data.get('name')
            episode_overview = episode_data.get('overview', '')
            still_path = episode_data.get('still_path')
            air_date = episode_data.get('air_date')
            vote_average = episode_data.get('vote_average', 0.0)
            vote_count = episode_data.get('vote_count', 0)
            
            log.info(f"Processing episode {i}/{len(episodes)}: S{season_number}E{episode_number}")
            
            # Generate AI content
            ai_content = generate_ai_content(
                series_title, 
                episode_title, 
                episode_overview, 
                season_number, 
                episode_number
            )
            
            # Prepare episode data
            episode_data_full = {
                "series_id": series_id,
                "series_title": series_title,
                "series_slug": series_slug,
                "season": season_number,
                "episode": episode_number,
                "episode_title": episode_title,
                "overview": episode_overview,
                "air_date": air_date,
                "still_path": still_path,
                "vote_average": vote_average,
                "vote_count": vote_count,
                "ai_content": ai_content
            }
            
            # Save episode data
            save_episode_data(series_id, season_number, episode_number, episode_data_full)
            
            # Delay to avoid rate limiting
            time.sleep(2)

def main():
    """Main function"""
    log.info("Starting Episode Content Bot")
    
    # Get TV series
    tv_series = get_tv_series()
    
    if not tv_series:
        log.error("No TV series found")
        return
    
    # Process only the first series (for testing)
    log.info("Processing first series only...")
    try:
        process_series(tv_series[0])
    except Exception as e:
        log.error(f"Error processing series: {e}")
    
    log.info("Episode Content Bot completed")

if __name__ == "__main__":
    main()
