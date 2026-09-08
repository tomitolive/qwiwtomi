import json
import os

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_JSON = os.path.join(BASE_PATH, 'data', 'content_index.json')
SEARCH_JS = os.path.join(BASE_PATH, 'data', 'search_index.js')


def get_content_from_supabase():
    """Try to get content from Supabase."""
    try:
        from supabase_helper import get_sb
        sb = get_sb()
        result = sb.table("content").select("title, title_ar, title_en, folder, slug, poster").limit(3000).execute()
        if result.data:
            return result.data
    except Exception as e:
        print(f"⚠️ Supabase fetch failed: {e}")
    return None


def generate():
    # Try Supabase first
    data = get_content_from_supabase()
    source = "Supabase"

    # Fallback to JSON
    if not data:
        if not os.path.exists(INDEX_JSON):
            print(f"Error: {INDEX_JSON} not found.")
            return
        with open(INDEX_JSON, 'r', encoding='utf-8') as f:
            data = json.load(f)
        source = "JSON"

    # We only need specific fields for search to keep the file size manageable
    compact_data = []
    for item in data:
        compact_data.append({
            "title": item.get("title", ""),
            "title_ar": item.get("title_ar", ""),
            "title_en": item.get("title_en", ""),
            "folder": item.get("folder", "movie"),
            "slug": item.get("slug", ""),
            "poster": item.get("poster", "")
        })

    js_content = f"const FULL_INDEX = {json.dumps(compact_data, ensure_ascii=False)};"

    with open(SEARCH_JS, 'w', encoding='utf-8') as f:
        f.write(js_content)

    print(f"✅ Generated {SEARCH_JS} from {source} ({len(compact_data)} items)")


if __name__ == '__main__':
    generate()
