"""
supabase_helper.py
------------------
Supabase helper for Python bot scripts.
Provides read/write functions for content, genres, and carousel tables.
"""

import os
import json
import logging

log = logging.getLogger(__name__)

SUPABASE_URL = "https://apsfzuzvtglhhhnakjnt.supabase.co"
SUPABASE_KEY = "sb_publishable_-f_OPA_jcwhY1RZi1PnoUg_WO2RmuG1"

_sb_client = None


def get_sb():
    """Get or create Supabase client (singleton)."""
    global _sb_client
    if _sb_client is None:
        from supabase import create_client
        _sb_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _sb_client


def sb_upsert_content(record: dict):
    """Upsert a single content record to Supabase."""
    try:
        sb = get_sb()
        sb.table("content").upsert(record).execute()
        return True
    except Exception as e:
        log.error(f"Supabase upsert content failed: {e}")
        return False


def sb_upsert_content_batch(records: list):
    """Upsert a batch of content records."""
    try:
        sb = get_sb()
        sb.table("content").upsert(records).execute()
        return True
    except Exception as e:
        log.error(f"Supabase batch upsert failed: {e}")
        return False


def sb_get_all_content_ids() -> set:
    """Get all tmdb_ids from Supabase content table."""
    try:
        sb = get_sb()
        result = sb.table("content").select("tmdb_id").execute()
        return {row["tmdb_id"] for row in result.data}
    except Exception as e:
        log.error(f"Supabase get all IDs failed: {e}")
        return set()


def sb_get_content_by_id(tmdb_id: int) -> dict | None:
    """Get a single content record by tmdb_id."""
    try:
        sb = get_sb()
        result = sb.table("content").select("*").eq("tmdb_id", tmdb_id).single().execute()
        return result.data
    except Exception as e:
        log.error(f"Supabase get content failed: {e}")
        return None


def sb_upsert_genre(slug: str, name: str, name_ar: str, description: str, items: list):
    """Upsert a genre record."""
    try:
        sb = get_sb()
        sb.table("genres").upsert({
            "slug": slug,
            "name": name,
            "name_ar": name_ar,
            "description": description,
            "items": items,
        }).execute()
        return True
    except Exception as e:
        log.error(f"Supabase upsert genre failed: {e}")
        return False


def sb_upsert_carousel(records: list):
    """Replace all carousel records."""
    try:
        sb = get_sb()
        sb.table("carousel").delete().neq("id", 0).execute()
        if records:
            sb.table("carousel").insert(records).execute()
        return True
    except Exception as e:
        log.error(f"Supabase upsert carousel failed: {e}")
        return False


def content_to_sb_record(data: dict) -> dict:
    """Convert a content dict (from create_page) to a Supabase-ready record."""
    tmdb_id = data.get("id")
    folder = data.get("folder", "movie")

    # Normalize poster_path
    poster_path = data.get("poster_path", "")
    if poster_path.startswith("/t/p/"):
        poster_path = poster_path.replace("/t/p/w500", "")
    elif poster_path.startswith("http"):
        poster_path = poster_path.replace("https://image.tmdb.org/t/p/w500", "")

    poster_full = f"/t/p/w500{poster_path}" if poster_path else ""

    # Genres
    raw_genres = data.get("genres", [])
    if raw_genres and isinstance(raw_genres[0], dict):
        genres = raw_genres
    elif raw_genres and isinstance(raw_genres[0], str):
        genres = [{"id": i, "name": g} for i, g in enumerate(raw_genres)]
    else:
        genres = []

    import time

    return {
        "tmdb_id": int(tmdb_id) if tmdb_id else 0,
        "slug": data.get("slug", str(tmdb_id)),
        "title": data.get("title", ""),
        "title_ar": data.get("title_ar", ""),
        "title_en": data.get("title_en", ""),
        "type": data.get("type", folder),
        "folder": folder,
        "poster": poster_full,
        "poster_path": poster_path,
        "backdrop_path": data.get("backdrop_path", ""),
        "release_date": data.get("release_date", ""),
        "first_air_date": data.get("first_air_date", ""),
        "vote_average": data.get("vote_average"),
        "vote_count": data.get("vote_count"),
        "genres": genres,
        "genre_ids": [g.get("id") for g in genres if g.get("id")] if genres and isinstance(genres[0], dict) else data.get("genre_ids", []),
        "ai_content": data.get("ai_content", {}),
        "overview": data.get("overview", ""),
        "overview_en": data.get("overview_en", ""),
        "section": data.get("section", ""),
        "quality": data.get("quality", ""),
        "duration": data.get("duration", ""),
        "language": data.get("language", ""),
        "country": data.get("country", ""),
        "cast_members": data.get("cast", ""),
        "imdb_id": data.get("imdb_id", ""),
        "status": data.get("status", ""),
        "number_of_seasons": data.get("number_of_seasons"),
        "seasons": data.get("seasons", []),
        "number_of_episodes": data.get("number_of_episodes"),
        "timestamp": int(time.time()),
        "fixed": data.get("fixed", False),
        "name": data.get("name", ""),
        "media_type": data.get("media_type", folder),
    }
