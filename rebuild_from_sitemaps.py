#!/usr/bin/env python3
"""Rebuild all movie/TV pages listed in sitemap_*.xml via mega_bot.create_page()."""
import argparse
import json
import logging
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

import ai_engine
import mega_bot

# Skip slow Pytrends during mass rebuild
ai_engine.get_live_trends = lambda q, *args, **kwargs: ""

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE_PATH, "data", "content_index.json")

SITEMAP_FILES = [
    "sitemap_movie_1.xml",
    "sitemap_movie_2.xml",
    "sitemap_movie_3.xml",
    "sitemap_movie_4.xml",
    "sitemap_tv_1.xml",
    "sitemap_tv_2.xml",
    "sitemap_tv_3.xml",
    "sitemap_tv_4.xml",
]


def extract_sitemaps():
    seen = set()
    items = []
    for sm in SITEMAP_FILES:
        path = os.path.join(BASE_PATH, sm)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            content = f.read()
        urls = re.findall(r"<loc>(https://tomito\.xyz/([^/]+)/([^<]+))</loc>", content)
        for _, folder, slug in urls:
            if folder not in ("movie", "tv"):
                continue
            match = re.search(r"^(\d+)", slug)
            if not match:
                continue
            tmdb_id = match.group(1)
            key = (folder, tmdb_id)
            if key in seen:
                continue
            seen.add(key)
            items.append({"folder": folder, "slug": slug, "tmdb_id": tmdb_id})
    return items


def process_item(item):
    tmdb_id = str(item["tmdb_id"])
    media_type = "movie" if item["folder"] == "movie" else "tv"
    try:
        details = mega_bot.fetch_details(tmdb_id, media_type)
        if not details:
            log.warning("No TMDB details for %s (%s)", tmdb_id, media_type)
            return None
        mega_bot.index_new_page = lambda u: None  # disable Google indexing API
        _, index_entry = mega_bot.create_page(details, media_type)
        if index_entry:
            log.info("✅ %s %s", media_type, tmdb_id)
            return tmdb_id, index_entry
    except Exception as e:
        log.error("Error on %s: %s", tmdb_id, e)
    return None


def rebuild_from_sitemaps(limit=None, workers=6):
    items = extract_sitemaps()
    # ✅ Skip pages that already have a local JSON file
    local_content_dir = os.path.join(BASE_PATH, "data", "content")
    items = [
        item for item in items
        if not os.path.exists(os.path.join(local_content_dir, f"{item['tmdb_id']}.json"))
    ]
    if limit:
        items = items[:limit]
    log.info("Found %d missing pages to generate (already-local skipped)", len(items))

    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, encoding="utf-8") as f:
            index_data = json.load(f)
    else:
        index_data = []

    index_map = {str(item.get("tmdb_id")): i for i, item in enumerate(index_data)}
    lock = threading.Lock()
    count = 0
    errors = 0

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = [executor.submit(process_item, item) for item in items]
        for future in as_completed(futures):
            res = future.result()
            if not res:
                errors += 1
                continue
            tmdb_id, index_entry = res
            with lock:
                if tmdb_id in index_map:
                    index_data[index_map[tmdb_id]].update(index_entry)
                else:
                    index_data.append(index_entry)
                    index_map[tmdb_id] = len(index_data) - 1
                count += 1
                if count % 20 == 0:
                    with open(INDEX_FILE, "w", encoding="utf-8") as f:
                        json.dump(index_data, f, ensure_ascii=False, indent=2)
                    try:
                        from sync_home_index import sync as sync_home_index
                        sync_home_index()
                    except Exception as e:
                        log.warning("Home index sync skipped: %s", e)
                    log.info("💾 Index saved — %d / %d done", count, len(items))

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, ensure_ascii=False, indent=2)
    try:
        from sync_home_index import sync as sync_home_index
        sync_home_index()
    except Exception as e:
        log.warning("Final home index sync skipped: %s", e)
    log.info("🚀 Rebuild complete: %d OK, %d failed, index has %d entries", count, errors, len(index_data))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rebuild pages from sitemap XML files")
    parser.add_argument("--limit", type=int, default=None, help="Max pages to process")
    parser.add_argument("--workers", type=int, default=6, help="Parallel workers")
    args = parser.parse_args()
    rebuild_from_sitemaps(limit=args.limit, workers=args.workers)
