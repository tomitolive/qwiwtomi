import json
import os
import requests
from pathlib import Path

TMDB_API_KEY = "882e741f7283dc9ba1654d4692ec30f6"
BASE_URL = "https://api.themoviedb.org/3"
CONTENT_DIR = Path("data/content")

# Country mapping for Arabic names
COUNTRY_MAP = {
    'US': 'الولايات المتحدة الأمريكية',
    'GB': 'المملكة المتحدة',
    'FR': 'فرنسا',
    'DE': 'ألمانيا',
    'IT': 'إيطاليا',
    'ES': 'إسبانيا',
    'JP': 'اليابان',
    'KR': 'كوريا الجنوبية',
    'CN': 'الصين',
    'IN': 'الهند',
    'CA': 'كندا',
    'AU': 'أستراليا',
    'BR': 'البرازيل',
    'MX': 'المكسيك',
    'RU': 'روسيا',
    'TR': 'تركيا',
    'SA': 'السعودية',
    'EG': 'مصر',
    'MA': 'المغرب',
    'DZ': 'الجزائر',
    'TN': 'تونس',
}

# Language mapping for Arabic names
LANGUAGE_MAP = {
    'en': 'الإنجليزية',
    'fr': 'الفرنسية',
    'de': 'الألمانية',
    'es': 'الإسبانية',
    'it': 'الإيطالية',
    'ja': 'اليابانية',
    'ko': 'الكورية',
    'zh': 'الصينية',
    'hi': 'الهندية',
    'ar': 'العربية',
    'ru': 'الروسية',
    'tr': 'التركية',
    'pt': 'البرتغالية',
    'th': 'التايلاندية',
    'vi': 'الفيتنامية',
    'id': 'الإندونيسية',
}

def get_tmdb_data(endpoint, params=None):
    """Fetch data from TMDB API"""
    url = f"{BASE_URL}/{endpoint}"
    params = params or {}
    params['api_key'] = TMDB_API_KEY
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching {endpoint}: {e}")
        return None

def update_movie_details():
    """Update all movie JSON files with real details from TMDB"""
    
    if not CONTENT_DIR.exists():
        print(f"Content directory not found: {CONTENT_DIR}")
        return
    
    json_files = list(CONTENT_DIR.glob("*.json"))
    print(f"Found {len(json_files)} JSON files to update")
    
    for i, json_file in enumerate(json_files, 1):
        print(f"[{i}/{len(json_files)}] Processing {json_file.name}")
        
        try:
            # Read existing JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            movie_id = data.get('id')
            if not movie_id:
                print(f"  Skipping: No ID found")
                continue
            
            # Fetch movie details from TMDB
            tmdb_data = get_tmdb_data(f"movie/{movie_id}")
            if not tmdb_data:
                print(f"  Skipping: Failed to fetch TMDB data")
                continue
            
            # Extract real details
            # Duration
            if tmdb_data.get('runtime'):
                data['duration'] = f"{tmdb_data['runtime']} دقيقة"
            
            # Language
            original_language = tmdb_data.get('original_language')
            if original_language:
                data['language'] = LANGUAGE_MAP.get(original_language, original_language)
            
            # Country
            production_countries = tmdb_data.get('production_countries', [])
            if production_countries:
                iso_code = production_countries[0].get('iso_3166_1')
                if iso_code:
                    data['country'] = COUNTRY_MAP.get(iso_code, production_countries[0].get('name', iso_code))
            
            # Cast (top 5 actors)
            credits = get_tmdb_data(f"movie/{movie_id}/credits")
            if credits and credits.get('cast'):
                cast_names = [actor['name'] for actor in credits['cast'][:5]]
                data['cast'] = ' '.join(cast_names)
            
            # Quality (default)
            if not data.get('quality'):
                data['quality'] = '1080p BluRay'
            
            # Section (default)
            if not data.get('section'):
                data['section'] = 'أفلام أجنبية'
            
            # Write updated JSON
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            print(f"  ✓ Updated successfully")
            
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    print("\n✓ All files processed successfully!")

if __name__ == "__main__":
    update_movie_details()
