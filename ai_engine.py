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

# Load .env file manually
def load_env():
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        return True
    return False

load_env()

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

def is_arabic_text(text):
    """Check if text is primarily Arabic (not Hebrew, Cyrillic, Chinese, etc.)."""
    if not text:
        return False
    
    # Count Arabic characters (Unicode range U+0600-U+06FF)
    arabic_chars = len(re.findall(r'[\u0600-\u06FF]', text))
    
    # Count total non-whitespace characters
    total_chars = len(re.sub(r'\s', '', text))
    
    if total_chars == 0:
        return False
    
    # If more than 50% of characters are Arabic, consider it Arabic text
    arabic_ratio = arabic_chars / total_chars
    return arabic_ratio > 0.5

def is_english_text(text):
    """Check if text is primarily English (Latin letters)."""
    if not text:
        return False
    
    # Count Latin characters
    latin_chars = len(re.findall(r'[a-zA-Z]', text))
    
    # Count total non-whitespace characters
    total_chars = len(re.sub(r'\s', '', text))
    
    if total_chars == 0:
        return False
    
    # If more than 50% of characters are Latin, consider it English text
    latin_ratio = latin_chars / total_chars
    return latin_ratio > 0.5

def is_valid_title_ar(text):
    """Check if text is valid for title_ar (Arabic or English only, not Hebrew, Cyrillic, Chinese, etc.)."""
    if not text:
        return False
    
    # Check if Arabic
    if is_arabic_text(text):
        return True
    
    # Check if English (Latin letters only)
    # Remove spaces and check if remaining characters are Latin letters or basic punctuation
    clean_text = re.sub(r'[\s\-\'".,:;!?]', '', text)
    if clean_text and re.match(r'^[a-zA-Z0-9]+$', clean_text):
        return True
    
    return False

def is_adult_content(title, overview):
    """Check if content is adult/explicit based on title and overview."""
    if not title and not overview:
        return False
    
    # Adult content keywords to filter out (in English and Arabic)
    adult_keywords = [
        'porn', 'xxx', 'sex', 'erotic', 'adult', 'nude', 'naked', 'hardcore',
        'softcore', 'erotica', 'pornography', 'incest', 'taboo',
        'إباحي', 'جنس', 'عري', 'محظور', 'إغراء'
    ]
    
    text_to_check = f"{title or ''} {overview or ''}".lower()
    
    for keyword in adult_keywords:
        if keyword.lower() in text_to_check:
            log.warning(f"🚫 Adult content detected: '{keyword}' found in title/overview")
            return True
    
    return False

def clean_arabic_text(text):
    """Remove non-Arabic characters from Arabic text fields, but preserve English proper names."""
    if not text:
        return text
    # First, preserve proper names (capitalized English words)
    # This keeps titles like "Star City", "For All Mankind" etc.
    proper_names = re.findall(r'\b[A-Z][a-zA-Z]+\b', text)
    
    # Remove English letters except for proper names
    cleaned = re.sub(r'\b[a-z]+\b', '', text)  # Remove lowercase English words
    cleaned = re.sub(r'\b[A-Z](?![a-zA-Z])\b', '', cleaned)  # Remove single uppercase letters
    
    # Add back proper names
    for name in proper_names:
        if name not in cleaned:
            cleaned = cleaned + ' ' + name
    
    return cleaned.strip()

def clean_english_text(text):
    """Remove non-English characters from English text fields."""
    if not text:
        return text
    # Keep English letters, numbers, and basic punctuation
    # Remove Arabic letters and other non-English characters
    cleaned = re.sub(r'[\u0600-\u06FF]', '', text)
    return cleaned.strip()

