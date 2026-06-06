import requests
from bs4 import BeautifulSoup
import re
import json

def scrape_design(url):
    print(f"🔍 Scraping design from {url}...")
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all stylesheets
        stylesheets = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                if not href.startswith('http'):
                    href = requests.compat.urljoin(url, href)
                stylesheets.append(href)
        
        design_data = {
            "colors": {},
            "fonts": [],
            "gradients": [],
            "shadows": []
        }
        
        for css_url in stylesheets:
            print(f"  📄 Reading CSS: {css_url}")
            css_resp = requests.get(css_url)
            css_text = css_resp.text
            
            # Extract HSL variables (common in Tailwind)
            hsl_vars = re.findall(r'--([\w-]+):\s*([\d\s.%]+)', css_text)
            for name, val in hsl_vars:
                design_data["colors"][name] = val.strip()
                
            # Extract Gradients
            gradients = re.findall(r'linear-gradient\([^)]+\)', css_text)
            design_data["gradients"].extend(list(set(gradients)))
            
            # Extract Fonts
            fonts = re.findall(r'family=([\w+:]+)', css_text)
            design_data["fonts"].extend(list(set(fonts)))
            
        print("\n✨ Design Tokens Found:")
        print(json.dumps(design_data, indent=2, ensure_ascii=False))
        
        return design_data

    except Exception as e:
        print(f"❌ Error: {e}")

import sys

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_url = sys.argv[1]
    else:
        target_url = "https://tv.tomito.xyz/"
        print(f"ℹ️ No URL provided, defaulting to {target_url}")
        
    scrape_design(target_url)
