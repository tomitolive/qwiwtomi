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
    
    # Validate title_ar - if not Arabic or English, fallback to title_en
    if title_ar and not is_valid_title_ar(title_ar):
        log.warning(f"⚠️ title_ar '{title_ar}' is not Arabic or English. Falling back to title_en: '{title_en}'")
        title_ar = title_en
    
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
        
        data['desc_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data['desc_ar']))))
        data['desc_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('desc_en', '')))))
        data['meta_desc'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('meta_desc', '')))))
        data['seo_title_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('seo_title_ar', '')))))
        data['opinion_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('opinion_ar', '')))))
        data['opinion_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('opinion_en', '')))))
        data['keywords'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(data.get('keywords', '')))))

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
                faq_item['q'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_arabic_text(faq_item['q'])))))
            if 'a' in faq_item:
                faq_item['a'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_arabic_text(faq_item['a'])))))
            if 'q_en' in faq_item:
                faq_item['q_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_english_text(faq_item['q_en'])))))
            if 'a_en' in faq_item:
                faq_item['a_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(clean_english_text(faq_item['a_en'])))))

        if not data.get('keywords'):
            data['keywords'] = f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {title_en} online"
        data['keywords'] = clean_arabic_text(data['keywords'])
        
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
        fallback_data['desc_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['desc_ar']))))
        fallback_data['desc_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['desc_en']))))
        fallback_data['meta_desc'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['meta_desc']))))
        fallback_data['seo_title_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['seo_title_ar']))))
        fallback_data['opinion_ar'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['opinion_ar']))))
        fallback_data['opinion_en'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['opinion_en']))))
        fallback_data['keywords'] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(fallback_data['keywords']))))
        
        # Apply fix to FAQ
        for faq_item in fallback_data['faq']:
            for key in ['q', 'a', 'q_en', 'a_en']:
                if key in faq_item:
                    faq_item[key] = fix_el_cementerio_de_los_elefantes(fix_la_casa_de_los_famosos(fix_jack_joker(fix_attack_on_titan(faq_item[key]))))
        
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
