#!/usr/bin/env python3
import os
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

# Genre name mappings
GENRE_NAMES = {
    "action": {"name": "Action", "name_ar": "أكشن", "description": "أفلام ومسلسلات الأكشن المثيرة مليئة بالحركة والتشويق"},
    "adventure": {"name": "Adventure", "name_ar": "مغامرة", "description": "أفلام ومسلسلات المغامرة المليئة بالاكتشافات والرحلات"},
    "animation": {"name": "Animation", "name_ar": "أنمي", "description": "أفلام ومسلسلات الأنمي والرسوم المتحركة"},
    "comedy": {"name": "Comedy", "name_ar": "كوميديا", "description": "أفلام ومسلسلات الكوميديا المضحكة"},
    "crime": {"name": "Crime", "name_ar": "جريمة", "description": "أفلام ومسلسلات الجريمة والتحقيق"},
    "documentary": {"name": "Documentary", "name_ar": "وثائقي", "description": "أفلام ومسلسلات وثائقية تعليمية"},
    "drama": {"name": "Drama", "name_ar": "دراما", "description": "أفلام ومسلسلات الدراما العاطفية"},
    "family": {"name": "Family", "name_ar": "عائلي", "description": "أفلام ومسلسلات عائلية مناسبة للجميع"},
    "fantasy": {"name": "Fantasy", "name_ar": "خيال", "description": "أفلام ومسلسلات الخيال والسحر"},
    "history": {"name": "History", "name_ar": "تاريخي", "description": "أفلام ومسلسلات تاريخية"},
    "horror": {"name": "Horror", "name_ar": "رعب", "description": "أفلام ومسلسلات الرعب والمخاوف"},
    "music": {"name": "Music", "name_ar": "موسيقي", "description": "أفلام ومسلسلات موسيقية"},
    "mystery": {"name": "Mystery", "name_ar": "غموض", "description": "أفلام ومسلسلات الغموض والتحقيق"},
    "romance": {"name": "Romance", "name_ar": "رومانسية", "description": "أفلام ومسلسلات الرومانسية"},
    "sci-fi": {"name": "Sci-Fi", "name_ar": "خيال علمي", "description": "أفلام ومسلسلات الخيال العلمي"},
    "tv-movie": {"name": "TV Movie", "name_ar": "فيلم تلفزيوني", "description": "أفلام تلفزيونية"},
    "thriller": {"name": "Thriller", "name_ar": "إثارة", "description": "أفلام ومسلسلات الإثارة والتشويق"},
    "war": {"name": "War", "name_ar": "حربي", "description": "أفلام ومسلسلات الحرب"},
    "western": {"name": "Western", "name_ar": "غربي", "description": "أفلام ومسلسلات الغرب الأمريكي"},
    "20th-century": {"name": "20th Century", "name_ar": "القرن العشرين", "description": "أفلام ومسلسلات من القرن العشرين"},
    "20th-century-studios": {"name": "20th Century Studios", "name_ar": "ستوديوهات القرن العشرين", "description": "أفلام ومسلسلات من ستوديوهات القرن العشرين"},
    "70s-cinema": {"name": "70s Cinema", "name_ar": "سينما السبعينات", "description": "أفلام ومسلسلات من سبعينيات القرن الماضي"},
    "80s-cinema": {"name": "80s Cinema", "name_ar": "سينما الثمانينات", "description": "أفلام ومسلسلات من ثمانينيات القرن الماضي"},
    "90s-cinema": {"name": "90s Cinema", "name_ar": "سينما التسعينات", "description": "أفلام ومسلسلات من تسعينيات القرن الماضي"},
    "2000s-cinema": {"name": "2000s Cinema", "name_ar": "سينما الألفيات", "description": "أفلام ومسلسلات من بدايات الألفية الثالثة"},
    "a24": {"name": "A24", "name_ar": "A24", "description": "أفلام ومسلسلات من استوديو A24"},
    "amazon": {"name": "Amazon", "name_ar": "أمازون", "description": "أفلام ومسلسلات أمازون أوريجينال"},
    "amazon-studios": {"name": "Amazon Studios", "name_ar": "ستوديوهات أمازون", "description": "أفلام ومسلسلات من ستوديوهات أمازون"},
    "apple": {"name": "Apple", "name_ar": "آبل", "description": "أفلام ومسلسلات آبل أوريجينال"},
    "apple-tv": {"name": "Apple TV", "name_ar": "آبل تي في", "description": "أفلام ومسلسلات آبل تي في"},
    "blumhouse": {"name": "Blumhouse", "name_ar": "بلومهاوس", "description": "أفلام ومسلسلات رعب من بلومهاوس"},
    "canal": {"name": "Canal", "name_ar": "قناة", "description": "أفلام ومسلسلات من قناة"},
    "classics": {"name": "Classics", "name_ar": "كلاسيكيات", "description": "أفلام ومسلسلات كلاسيكية"},
    "columbia-pictures": {"name": "Columbia Pictures", "name_ar": "كولومبيا بيكتشرز", "description": "أفلام ومسلسلات من كولومبيا بيكتشرز"},
    "disney": {"name": "Disney", "name_ar": "ديزني", "description": "أفلام ومسلسلات ديزني"},
    "dreamworks": {"name": "Dreamworks", "name_ar": "دريم ووركس", "description": "أفلام ومسلسلات دريم ووركس"},
    "hbo": {"name": "HBO", "name_ar": "HBO", "description": "أفلام ومسلسلات HBO"},
    "hulu": {"name": "Hulu", "name_ar": "هولو", "description": "أفلام ومسلسلات هولو"},
    "legendary": {"name": "Legendary", "name_ar": "ليجندري", "description": "أفلام ومسلسلات من ليجندري"},
    "lionsgate": {"name": "Lionsgate", "name_ar": "لايونزغيت", "description": "أفلام ومسلسلات من لايونزغيت"},
    "lucasfilm": {"name": "Lucasfilm", "name_ar": "لوكاس فيلم", "description": "أفلام ومسلسلات من لوكاس فيلم"},
    "marvel": {"name": "Marvel", "name_ar": "مارفل", "description": "أفلام ومسلسلات مارفل"},
    "marvel-studios": {"name": "Marvel Studios", "name_ar": "ستوديوهات مارفل", "description": "أفلام ومسلسلات من ستوديوهات مارفل"},
    "mbc": {"name": "MBC", "name_ar": "MBC", "description": "أفلام ومسلسلات MBC"},
    "mbc-group-shahid": {"name": "MBC Group Shahid", "name_ar": "MBC شاهد", "description": "أفلام ومسلسلات MBC شاهد"},
    "mbc-studios": {"name": "MBC Studios", "name_ar": "ستوديوهات MBC", "description": "أفلام ومسلسلات من ستوديوهات MBC"},
    "mini-series": {"name": "Mini Series", "name_ar": "مسلسلات قصيرة", "description": "مسلسلات قصيرة ومحدودة الحلقات"},
    "miramax": {"name": "Miramax", "name_ar": "ميراماكس", "description": "أفلام ومسلسلات من ميراماكس"},
    "movie": {"name": "Movies", "name_ar": "أفلام", "description": "أفلام سينمائية متنوعة"},
    "new-line": {"name": "New Line", "name_ar": "نيو لاين", "description": "أفلام ومسلسلات من نيو لاين"},
    "new-line-cinema": {"name": "New Line Cinema", "name_ar": "نيو لاين سينما", "description": "أفلام ومسلسلات من نيو لاين سينما"},
    "new-releases": {"name": "New Releases", "name_ar": "إصدارات جديدة", "description": "أحدث الإصدارات من الأفلام والمسلسلات"},
    "paramount": {"name": "Paramount", "name_ar": "باراماونت", "description": "أفلام ومسلسلات من باراماونت"},
    "pixar": {"name": "Pixar", "name_ar": "بيكسار", "description": "أفلام ومسلسلات بيكسار"},
    "reality-talk": {"name": "Reality Talk", "name_ar": "برامج واقع", "description": "برامج الواقع والحوار"},
    "sony": {"name": "Sony", "name_ar": "سوني", "description": "أفلام ومسلسلات سوني"},
    "sony-pictures": {"name": "Sony Pictures", "name_ar": "سوني بيكتشرز", "description": "أفلام ومسلسلات من سوني بيكتشرز"},
    "synergy": {"name": "Synergy", "name_ar": "سينرجي", "description": "أفلام ومسلسلات سينرجي"},
    "tv-show": {"name": "TV Shows", "name_ar": "مسلسلات", "description": "مسلسلات تلفزيونية متنوعة"},
    "universal": {"name": "Universal", "name_ar": "يونيفرسال", "description": "أفلام ومسلسلات يونيفرسال"},
    "universal-pictures": {"name": "Universal Pictures", "name_ar": "يونيفرسال بيكتشرز", "description": "أفلام ومسلسلات من يونيفرسال بيكتشرز"},
    "warner-bros": {"name": "Warner Bros", "name_ar": "وارنر براذرز", "description": "أفلام ومسلسلات من وارنر براذرز"},
    "western": {"name": "Western", "name_ar": "غربي", "description": "أفلام ومسلسلات الغرب الأمريكي"},
}

