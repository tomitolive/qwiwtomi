import json
import os
import glob
import requests
from concurrent.futures import ThreadPoolExecutor

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
POSTER_DIR = os.path.join(BASE_PATH, 'public', 't', 'p', 'w500')
BACKDROP_DIR = os.path.join(BASE_PATH, 'public', 't', 'p', 'original')

os.makedirs(POSTER_DIR, exist_ok=True)
os.makedirs(BACKDROP_DIR, exist_ok=True)

def is_valid_local_image(path, min_bytes=100):
    if not os.path.exists(path) or os.path.getsize(path) < min_bytes:
        return False
    with open(path, "rb") as f:
        header = f.read(12)
    return (
        header[:2] == b"\xff\xd8"
        or header[:4] == b"\x89PNG"
        or (header[:4] == b"RIFF" and header[8:12] == b"WEBP")
    )

def download_image(path, is_backdrop=False):
    if not path:
        return
    filename = path.lstrip('/')
    target_dir = BACKDROP_DIR if is_backdrop else POSTER_DIR
    local_path = os.path.join(target_dir, filename)
    
    if is_valid_local_image(local_path):
        return  # Already downloaded
        
    size_path = 'original' if is_backdrop else 'w500'
    source_url = f"https://image.tmdb.org/t/p/{size_path}/{filename}"
    
    try:
        resp = requests.get(source_url, timeout=10)
        if resp.status_code == 200 and resp.content and len(resp.content) > 100:
            tmp_path = local_path + ".tmp"
            with open(tmp_path, 'wb') as f:
                f.write(resp.content)
            os.replace(tmp_path, local_path)
            print(f"✅ Downloaded: {filename}")
        else:
            print(f"❌ Failed to download {filename} (Status: {resp.status_code})")
    except Exception as e:
        print(f"❌ Error downloading {filename}: {e}")

def process_file(fp):
    try:
        with open(fp, 'r', encoding='utf-8') as f:
            data = json.load(f)
        download_image(data.get('poster_path'), is_backdrop=False)
        download_image(data.get('backdrop_path'), is_backdrop=True)
    except Exception as e:
        print(f"Error processing {fp}: {e}")

def main():
    files = glob.glob(os.path.join(BASE_PATH, 'data', 'content', '*.json'))
    print(f"Found {len(files)} JSON files. Starting parallel downloads...")
    with ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(process_file, files)
    print("🎉 All downloads completed!")

if __name__ == '__main__':
    main()
