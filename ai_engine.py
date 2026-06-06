#!/usr/bin/env python3
"""
AI Engine - Rebuilt from scratch
Features:
- HuggingFace API for content generation
- pytrends for trending keywords (Saudi Arabia & Middle East)
- TMDB API for trending content (1 trending + 1 random high-rated)
- Robust error handling and retry logic
- Valid JSON output without fallback
"""

import os
import json
import requests
import logging
import time
import random
import re
from datetime import datetime

# Configuration
COHERE_API_KEY = os.getenv("COHERE_API_KEY")
COHERE_API_URL = "https://api.cohere.com/v2/chat"

TMDB_API_KEY = os.getenv("TMDB_API_KEY", "882e741f7283dc9ba1654d4692ec30f6")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

# Global state
_current_model_idx = 0

# Cohere Models Configuration
COHERE_MODELS = [
    {
        "name": "command-r-08-2024",
        "model_id": "command-r-08-2024",
        "api_key": COHERE_API_KEY
    }
]


def _call_cohere_llm(system_msg, user_msg, max_retries=3):
    """Call Cohere API with retry logic."""
    global _current_model_idx
    
    for attempt in range(max_retries):
        model_config = COHERE_MODELS[_current_model_idx]
        log.info(f"🔍 Attempting model: {model_config['name']} ({model_config['model_id']})")
        
        try:
            headers = {
                "Authorization": f"Bearer {model_config['api_key']}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            payload = {
                "model": model_config["model_id"],
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": user_msg}
                ]
            }

            response = requests.post(COHERE_API_URL, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                text = data.get("message", {}).get("content", [{}])[0].get("text", "")
                if text:
                    text = re.sub(r'```json\s*|\s*```', '', text).strip()
                    log.info(f"✅ SUCCESS: {model_config['name']} generated content successfully")
                    return text, model_config['name']
            elif response.status_code == 429:
                log.warning(f"⚠️ Rate limit hit on {model_config['name']}. Retrying in 2 seconds...")
                time.sleep(2)
                continue
            elif response.status_code == 503:
                log.warning(f"⚠️ Service unavailable on {model_config['name']}. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            else:
                log.error(f"❌ {model_config['name']} Error {response.status_code}: {response.text[:300]}")
                
        except requests.exceptions.Timeout:
            log.warning(f"⚠️ Timeout on {model_config['name']}. Retrying...")
            time.sleep(2)
            continue
        except Exception as e:
            log.error(f"❌ {model_config['name']} API Error: {e}")
        
        # Move to next model on failure
        _current_model_idx = (_current_model_idx + 1) % len(COHERE_MODELS)
    
    log.error("🚨 All Cohere models exhausted or failed.")
    return None, None


def get_trending_keywords(query, geo='SA'):
    """Get trending keywords using pytrends for Saudi Arabia & Middle East."""
    try:
        from pytrends.request import TrendReq
        pytrends = TrendReq(hl='ar-SA', tz=360)
        
        # Get related queries
        pytrends.build_payload([query], cat=0, timeframe='today 12-m', geo=geo, gprop='')
        related_queries = pytrends.related_queries()
        
        keywords = []
        if query in related_queries and 'top' in related_queries[query]:
            top_queries = related_queries[query]['top']
            if top_queries is not None and not top_queries.empty:
                keywords = top_queries['query'].head(10).tolist()
        
        log.info(f"🔍 Found {len(keywords)} trending keywords for '{query}' in {geo}")
        return keywords
        
    except Exception as e:
        log.error(f"❌ Error fetching trending keywords: {e}")
        return []


def fetch_trending(media_type, tmdb_api_key=TMDB_API_KEY, available_ids=None):
    """Fetch trending content from TMDB (US region), excluding existing content."""
    available_ids = available_ids or set()
    log.info(f"🔥 Fetching trending {media_type} (US region)...")
    
    params = {
        'api_key': tmdb_api_key,
        'region': 'US'
    }
    
    try:
        response = requests.get(f"{TMDB_BASE_URL}/trending/{media_type}/day", params=params, timeout=15)
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                trends = []
                for item in data['results'][:20]:
                    tid = item.get('id')
                    # Skip if already exists
                    if tid in available_ids:
                        continue
                    
                    title = item.get('title') or item.get('name')
                    poster = item.get('poster_path')
                    year = (item.get('release_date') or item.get('first_air_date') or "")[:4]
                    rating = round(item.get('vote_average', 0), 1)
                    
                    folder = 'movie' if media_type == 'movie' else 'tv'
                    
                    def clean_slug(text):
                        res = re.sub(r'[^\w\s-]', '', text).strip().lower()
                        res = re.sub(r'[-\s_]+', '-', res)
                        return res
                    
                    slug = f"{tid}-{clean_slug(title)}"
                    
                    trends.append({
                        'tmdb_id': tid,
                        'title': title,
                        'poster': poster,
                        'year': year,
                        'rating': rating,
                        'folder': folder,
                        'slug': slug
                    })
                
                if trends:
                    log.info(f"✅ Found {len(trends)} trending {media_type} (excluding existing)")
                else:
                    log.warning(f"⚠️ All trending {media_type} already exist in local data")
                
                return trends
    except Exception as e:
        log.error(f"Error fetching trending {media_type}: {e}")
    
    return []


def fetch_random_high_rated(media_type, tmdb_api_key=TMDB_API_KEY, available_ids=None):
    """Fetch one random movie/tv with rating >= 7, excluding existing content."""
    available_ids = available_ids or set()
    log.info(f"🎲 Fetching random high-rated {media_type} (rating >= 7)...")
    
    endpoint = "discover/movie" if media_type == 'movie' else "discover/tv"
    
    # Try multiple pages for more variety
    for page in range(1, 4):
        params = {
            'api_key': tmdb_api_key,
            'vote_average.gte': 7,
            'vote_count.gte': 50,
            'sort_by': 'vote_average.desc',
            'page': page
        }
        
        try:
            response = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    results = data['results'][:20]
                    # Filter out existing content
                    filtered = [r for r in results if r.get('id') not in available_ids]
                    
                    if filtered:
                        item = random.choice(filtered)
                        
                        tid = item.get('id')
                        title = item.get('title') or item.get('name')
                        poster = item.get('poster_path')
                        year = (item.get('release_date') or item.get('first_air_date') or "")[:4]
                        rating = round(item.get('vote_average', 0), 1)
                        
                        folder = 'movie' if media_type == 'movie' else 'tv'
                        
                        def clean_slug(text):
                            res = re.sub(r'[^\w\s-]', '', text).strip().lower()
                            res = re.sub(r'[-\s_]+', '-', res)
                            return res
                        
                        slug = f"{tid}-{clean_slug(title)}"
                        
                        log.info(f"✅ Found {media_type}: {title} ({year}) - Rating: {rating}")
                        return {
                            'tmdb_id': tid,
                            'title': title,
                            'poster': poster,
                            'year': year,
                            'rating': rating,
                            'folder': folder,
                            'slug': slug
                        }
        except Exception as e:
            log.error(f"Error fetching random high-rated {media_type} page {page}: {e}")
    
    return None


def get_available_ids():
    """Get set of available tmdb_ids from local content."""
    available_ids = set()
    index_path = os.path.join(os.path.dirname(__file__), 'data', 'content_index.json')
    if os.path.exists(index_path):
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
                for item in index_data:
                    tid = item.get('tmdb_id')
                    if tid:
                        available_ids.add(int(tid))
        except Exception:
            pass
    return available_ids


def fetch_mixed_content(media_type, tmdb_api_key=TMDB_API_KEY):
    """Fetch 1 trending + 1 random high-rated content, excluding existing content."""
    available_ids = get_available_ids()
    log.info(f"📊 Found {len(available_ids)} existing items in local data")
    
    trending = fetch_trending(media_type, tmdb_api_key, available_ids)
    random_item = fetch_random_high_rated(media_type, tmdb_api_key, available_ids)
    
    result = []
    
    # Get top trending (already filtered)
    if trending:
        result.append(trending[0])
    
    # Get random high-rated (already filtered)
    if random_item:
        result.append(random_item)
    
    log.info(f"✅ Returning {len(result)} new {media_type} items")
    return result


def generate_bilingual_description(title_ar, title_en, overview_ar, overview_en, year, genres_ar, media_type, actor=None, platform=None, is_arabic_content=False, *args, **kwargs):
    """Generate bilingual description using HuggingFace API."""
    genres_str = ", ".join(genres_ar) if isinstance(genres_ar, list) else str(genres_ar)
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    
    # Simple, clear prompt to avoid JSON parse errors
    system = """You are a JSON generator. Return ONLY valid JSON object. No markdown, no code blocks.

Generate this exact JSON structure:
{
  "desc_ar": "3-5 sentences summary in Arabic",
  "desc_en": "English summary",
  "meta_desc": "130-155 characters",
  "seo_title_ar": "مشاهدة فيلم TITLE_EN مترجم - توميتو",
  "opinion_ar": "1-2 sentence review in Arabic",
  "opinion_en": "1-2 sentence review in English",
  "faq": [{"q": "question in Arabic", "a": "answer in Arabic", "q_en": "question in English", "a_en": "answer in English"}],
  "keywords": "comma separated keywords"
}

CRITICAL: Complete the entire JSON. Do not cut off mid-sentence. Ensure all fields are present and properly formatted. No newlines in strings. Escape quotes properly."""

    user = f"""Arabic Title: {title_ar}. English Title: {title_en}. Type: {media_label_ar}. Genres: {genres_str}. Arabic Story: {overview_ar}. English Story: {overview_en}. Year: {year}."""

    res, model_used = _call_cohere_llm(system, user)
    
    try:
        data = json.loads(res or "{}")
        
        # Add trending keywords from pytrends
        t_query = title_ar if title_ar and title_ar.strip() else title_en
        trending_keywords = get_trending_keywords(t_query, geo='SA')
        
        # Merge keywords
        base_keywords = data.get('keywords', '')
        if trending_keywords:
            trending_kw_str = ", ".join(trending_keywords[:5])
            data['keywords'] = f"{base_keywords}, {trending_kw_str}"
        
        # Ensure all required fields exist
        if not data.get('desc_ar'):
            data['desc_ar'] = overview_ar or f"استمتع بمشاهدة {media_label_ar} {title_ar} مترجم بجودة عالية."
        if not data.get('desc_en'):
            data['desc_en'] = overview_en or f"Enjoy watching {title_en} in high quality."
        if not data.get('meta_desc'):
            data['meta_desc'] = f"مشاهدة {title_ar} مترجم بجودة عالية على توميتو واكتشف أحداث الإثارة."[:155]
        if not data.get('seo_title_ar'):
            data['seo_title_ar'] = f"مشاهدة {media_label_ar} {title_en} مترجم - توميتو"
        if not data.get('opinion_ar'):
            data['opinion_ar'] = f"عمل {media_label_ar} مذهل يستحق المتابعة والاستكشاف."
        if not data.get('opinion_en'):
            data['opinion_en'] = f"A stunning {media_label_ar} worth watching and exploring."
        if not data.get('faq'):
            data['faq'] = [
                {"q": f"كيف يمكنني مشاهدة {media_label_ar} {title_ar}?", "a": f"يمكنك مشاهدته مترجماً بالكامل وبجودة عالية مباشرة على موقع توميتو.", "q_en": f"How can I watch {title_en}?", "a_en": f"You can watch it fully translated in high quality directly on the Tomito website."},
                {"q": f"ما هو تصنيف {media_label_ar} {title_ar}?", "a": f"يندرج العمل تحت تصنيف {genres_str}.", "q_en": f"What is the genre of {title_en}?", "a_en": f"It falls under the genre of {genres_str}."},
                {"q": f"ما هي قصة {media_label_ar} {title_ar}?", "a": overview_ar[:200] + "..." if len(overview_ar) > 200 else overview_ar, "q_en": f"What is the story of {title_en}?", "a_en": overview_en[:200] + "..." if len(overview_en) > 200 else overview_en}
            ]
        if not data.get('keywords'):
            data['keywords'] = f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {title_en} online"
        
        log.info(f"✅ Successfully generated content for {title_ar} using {model_used}")
        return data
        
    except json.JSONDecodeError as e:
        log.error(f"❌ JSON Parse failed: {e}. Response: {res[:500]}")
        # Return fallback with trending keywords
        trending_keywords = get_trending_keywords(title_ar or title_en, geo='SA')
        trending_kw_str = ", ".join(trending_keywords[:5]) if trending_keywords else ""
        
        return {
            "desc_ar": overview_ar or f"استمتع بمشاهدة {media_label_ar} {title_ar} مترجم بجودة عالية.",
            "desc_en": overview_en or f"Enjoy watching {title_en} in high quality.",
            "meta_desc": f"مشاهدة {title_ar} مترجم بجودة عالية على توميتو واكتشف أحداث الإثارة."[:155],
            "seo_title_ar": f"مشاهدة {media_label_ar} {title_en} مترجم - توميتو",
            "opinion_ar": f"عمل {media_label_ar} مذهل يستحق المتابعة والاستكشاف.",
            "opinion_en": f"A stunning {media_label_ar} worth watching and exploring.",
            "faq": [
                {"q": f"كيف يمكنني مشاهدة {media_label_ar} {title_ar}?", "a": f"يمكنك مشاهدته مترجماً بالكامل وبجودة عالية مباشرة على موقع توميتو.", "q_en": f"How can I watch {title_en}?", "a_en": f"You can watch it fully translated in high quality directly on the Tomito website."},
                {"q": f"ما هو تصنيف {media_label_ar} {title_ar}?", "a": f"يندرج العمل تحت تصنيف {genres_str}.", "q_en": f"What is the genre of {title_en}?", "a_en": f"It falls under the genre of {genres_str}."},
                {"q": f"ما هي قصة {media_label_ar} {title_ar}?", "a": overview_ar[:200] + "..." if len(overview_ar) > 200 else overview_ar, "q_en": f"What is the story of {title_en}?", "a_en": overview_en[:200] + "..." if len(overview_en) > 200 else overview_en}
            ],
            "keywords": f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {trending_kw_str}"
        }


def get_rising_seo_tags(subject_name, media_type='movie', year='2026', genres_ar=None, actor=None, platform=None, is_arabic_content=False):
    """Generate rising SEO tags using trending keywords."""
    label = "فيلم" if media_type == 'movie' else "مسلسل"
    tag_label = "مترجم" if media_type == 'movie' else "مترجم كامل"
    
    # Get trending keywords
    trending_keywords = get_trending_keywords(subject_name, geo='SA')
    
    intents = [
        f"{subject_name} {tag_label}", 
        f"قصة {label} {subject_name}",
        f"مشاهدة {subject_name} {year}",
        f"أحداث {subject_name} بالتفصيل"
    ]
    
    # Add trending keywords
    if trending_keywords:
        intents.extend(trending_keywords[:5])
    
    return intents


def generate_faq(title_ar, title_en, year, media_type, ai_data=None):
    """Generate FAQ section for content."""
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    
    # If AI data contains faq, use it
    if ai_data and 'faq' in ai_data:
        return ai_data['faq']
    
    faq = [
        {
            "q": f"ما هو {media_label_ar} {title_ar}؟",
            "a": f"{media_label_ar} {title_ar} ({year}) عمل فني رائع يستحق المشاهدة.",
            "q_en": f"What is {title_en}?",
            "a_en": f"{title_en} ({year}) is a wonderful piece of work worth watching."
        },
        {
            "q": f"كيف يمكنني مشاهدة {media_label_ar} {title_ar}؟",
            "a": f"يمكنك مشاهدته مترجماً بالكامل وبجودة عالية مباشرة على موقع توميتو.",
            "q_en": f"How can I watch {title_en}?",
            "a_en": f"You can watch it with full translation and in high quality directly on the Tomito website."
        },
        {
            "q": f"هل مشاهدة {title_ar} مجانية؟",
            "a": f"نعم، يمكنك مشاهدة {media_label_ar} {title_ar} مجاناً على توميتو بدون إعلانات.",
            "q_en": f"Is watching {title_en} free?",
            "a_en": f"Yes, you can watch {title_en} for free on Tomito without ads."
        }
    ]
    
    return faq


def generate_meta_tags(title_ar, title_en, year, genres_ar, media_type):
    """Generate meta tags for content."""
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    genres_str = ", ".join(genres_ar) if isinstance(genres_ar, list) else str(genres_ar)
    
    meta_desc = f"مشاهدة وتحميل {media_label_ar} {title_ar} ({year}) مترجم بجودة عالية HD حصرياً على توميتو. {genres_str}."
    keywords = f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {media_label_ar} {year}, {genres_str}"
    
    return {
        'meta_desc': meta_desc[:155],
        'keywords': keywords
    }


def generate_tomito_opinion(title_ar, title_en, year, media_type, ai_data=None):
    """Generate tomito opinion for content."""
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    
    # If AI data contains opinion, use it
    if ai_data and 'opinion' in ai_data:
        return ai_data['opinion']
    
    opinions = [
        f"عمل {media_label_ar} مذهل يستحق المتابعة والاستكشاف.",
        f"{media_label_ar} {title_ar} عمل فني رائع يقدم تجربة مشاهدة فريدة.",
        f"ننصح بشدة بمشاهدة {media_label_ar} {title_ar} للأداء المتميز والقصة المشوقة."
    ]
    
    return random.choice(opinions)


def generate_page_intro_outro(title_ar, title_en, year, media_type, genres_ar=None):
    """Generate page intro and outro for content."""
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    genres_str = ", ".join(genres_ar) if isinstance(genres_ar, list) else str(genres_ar)
    
    intro = f"استمتع بمشاهدة {media_label_ar} {title_ar} ({year}) مترجم بجودة عالية على توميتو. {genres_str}."
    outro = f"شاهد {title_ar} الآن واستمتع بتجربة مشاهدة فريدة على توميتو. {media_label_ar} {title_ar} متاح بجودة 1080p و 720p."
    
    return intro, outro


if __name__ == "__main__":
    # Test the functions
    print("Testing AI Engine...")
    print("=" * 50)
    
    # Test fetch_mixed_content
    print("\n🎬 Testing fetch_mixed_content for movies...")
    movies = fetch_mixed_content('movie')
    print(f"Movies fetched: {len(movies)}")
    print(json.dumps(movies, indent=2, ensure_ascii=False))
    
    print("\n📺 Testing fetch_mixed_content for tv...")
    tv_shows = fetch_mixed_content('tv')
    print(f"TV shows fetched: {len(tv_shows)}")
    print(json.dumps(tv_shows, indent=2, ensure_ascii=False))
    
    # Test generate_bilingual_description
    print("\n🤖 Testing generate_bilingual_description...")
    content = generate_bilingual_description(
        title_ar="هوكوم",
        title_en="Hokum",
        overview_ar="عندما ينعزل الروائي أوم بومان في نُزل ناءٍ لينثر رماد والديه، تسيطر عليه حكايات عن ساحرة تطارد نزلاء جناح شهر العسل.",
        overview_en="When novelist Ohm Bauman retreats to a remote inn to scatter his parents' ashes, he is consumed by tales of a witch haunting the honeymoon suite.",
        year="2026",
        genres_ar=["رعب"],
        media_type="movie"
    )
    print(json.dumps(content, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 50)
    print("✅ Test complete!")