def extract_cards_from_html(html_file):
    """Extract movie/tv cards from HTML file"""
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    cards = []
    
    # Find all card elements
    for card in soup.find_all('a', class_='card'):
        href = card.get('href', '')
        img = card.find('img')
        title_div = card.find('div', class_='card-title')
        
        if not href or not img:
            continue
        
        # Extract ID and type from URL
        # URL format: https://tomito.xyz/movie/12345-title or https://tomito.xyz/tv/12345-title
        url_match = re.search(r'/(movie|tv)/(\d+)', href)
        if not url_match:
            continue
        
        media_type = url_match.group(1)
        item_id = int(url_match.group(2))
        
        # Extract poster path
        poster_path = img.get('src', '')
        if poster_path.startswith('/t/p/w500/'):
            poster_path = poster_path.replace('/t/p/w500/', '')
        
        # Extract title
        title = title_div.get_text(strip=True) if title_div else img.get('alt', '')
        
        cards.append({
            'id': item_id,
            'title': title,
            'poster_path': poster_path,
            'media_type': media_type,
            'vote_average': 0.0,  # Default value, can be updated from content_index
            'release_date': None,
            'first_air_date': None
        })
    
    return cards

def load_content_index():
    """Load content index to get additional metadata"""
    try:
        with open('data/content_index.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def main():
    # Load content index for metadata
    content_index = load_content_index()
    content_dict = {item['tmdb_id']: item for item in content_index}
    
    # Process each HTML file in genre directory
    genre_dir = Path('genre')
    output_dir = Path('data/genre')
    output_dir.mkdir(exist_ok=True)
    
    for html_file in genre_dir.glob('*.html'):
        genre_slug = html_file.stem
        
        # Get genre info
        genre_info = GENRE_NAMES.get(genre_slug, {
            'name': genre_slug.title(),
            'name_ar': genre_slug,
            'description': f'أفلام ومسلسلات {genre_slug}'
        })
        
        # Extract cards
        cards = extract_cards_from_html(html_file)
        
        # Enhance cards with metadata from content index
        for card in cards:
            if card['id'] in content_dict:
                metadata = content_dict[card['id']]
                card['title_ar'] = metadata.get('title_ar') or metadata.get('title')
                card['title'] = metadata.get('title_en') or metadata.get('title')
                card['vote_average'] = metadata.get('rating', 0)
                card['release_date'] = metadata.get('year')
                card['first_air_date'] = metadata.get('year')
        
        # Create genre data
        genre_data = {
            'name': genre_info['name'],
            'name_ar': genre_info['name_ar'],
            'description': genre_info['description'],
            'items': cards
        }
        
        # Save JSON file
        output_file = output_dir / f'{genre_slug}.json'
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(genre_data, f, ensure_ascii=False, indent=2)
        
        print(f'Created: {output_file} with {len(cards)} items')

if __name__ == '__main__':
    main()