# Country translation map
COUNTRIES_MAP = {
    'Thailand': 'تايلاند',
    'Japan': 'اليابان',
    'South Korea': 'كوريا الجنوبية',
    'France': 'فرنسا',
    'Germany': 'ألمانيا',
    'United States': 'الولايات المتحدة',
    'USA': 'الولايات المتحدة',
    'United States of America': 'الولايات المتحدة',
    'United Kingdom': 'المملكة المتحدة',
    'UK': 'المملكة المتحدة',
    'Italy': 'إيطاليا',
    'Spain': 'إسبانيا',
    'China': 'الصين',
    'India': 'الهند',
    'Brazil': 'البرازيل',
    'Mexico': 'المكسيك',
    'Canada': 'كندا',
    'Australia': 'أستراليا',
    'Russia': 'روسيا',
    'Turkey': 'تركيا',
    'Egypt': 'مصر',
    'Saudi Arabia': 'السعودية',
    'United Arab Emirates': 'الإمارات العربية المتحدة',
    'UAE': 'الإمارات العربية المتحدة',
    'Indonesia': 'إندونيسيا',
    'Philippines': 'الفلبين',
    'Vietnam': 'فيتنام',
    'Malaysia': 'ماليزيا',
    'Singapore': 'سنغافورة',
    'Hong Kong': 'هونغ كونغ',
    'Taiwan': 'تايوان',
    'Poland': 'بولندا',
    'Sweden': 'السويد',
    'Norway': 'النرويج',
    'Denmark': 'الدنمارك',
    'Netherlands': 'هولندا',
    'Belgium': 'بلجيكا',
    'Switzerland': 'سويسرا',
    'Austria': 'النمسا',
    'Czech Republic': 'جمهورية التشيك',
    'Czechoslovakia': 'تشيكوسلوفاكيا',
    'Hungary': 'المجر',
    'Romania': 'رومانيا',
    'Bulgaria': 'بلغاريا',
    'Greece': 'اليونان',
    'Portugal': 'البرتغال',
    'Argentina': 'الأرجنتين',
    'Colombia': 'كولومبيا',
    'Chile': 'تشيلي',
    'Peru': 'بيرو',
    'Bolivia': 'بوليفيا',
    'South Africa': 'جنوب أفريقيا',
    'Nigeria': 'نيجيريا',
    'Kenya': 'كينيا',
    'Morocco': 'المغرب',
    'Algeria': 'الجزائر',
    'Tunisia': 'تونس',
    'Libya': 'ليبيا',
    'Sudan': 'السودان',
    'Iraq': 'العراق',
    'Syria': 'سوريا',
    'Jordan': 'الأردن',
    'Lebanon': 'لبنان',
    'Kuwait': 'الكويت',
    'Qatar': 'قطر',
    'Bahrain': 'البحرين',
    'Oman': 'عمان',
    'Yemen': 'اليمن',
    'Pakistan': 'باكستان',
    'Bangladesh': 'بنغلاديش',
    'Sri Lanka': 'سريلانكا',
    'Nepal': 'نيبال',
    'Myanmar': 'ميانمار',
    'Cambodia': 'كمبوديا',
    'Laos': 'لاوس',
    'New Zealand': 'نيوزيلندا',
    'Ireland': 'أيرلندا',
    'Finland': 'فنلندا',
    'Iceland': 'آيسلندا',
    'Estonia': 'إستونيا',
    'Latvia': 'لاتفيا',
    'Lithuania': 'ليتوانيا',
    'Ukraine': 'أوكرانيا',
    'Belarus': 'بيلاروسيا',
    'Kazakhstan': 'كازاخستان',
    'Uzbekistan': 'أوزبكستان',
    'Afghanistan': 'أفغانستان',
    'Iran': 'إيران',
    'Israel': 'إسرائيل',
    'North Korea': 'كوريا الشمالية',
    'Mongolia': 'منغوليا',
    'Georgia': 'جورجيا',
    'Armenia': 'أرمينيا',
    'Azerbaijan': 'أذربيجان',
    'Cyprus': 'قبرص',
    'Malta': 'مالطا',
    'Luxembourg': 'لوكسمبورغ',
    'Monaco': 'موناكو',
    'San Marino': 'سان مارينو',
    'Vatican City': 'الفاتيكان',
    'Liechtenstein': 'ليختنشتاين',
    'Andorra': 'أندورا',
    'Croatia': 'كرواتيا',
    'Serbia': 'صربيا',
    'Bolivia': 'بوليفيا',
    'Dominican Republic': 'جمهورية الدومينيكان',
    'Soviet Union': 'الاتحاد السوفيتي',
    'Yugoslavia': 'يوغوسلافيا',
    'East Germany': 'ألمانيا الشرقية',
    'Aruba': 'أروبا',
}

