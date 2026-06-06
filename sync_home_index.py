#!/usr/bin/env python3
"""Sync data/content_index.json from data/content/*.json + sitemap folder map."""
import json
import os
import time

from rebuild_from_sitemaps import extract_sitemaps

BASE = os.path.dirname(os.path.abspath(__file__))
INDEX_FILE = os.path.join(BASE, "data", "content_index.json")
CONTENT_DIR = os.path.join(BASE, "data", "content")


def folder_map_from_sitemaps():
    m = {}
    for item in extract_sitemaps():
        m[str(item["tmdb_id"])] = item["folder"]
    return m


def json_to_entry(data, folder):
    title_ar = data.get("title_ar") or data.get("title", "")
    title_en = data.get("title_en", "")
    poster_path = data.get("poster_path") or ""
    if poster_path.startswith("/t/p/"):
        poster = poster_path
    elif poster_path.startswith("http"):
        poster = poster_path.replace("https://image.tmdb.org/t/p/w500", "/t/p/w500")
    else:
        poster = f"/t/p/w500{poster_path}" if poster_path else ""

    genres = data.get("genres") or []
    return {
        "title": f"{title_ar} / {title_en}".strip(" /"),
        "title_ar": title_ar,
        "title_en": title_en,
        "slug": data.get("slug") or str(data.get("id")),
        "folder": folder,
        "poster": poster,
        "rating": data.get("vote_average"),
        "year": (data.get("release_date") or data.get("first_air_date") or "")[:4],
        "type": "tv" if folder == "tv" else "movie",
        "tmdb_id": data.get("id"),
        "genre_ids": [g.get("id") for g in genres if g.get("id")],
        "genres": [g.get("name") for g in genres if g.get("name")],
        "timestamp": int(os.path.getmtime(os.path.join(CONTENT_DIR, f"{data['id']}.json")))
        if os.path.exists(os.path.join(CONTENT_DIR, f"{data['id']}.json"))
        else int(time.time()),
        "fixed": data.get("fixed", True),
    }


def sync():
    sitemap_folders = folder_map_from_sitemaps()
    index = []
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, encoding="utf-8") as f:
            index = json.load(f)

    by_id = {str(x.get("tmdb_id")): x for x in index if x.get("tmdb_id")}

    if not os.path.isdir(CONTENT_DIR):
        print("No content dir")
        return

    for fname in os.listdir(CONTENT_DIR):
        if not fname.endswith(".json"):
            continue
        tmdb_id = fname.replace(".json", "")
        path = os.path.join(CONTENT_DIR, fname)
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        folder = (
            data.get("folder")
            or ("tv" if data.get("media_type") == "tv" else None)
            or sitemap_folders.get(tmdb_id)
            or "movie"
        )

        entry = json_to_entry(data, folder)
        if tmdb_id in by_id:
            by_id[tmdb_id].update(entry)
        else:
            by_id[tmdb_id] = entry

    merged = sorted(by_id.values(), key=lambda x: x.get("timestamp") or 0, reverse=True)
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)
    print(f"✅ Homepage index synced: {len(merged)} entries")


if __name__ == "__main__":
    sync()
