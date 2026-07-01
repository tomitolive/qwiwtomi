#!/usr/bin/env python3
"""Generate sitemap index and individual category sitemaps from data/content_index.json"""

import os
import json
from datetime import datetime

def generate_sitemaps():
    base_url = "https://tomito.xyz"
    img_base_url = "https://tomito.xyz" # Images are now served via Next.js directly
    root_dir = os.path.dirname(os.path.abspath(__file__))
    index_file = os.path.join(root_dir, 'data', 'content_index.json')
    today = datetime.now().strftime('%Y-%m-%d')
    
    sitemap_index_urls = []
    MAX_LINKS = 300
    
    # 1. Main Root Sitemap (Homepage & Root Pages)
    root_urls = []
    root_urls.append({'loc': f"{base_url}/", 'priority': 1.0, 'freq': 'daily'})
    # Essential Next.js pages
    root_pages = ['movie', 'tv']
    for p in root_pages:
        root_urls.append({'loc': f"{base_url}/{p}", 'priority': 0.9, 'freq': 'daily'})
    
    if root_urls:
        sitemap_index_urls.extend(write_split_sitemaps(root_dir, "root", root_urls, base_url, today, MAX_LINKS))

    # Load content index
    content_index = []
    if os.path.exists(index_file):
        with open(index_file, 'r', encoding='utf-8') as f:
            content_index = json.load(f)

    # Separate into movies and tv shows
    movies = [item for item in content_index if item.get('folder') == 'movie']
    tv_shows = [item for item in content_index if item.get('folder') == 'tv']

    # 2. Movie Sitemaps
    if movies:
        movie_urls = []
        for item in movies:
            slug = item.get('slug') or str(item.get('tmdb_id'))
            url = f"{base_url}/movie/{slug}"
            poster = item.get('poster')
            img_url = f"{img_base_url}{poster}" if poster else None
            
            url_item = {'loc': url, 'priority': 0.8, 'freq': 'weekly'}
            if img_url: url_item['image'] = img_url
            movie_urls.append(url_item)
            
        sitemap_index_urls.extend(write_split_sitemaps(root_dir, "movie", movie_urls, base_url, today, MAX_LINKS))

    # 3. TV Show Sitemaps
    if tv_shows:
        tv_urls = []
        for item in tv_shows:
            slug = item.get('slug') or str(item.get('tmdb_id'))
            url = f"{base_url}/tv/{slug}"
            poster = item.get('poster')
            img_url = f"{img_base_url}{poster}" if poster else None
            
            url_item = {'loc': url, 'priority': 0.8, 'freq': 'weekly'}
            if img_url: url_item['image'] = img_url
            tv_urls.append(url_item)
            
        sitemap_index_urls.extend(write_split_sitemaps(root_dir, "tv", tv_urls, base_url, today, MAX_LINKS))

    # 4. Generate Main Sitemap Index
    index_path = os.path.join(root_dir, 'public', 'sitemap.xml')
    os.makedirs(os.path.dirname(index_path), exist_ok=True)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n')
        for loc in sitemap_index_urls:
            f.write(f'  <sitemap>\n')
            f.write(f'    <loc>{loc}</loc>\n')
            f.write(f'    <lastmod>{today}</lastmod>\n')
            f.write(f'  </sitemap>\n')
        f.write('</sitemapindex>')
    
    print(f"\nGenerated sitemap index: {index_path} with {len(sitemap_index_urls)} sub-sitemaps.")

def write_split_sitemaps(root_dir, name, urls, base_url, date, max_links):
    """Splits URLs into chunks of max_links and writes separate XML files."""
    # Deduplicate
    unique_urls = {}
    for u in urls:
        loc = u['loc']
        if loc not in unique_urls or u['priority'] > unique_urls[loc]['priority']:
            unique_urls[loc] = u
    
    sorted_items = sorted(unique_urls.values(), key=lambda x: x['loc'])
    chunks = [sorted_items[i:i + max_links] for i in range(0, len(sorted_items), max_links)]
    
    generated_urls = []
    for idx, chunk in enumerate(chunks, 1):
        filename = f"sitemap_{name}_{idx}.xml" if len(chunks) > 1 else f"sitemap_{name}.xml"
        filepath = os.path.join(root_dir, 'public', filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            f.write('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n')
            for item in chunk:
                f.write(f'  <url>\n')
                f.write(f'    <loc>{item["loc"]}</loc>\n')
                f.write(f'    <lastmod>{date}</lastmod>\n')
                f.write(f'    <changefreq>{item["freq"]}</changefreq>\n')
                f.write(f'    <priority>{item["priority"]:.1f}</priority>\n')
                if 'image' in item:
                    f.write(f'    <image:image>\n')
                    f.write(f'      <image:loc>{item["image"]}</image:loc>\n')
                    f.write(f'    </image:image>\n')
                f.write(f'  </url>\n')
            f.write('</urlset>')
        
        generated_urls.append(f"{base_url}/{filename}")
        print(f"    - {filename}: {len(chunk)} URLs")
    
    return generated_urls

if __name__ == '__main__':
    generate_sitemaps()