# Bot missions for content generation
BOT_MISSIONS = [
    {
        "name": "Disney",
        "type": "company",
        "id": 2,
        "label": "Disney"
    },
    {
        "name": "Marvel Studios",
        "type": "company",
        "id": 420,
        "label": "Marvel"
    },
    {
        "name": "Netflix",
        "type": "company",
        "id": 213,
        "label": "Netflix"
    },
    {
        "name": "Warner Bros. Pictures",
        "type": "company",
        "id": 1743,
        "label": "Warner Bros"
    },
    {
        "name": "Universal Pictures",
        "type": "company",
        "id": 334,
        "label": "Universal"
    },
    {
        "name": "Paramount Pictures",
        "type": "company",
        "id": 45,
        "label": "Paramount"
    },
    {
        "name": "Sony Pictures",
        "type": "company",
        "id": 562,
        "label": "Sony"
    },
    {
        "name": "20th Century Studios",
        "type": "company",
        "id": 257,
        "label": "20th Century"
    },
    {
        "name": "Walt Disney Pictures",
        "type": "company",
        "id": 28,
        "label": "Disney Pictures"
    },
    {
        "name": "Apple TV+",
        "type": "company",
        "id": 25529,
        "label": "Apple TV"
    },
    {
        "name": "Amazon Studios",
        "type": "company",
        "id": 110810,
        "label": "Amazon"
    },
    {
        "name": "HBO",
        "type": "company",
        "id": 3268,
        "label": "HBO"
    },
    {
        "name": "Hulu",
        "type": "company",
        "id": 3560,
        "label": "Hulu"
    },
    {
        "name": "MGM",
        "type": "company",
        "id": 211,
        "label": "MGM"
    },
    {
        "name": "Lionsgate",
        "type": "company",
        "id": 1632,
        "label": "Lionsgate"
    },
    {
        "name": "A24",
        "type": "company",
        "id": 41077,
        "label": "A24"
    },
    {
        "name": "BBC",
        "type": "company",
        "id": 616,
        "label": "BBC"
    },
    {
        "name": "Canal+",
        "type": "company",
        "id": 3101,
        "label": "Canal+"
    },
    {
        "name": "Blumhouse",
        "type": "company",
        "id": 3172,
        "label": "Blumhouse"
    },
    {
        "name": "Bad Robot",
        "type": "company",
        "id": 11461,
        "label": "Bad Robot"
    },
    {
        "name": "Legendary Pictures",
        "type": "company",
        "id": 923,
        "label": "Legendary"
    },
    {
        "name": "Amblin Entertainment",
        "type": "company",
        "id": 56,
        "label": "Amblin"
    },
    {
        "name": "Action",
        "type": "genre",
        "id": 28,
        "label": "Action"
    },
    {
        "name": "Drama",
        "type": "genre",
        "id": 18,
        "label": "Drama"
    },
    {
        "name": "Comedy",
        "type": "genre",
        "id": 35,
        "label": "Comedy"
    },
    {
        "name": "Horror",
        "type": "genre",
        "id": 27,
        "label": "Horror"
    },
    {
        "name": "Sci-Fi",
        "type": "genre",
        "id": 878,
        "label": "Sci-Fi"
    },
    {
        "name": "Trending",
        "type": "trending",
        "id": None,
        "label": "Trending"
    }
]

