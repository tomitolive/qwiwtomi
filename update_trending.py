#!/usr/bin/env python3
import os
import json
import requests
import logging
import re
import random

# --- Configuration ---
TMDB_API_KEY = (os.environ.get("TMDB_API_KEY") or "882e741f7283dc9ba1654d4692ec30f6").strip()
BASE_URL = "https://api.themoviedb.org/3"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
BASE_PATH = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

def get_tmdb_data(endpoint, params={}):
    params['api_key'] = TMDB_API_KEY
    try:
        response = requests.get(f"{BASE_URL}/{endpoint}", params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        log.error(f"TMDB API Error {response.status_code}: {response.text}")
    except Exception as e:
        log.error(f"Error fetching from TMDB: {e}")
    return None

def fetch_trending(media_type):
    log.info(f"🔥 Fetching trending {media_type} (US region)...")
    data = get_tmdb_data(f"trending/{media_type}/day", {'region': 'US'})
    if not data or 'results' not in data:
        return []
    
    trends = []
    for item in data['results'][:20]:
        tid = item.get('id')
        title = item.get('title') or item.get('name')
        poster = f"{IMAGE_BASE_URL}{item.get('poster_path')}" if item.get('poster_path') else None
        year = (item.get('release_date') or item.get('first_air_date') or "")[:4]
        rating = round(item.get('vote_average', 0), 1)
        
        # Determine folder and slug
        folder = 'movie' if media_type == 'movie' else 'tv'
        
        # Heuristic slug (should ideally match create_page logic)
        import re
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
    return trends

def fetch_random_high_rated(media_type):
    """Fetch one random movie/tv with rating >= 7"""
    log.info(f"🎲 Fetching random high-rated {media_type} (rating >= 7)...")
    
    # Use discover endpoint to get random high-rated content
    endpoint = "discover/movie" if media_type == 'movie' else "discover/tv"
    params = {
        'vote_average.gte': 7,
        'vote_count.gte': 100,
        'sort_by': 'popularity.desc',
        'page': 1
    }
    
    data = get_tmdb_data(endpoint, params)
    if not data or 'results' not in data:
        return None
    
    # Pick a random item from the results
    import random
    results = data['results'][:20]
    item = random.choice(results)
    
    tid = item.get('id')
    title = item.get('title') or item.get('name')
    poster = f"{IMAGE_BASE_URL}{item.get('poster_path')}" if item.get('poster_path') else None
    year = (item.get('release_date') or item.get('first_air_date') or "")[:4]
    rating = round(item.get('vote_average', 0), 1)
    
    folder = 'movie' if media_type == 'movie' else 'tv'
    
    def clean_slug(text):
        res = re.sub(r'[^\w\s-]', '', text).strip().lower()
        res = re.sub(r'[-\s_]+', '-', res)
        return res
    
    slug = f"{tid}-{clean_slug(title)}"
    
    return {
        'tmdb_id': tid,
        'title': title,
        'poster': poster,
        'year': year,
        'rating': rating,
        'folder': folder,
        'slug': slug
    }

def main():
    # Fetch 1 trending movie + 1 random high-rated movie
    trending_movies = fetch_trending('movie')
    random_movie = fetch_random_high_rated('movie')
    
    # Fetch 1 trending tv + 1 random high-rated tv
    trending_tv = fetch_trending('tv')
    random_tv = fetch_random_high_rated('tv')
    
    # Combine: 1 trending + 1 random for each type
    movies = []
    if trending_movies:
        movies.append(trending_movies[0])  # Top trending movie
    if random_movie:
        movies.append(random_movie)  # Random high-rated movie
    
    tv_shows = []
    if trending_tv:
        tv_shows.append(trending_tv[0])  # Top trending tv
    if random_tv:
        tv_shows.append(random_tv)  # Random high-rated tv
    
    os.makedirs(os.path.join(BASE_PATH, 'data'), exist_ok=True)
    
    with open(os.path.join(BASE_PATH, 'data', 'trend_movies.json'), 'w', encoding='utf-8') as f:
        json.dump(movies, f, ensure_ascii=False, indent=2)
        
    with open(os.path.join(BASE_PATH, 'data', 'trend_tv.json'), 'w', encoding='utf-8') as f:
        json.dump(tv_shows, f, ensure_ascii=False, indent=2)
        
    log.info("✅ Trending data updated successfully (1 trending + 1 random high-rated per type).")

if __name__ == "__main__":
    main()