# Cohere Models Configuration
COHERE_MODELS = [
    {
        "name": "command-r-08-2024",
        "model_id": "command-r-08-2024",
        "api_key": os.getenv("COHERE_API_KEY")
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
        
        # Also try rising queries for additional keywords
        if query in related_queries and 'rising' in related_queries[query]:
            rising_queries = related_queries[query]['rising']
            if rising_queries is not None and not rising_queries.empty:
                rising_keywords = rising_queries['query'].head(5).tolist()
                keywords.extend(rising_keywords)
        
        # Remove duplicates and limit to 15
        keywords = list(dict.fromkeys(keywords))[:15]
        
        log.info(f"🔍 Found {len(keywords)} trending keywords for '{query}' in {geo}")
        return keywords
        
    except Exception as e:
        log.error(f"❌ Error fetching trending keywords: {e}")
        return []


def fetch_trending(media_type, tmdb_api_key=TMDB_API_KEY, available_ids=None):
    """Fetch trending content from TMDB (US region), excluding existing content, LGBTQ+, and adult content."""
    available_ids = available_ids or set()
    log.info(f"🔥 Fetching trending {media_type} (US region)...")
    
    # Common LGBTQ+ keyword IDs on TMDB to exclude
    lgbt_keywords = "210024,9799,10769,158718,10850,3656,11466,10777,10886,161176,145330"
    
    # Adult content genre IDs to exclude (Adult, Erotica)
    adult_genres = "299697,299696"
    
    endpoint = "discover/movie" if media_type == 'movie' else "discover/tv"

    trends = []
    
    # Loop up to 10 pages to ensure we find new content
    for page in range(1, 11):
        params = {
            'api_key': tmdb_api_key,
            'region': 'US',
            'page': page,
            'sort_by': 'popularity.desc',
            'without_keywords': lgbt_keywords,
            'without_genres': adult_genres,
            'include_adult': 'false'
        }
        
        try:
            response = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    for item in data['results']:
                        tid = item.get('id')
                        # Skip if already exists
                        if tid in available_ids:
                            continue
                        
                        title = item.get('title') or item.get('name')
                        overview = item.get('overview', '')
                        
                        # Check for adult content
                        if is_adult_content(title, overview):
                            log.warning(f"🚫 Skipping adult content: {title} (ID: {tid})")
                            continue
                        
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
                        
                        # Return immediately once we find enough new trends
                        if len(trends) >= 3:
                            log.info(f"✅ Found new trending {media_type} (excluding existing & LGBTQ+)")
                            return trends
        except Exception as e:
            log.error(f"Error fetching trending {media_type} page {page}: {e}")
            
    if trends:
        return trends

    log.warning(f"⚠️ All trending {media_type} (up to page 10) already exist in local data")
    return []


def fetch_random_high_rated(media_type, tmdb_api_key=TMDB_API_KEY, available_ids=None):
    """Fetch one random movie/tv with rating >= 7, excluding existing content, LGBTQ+, and adult content."""
    available_ids = available_ids or set()
    log.info(f"🎲 Fetching random high-rated {media_type} (rating >= 7)...")
    
    endpoint = "discover/movie" if media_type == 'movie' else "discover/tv"
    
    # Common LGBTQ+ keyword IDs on TMDB to exclude
    lgbt_keywords = "210024,9799,10769,158718,10850,3656,11466,10777,10886,161176,145330"
    
    # Adult content genre IDs to exclude (Adult, Erotica)
    adult_genres = "299697,299696"
    
    # Try random pages for infinite variety
    pages_to_try = random.sample(range(1, 100), 10)
    for page in pages_to_try:
        params = {
            'api_key': tmdb_api_key,
            'vote_average.gte': 7,
            'vote_count.gte': 200,
            'sort_by': 'vote_average.desc',
            'page': page,
            'without_keywords': lgbt_keywords,
            'without_genres': adult_genres,
            'include_adult': 'false'
        }
        
        try:
            response = requests.get(f"{TMDB_BASE_URL}/{endpoint}", params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and len(data['results']) > 0:
                    results = data['results']
                    # Filter out existing content
                    filtered = [r for r in results if r.get('id') not in available_ids]
                    
                    if filtered:
                        item = random.choice(filtered)
                        
                        tid = item.get('id')
                        title = item.get('title') or item.get('name')
                        overview = item.get('overview', '')
                        
                        # Check for adult content
                        if is_adult_content(title, overview):
                            log.warning(f"🚫 Skipping adult content: {title} (ID: {tid})")
                            continue
                        
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
    """Fetch content using rotating TMDB endpoints (now_playing, top_rated, popular, trending, etc.)."""
    available_ids = get_available_ids()
    log.info(f"📊 Found {len(available_ids)} existing items in local data")
    
    # Define endpoints for rotation
    if media_type == 'movie':
        endpoints_group1 = [
            ('now_playing', 'now_playing'),
            ('top_rated', 'top_rated'),
            ('popular', 'popular'),
            ('trending', 'trending/day')
        ]
        endpoints_group2 = [
            ('trending', 'trending/week'),
            ('upcoming', 'upcoming'),
            ('popular', 'popular'),
            ('top_rated', 'top_rated')
        ]
    else:  # tv
        endpoints_group1 = [
            ('airing_today', 'airing_today'),
            ('top_rated', 'top_rated'),
            ('popular', 'popular'),
            ('trending', 'trending/day')
        ]
        endpoints_group2 = [
            ('on_the_air', 'on_the_air'),
            ('trending', 'trending/week'),
            ('popular', 'popular'),
            ('top_rated', 'top_rated')
        ]
    
    # Rotate between groups based on time (every 30 minutes)
    import time
    current_time = int(time.time())
    use_group1 = (current_time // 1800) % 2 == 0  # Switch every 30 minutes
    
    endpoints = endpoints_group1 if use_group1 else endpoints_group2
    log.info(f"🔄 Using endpoint group: {'Group 1' if use_group1 else 'Group 2'}")
    
    result = []
    
    # Fetch from each endpoint in the group
    for endpoint_type, endpoint_path in endpoints:
        items = fetch_from_endpoint(media_type, endpoint_type, endpoint_path, tmdb_api_key, available_ids)
        if items:
            result.extend(items)
            if len(result) >= 3:  # Get up to 3 items per media type
                break
    
    # Deduplicate by tmdb_id
    seen_ids = set()
    unique_result = []
    for item in result:
        if item['tmdb_id'] not in seen_ids:
            seen_ids.add(item['tmdb_id'])
            unique_result.append(item)
    
    log.info(f"✅ Returning {len(unique_result)} new {media_type} items")
    return unique_result


def fetch_from_endpoint(media_type, endpoint_type, endpoint_path, tmdb_api_key, available_ids):
    """Fetch content from a specific TMDB endpoint."""
    available_ids = available_ids or set()
    log.info(f"🔍 Fetching from {endpoint_type} ({endpoint_path}) for {media_type}...")
    
    # Adult content filters
    lgbt_keywords = "210024,9799,10769,158718,10850,3656,11466,10777,10886,161176,145330"
    adult_genres = "299697,299696"
    
    items = []
    
    # Try up to 3 pages
    for page in range(1, 4):
        if endpoint_type == 'trending':
            url = f"{TMDB_BASE_URL}/trending/{media_type}/{endpoint_path.split('/')[1]}"
            params = {
                'api_key': tmdb_api_key,
                'page': page
            }
        else:
            url = f"{TMDB_BASE_URL}/{media_type}/{endpoint_type}"
            params = {
                'api_key': tmdb_api_key,
                'page': page,
                'without_keywords': lgbt_keywords,
                'without_genres': adult_genres,
                'include_adult': 'false'
            }
        
        try:
            response = requests.get(url, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                for item in results:
                    tid = item.get('id')
                    if tid in available_ids:
                        continue
                    
                    title = item.get('title') or item.get('name')
                    overview = item.get('overview', '')
                    
                    # Check for adult content
                    if is_adult_content(title, overview):
                        log.warning(f"🚫 Skipping adult content: {title} (ID: {tid})")
                        continue
                    
                    poster = item.get('poster_path')
                    year = (item.get('release_date') or item.get('first_air_date') or "")[:4]
                    rating = round(item.get('vote_average', 0), 1)
                    
                    folder = 'movie' if media_type == 'movie' else 'tv'
                    
                    def clean_slug(text):
                        res = re.sub(r'[^\w\s-]', '', text).strip().lower()
                        res = re.sub(r'[-\s_]+', '-', res)
                        return res
                    
                    slug = f"{tid}-{clean_slug(title)}"
                    
                    items.append({
                        'tmdb_id': tid,
                        'title': title,
                        'poster': poster,
                        'year': year,
                        'rating': rating,
                        'folder': folder,
                        'slug': slug
                    })
                    
                    if len(items) >= 2:
                        log.info(f"✅ Found {len(items)} items from {endpoint_type}")
                        return items
                        
        except Exception as e:
            log.error(f"Error fetching from {endpoint_type} page {page}: {e}")
    
    return items


def generate_bilingual_description(title_ar, title_en, overview_ar, overview_en, year, genres_ar, media_type, actor=None, platform=None, is_arabic_content=False, *args, **kwargs):
    """Generate bilingual description using HuggingFace API."""
    genres_str = ", ".join(genres_ar) if isinstance(genres_ar, list) else str(genres_ar)
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    
    # Validate title_ar - if not Arabic or English, fallback to title_en
    if title_ar and not is_valid_title_ar(title_ar):
        log.warning(f"⚠️ title_ar '{title_ar}' is not Arabic or English. Falling back to title_en: '{title_en}'")
        title_ar = title_en
    
    # If title_ar is the same as title_en (both English), translate title_ar to Arabic
    if title_ar == title_en and is_english_text(title_ar):
        log.info(f"🔄 Translating title_ar from English to Arabic: '{title_en}'")
        try:
            from googletrans import Translator
            translator = Translator()
            translated = translator.translate(title_en, src='en', dest='ar')
            if translated and translated.text:
                title_ar = translated.text
                log.info(f"✅ Translated to: '{title_ar}'")
        except Exception as e:
            log.warning(f"⚠️ Could not translate title_ar: {e}")
    
    # Simple, clear prompt to avoid JSON parse errors
    system = """You are a JSON generator. Return ONLY valid JSON object. No markdown, no code blocks.

Generate this exact JSON structure:
{
  "desc_ar": "3-5 sentences summary in Arabic - MUST include the Arabic Title and English Title in the text",
  "desc_en": "English summary - MUST include the English Title in the text",
  "meta_desc": "130-155 characters - MUST include the title",
  "seo_title_ar": "مشاهدة [TYPE] [TITLE_EN] مترجم - توميتو",
  "opinion_ar": "1-2 sentence review in Arabic - MUST include the title",
  "opinion_en": "1-2 sentence review in English - MUST include the title",
  "faq": [{"q": "question in Arabic with title", "a": "answer in Arabic", "q_en": "question in English with title", "a_en": "answer in English"}],
  "keywords": "comma separated keywords without leading comma"
}

CRITICAL INSTRUCTIONS:
1. You MUST use the provided Arabic Title and English Title in ALL text fields (desc_ar, desc_en, meta_desc, seo_title_ar, opinion_ar, opinion_en, faq).
2. Do NOT leave empty spaces or placeholders. Always include the actual titles.
3. Complete the entire JSON. Do not cut off mid-sentence.
4. Ensure all fields are present and properly formatted.
5. No newlines in strings. Escape quotes properly.
6. Keywords must NOT start with a comma.
7. IMPORTANT: Do NOT delete any part of the title, including prepositions like "de", "los", "de los", "la", "el", "las", "en". Always use the FULL title exactly as provided."""

    user = f"""Arabic Title: {title_ar}. English Title: {title_en}. Type: {media_label_ar}. Genres: {genres_str}. Arabic Story: {overview_ar}. English Story: {overview_en}. Year: {year}.

IMPORTANT: You MUST use "{title_ar}" and "{title_en}" in your generated content. Do not leave empty spaces."""

    res, model_used = _call_cohere_llm(system, user)
    
    try:
        data = json.loads(res or "{}")
        
        # Add trending keywords from pytrends
        t_query = title_ar if title_ar and title_ar.strip() else title_en
        trending_keywords = get_trending_keywords(t_query, geo='SA')
        
        # Merge keywords - use more trending keywords (up to 10)
        base_keywords = data.get('keywords', '')
        if trending_keywords:
            trending_kw_str = ", ".join(trending_keywords[:10])
            data['keywords'] = f"{base_keywords}, {trending_kw_str}"
        
        # Ensure all required fields exist and clean them
        if not data.get('desc_ar'):
            data['desc_ar'] = overview_ar or f"استمتع بمشاهدة {media_label_ar} {title_ar} مترجم بجودة عالية."
        data['desc_ar'] = clean_arabic_text(data['desc_ar'])
        
        # Fix "Attack Titan" -> "Attack on Titan" in all fields
        def fix_attack_on_titan(text):
            if not text:
                return text
            return re.sub(r'Attack\s+Titan', 'Attack on Titan', text)
        
        # Fix "Jack Joker:  Steal" -> "Jack Joker: U Steal"
        def fix_jack_joker(text):
            if not text:
                return text
            return re.sub(r'Jack Joker:\s+Steal', 'Jack Joker: U Steal', text)
        
        # Fix "La Casa   Famosos" -> "La Casa de los Famosos"
        def fix_la_casa_de_los_famosos(text):
            if not text:
                return text
            return re.sub(r'La Casa\s+Famosos', 'La Casa de los Famosos', text)
        
        # Fix "El Cementerio   Elefantes" -> "El Cementerio de los Elefantes"
        def fix_el_cementerio_de_los_elefantes(text):
            if not text:
                return text
            return re.sub(r'El Cementerio\s+Elefantes', 'El Cementerio de los Elefantes', text)
        
        # Fix "Scooby-Doos  Nutcracker Scoob" -> "Scooby-Doos A Nutcracker Scoob"
        def fix_scooby_doos_a_nutcracker_scoob(text):
            if not text:
                return text
            return re.sub(r'Scooby-Doos\s+Nutcracker Scoob', 'Scooby-Doos A Nutcracker Scoob', text)
        
        data['desc_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data['desc_ar'])))))
        data['desc_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('desc_en', ''))))))
        data['meta_desc'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('meta_desc', ''))))))
        data['seo_title_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('seo_title_ar', ''))))))
        data['opinion_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('opinion_ar', ''))))))
        data['opinion_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('opinion_en', ''))))))
        data['keywords'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('keywords', ''))))))

        if not data.get('desc_en'):
            data['desc_en'] = overview_en or f"Enjoy watching {title_en} in high quality."
        data['desc_en'] = clean_english_text(data['desc_en'])

        if not data.get('meta_desc'):
            data['meta_desc'] = f"مشاهدة {title_ar} مترجم بجودة عالية على توميتو واكتشف أحداث الإثارة."[:155]
        data['meta_desc'] = clean_arabic_text(data['meta_desc'])

        if not data.get('seo_title_ar'):
            data['seo_title_ar'] = f"مشاهدة {media_label_ar} {title_en} مترجم - توميتو"
        data['seo_title_ar'] = clean_arabic_text(data['seo_title_ar'])

        if not data.get('opinion_ar'):
            data['opinion_ar'] = f"عمل {media_label_ar} مذهل يستحق المتابعة والاستكشاف."
        data['opinion_ar'] = clean_arabic_text(data['opinion_ar'])

        if not data.get('opinion_en'):
            data['opinion_en'] = f"A stunning {media_label_ar} worth watching and exploring."
        data['opinion_en'] = clean_english_text(data['opinion_en'])

        if not data.get('faq'):
            data['faq'] = [
                {"q": f"كيف يمكنني مشاهدة {media_label_ar} {title_ar}?", "a": f"يمكنك مشاهدته مترجماً بالكامل وبجودة عالية مباشرة على موقع توميتو.", "q_en": f"How can I watch {title_en}?", "a_en": f"You can watch it fully translated in high quality directly on the Tomito website."},
                {"q": f"ما هو تصنيف {media_label_ar} {title_ar}?", "a": f"يندرج العمل تحت تصنيف {genres_str}.", "q_en": f"What is the genre of {title_en}?", "a_en": f"It falls under the genre of {genres_str}."},
                {"q": f"ما هي قصة {media_label_ar} {title_ar}?", "a": overview_ar[:200] + "..." if len(overview_ar) > 200 else overview_ar, "q_en": f"What is the story of {title_en}?", "a_en": overview_en[:200] + "..." if len(overview_en) > 200 else overview_en}
            ]
        # Clean FAQ fields
        for faq_item in data['faq']:
            if 'q' in faq_item:
                faq_item['q'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_arabic_text(faq_item['q']))))))
            if 'a' in faq_item:
                faq_item['a'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_arabic_text(faq_item['a']))))))
            if 'q_en' in faq_item:
                faq_item['q_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_english_text(faq_item['q_en']))))))
            if 'a_en' in faq_item:
                faq_item['a_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_english_text(faq_item['a_en']))))))

        if not data.get('keywords'):
            data['keywords'] = f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {title_en} online"
        data['keywords'] = clean_arabic_text(data['keywords'])
        
        # Clean keywords: remove empty placeholders and extra spaces
        def clean_keywords(text):
            if not text:
                return text
            # Split by comma, strip each part, filter empty strings, join back
            parts = [k.strip() for k in text.split(',') if k.strip()]
            return ', '.join(parts)
        
        data['keywords'] = clean_keywords(data['keywords'])
        
        # Validation: Check if title is present in all fields
        def validate_title_in_content(data, title_en):
            """Validate that the title is present in all content fields."""
            fields = ['desc_ar', 'opinion_ar', 'seo_title_ar', 'meta_desc', 'keywords']
            missing_fields = []
            
            for field in fields:
                content = data.get(field, '')
                # Check if full title is present or at least the first word
                if title_en not in content and title_en.split()[0] not in content:
                    missing_fields.append(field)
            
            if missing_fields:
                log.warning(f"⚠️ Title '{title_en}' missing from fields: {', '.join(missing_fields)}")
            
            return len(missing_fields) == 0
        
        validate_title_in_content(data, title_en)
        
        # Validation: Check for empty placeholders and malformed output
        def has_empty_placeholders(text):
            if not text:
                return True
            # Check for patterns like "  ," or "  ." (double spaces with punctuation)
            if re.search(r'\s{2,}[,.]', text):
                return True
            # Check for patterns like "عالم  ، حيث" (space, Arabic comma, space)
            if re.search(r'\s+،\s+', text):
                return True
            # Check for just ": - , ." or similar
            if re.match(r'^[:\-,\s\.]+$', text):
                return True
            return False
        
        # Validate and fix meta_desc
        if has_empty_placeholders(data.get('meta_desc', '')):
            data['meta_desc'] = f"مشاهدة {title_ar} مترجم بجودة عالية على توميتو واكتشف أحداث الإثارة."[:155]
            data['meta_desc'] = clean_arabic_text(data['meta_desc'])
        
        # Validate and fix desc_ar
        if has_empty_placeholders(data.get('desc_ar', '')):
            data['desc_ar'] = overview_ar or f"استمتع بمشاهدة {media_label_ar} {title_ar} مترجم بجودة عالية."
            data['desc_ar'] = clean_arabic_text(data['desc_ar'])
        
        # Validate and fix desc_en
        if has_empty_placeholders(data.get('desc_en', '')):
            data['desc_en'] = overview_en or f"Enjoy watching {title_en} in high quality."
            data['desc_en'] = clean_english_text(data['desc_en'])
        
        # Validate and fix opinion_ar
        if has_empty_placeholders(data.get('opinion_ar', '')):
            data['opinion_ar'] = f"عمل {media_label_ar} مذهل يستحق المتابعة والاستكشاف."
            data['opinion_ar'] = clean_arabic_text(data['opinion_ar'])
        
        # Validate and fix opinion_en
        if has_empty_placeholders(data.get('opinion_en', '')):
            data['opinion_en'] = f"A stunning {media_label_ar} worth watching and exploring."
            data['opinion_en'] = clean_english_text(data['opinion_en'])
        
        # Validate and fix keywords (remove leading comma)
        if data.get('keywords', '').startswith(','):
            data['keywords'] = data['keywords'][1:].strip()
        
        # Validate FAQ fields
        for faq_item in data.get('faq', []):
            for key in ['q', 'a', 'q_en', 'a_en']:
                if key in faq_item and has_empty_placeholders(faq_item[key]):
                    if key == 'q':
                        faq_item[key] = f"سؤال عن {title_ar}"
                    elif key == 'a':
                        faq_item[key] = f"إجابة عن {title_ar}"
                    elif key == 'q_en':
                        faq_item[key] = f"Question about {title_en}"
                    elif key == 'a_en':
                        faq_item[key] = f"Answer about {title_en}"
        
        log.info(f"✅ Successfully generated content for {title_ar} using {model_used}")
        return data
        
    except json.JSONDecodeError as e:
        log.error(f"❌ JSON Parse failed: {e}. Response: {res[:500]}")
        # Return fallback with trending keywords
        trending_keywords = get_trending_keywords(title_ar or title_en, geo='SA')
        trending_kw_str = ", ".join(trending_keywords[:5]) if trending_keywords else ""
        
        # Fix "Attack Titan" -> "Attack on Titan" in fallback
        def fix_attack_on_titan(text):
            if not text:
                return text
            return re.sub(r'Attack\s+Titan', 'Attack on Titan', text)
        
        # Fix "Jack Joker:  Steal" -> "Jack Joker: U Steal"
        def fix_jack_joker(text):
            if not text:
                return text
            return re.sub(r'Jack Joker:\s+Steal', 'Jack Joker: U Steal', text)
        
        # Fix "La Casa   Famosos" -> "La Casa de los Famosos"
        def fix_la_casa_de_los_famosos(text):
            if not text:
                return text
            return re.sub(r'La Casa\s+Famosos', 'La Casa de los Famosos', text)
        
        # Fix "El Cementerio   Elefantes" -> "El Cementerio de los Elefantes"
        def fix_el_cementerio_de_los_elefantes(text):
            if not text:
                return text
            return re.sub(r'El Cementerio\s+Elefantes', 'El Cementerio de los Elefantes', text)
        
        # Fix "Scooby-Doos  Nutcracker Scoob" -> "Scooby-Doos A Nutcracker Scoob"
        def fix_scooby_doos_a_nutcracker_scoob(text):
            if not text:
                return text
            return re.sub(r'Scooby-Doos\s+Nutcracker Scoob', 'Scooby-Doos A Nutcracker Scoob', text)
        
        fallback_data = {
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
        
        # Apply fix to all fields
        fallback_data['desc_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['desc_ar'])))))
        fallback_data['desc_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['desc_en'])))))
        fallback_data['meta_desc'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['meta_desc'])))))
        fallback_data['seo_title_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['seo_title_ar'])))))
        fallback_data['opinion_ar'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['opinion_ar'])))))
        fallback_data['opinion_en'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['opinion_en'])))))
        fallback_data['keywords'] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['keywords'])))))
        
        # Apply fix to FAQ
        for faq_item in fallback_data['faq']:
            for key in ['q', 'a', 'q_en', 'a_en']:
                if key in faq_item:
                    faq_item[key] = fix_scooby_doos_a_nutcracker_scoob(fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(faq_item[key])))))
        
        return fallback_data


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
