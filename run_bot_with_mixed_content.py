#!/usr/bin/env python3
"""
run_bot_with_mixed_content.py
------------------------------
بوت جلب التريند من TMDB وإنشاء صفحات مكتملة.
- يجلب التريند فقط من TMDB (movies + tv)
- يتحقق من عدم وجود المحتوى مسبقاً
- ينشئ صفحات مكتملة (meta_desc, desc, opinion, intro, outro, faq)
- يحدّث content_index.json
- يعيد بناء الصفحة الرئيسية + listing + search index + sitemap
"""

import os
import sys
import json
import logging
import time
import subprocess

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
CONTENT_DIR = os.path.join(BASE_PATH, 'data', 'content')
INDEX_FILE = os.path.join(BASE_PATH, 'data', 'content_index.json')
SITE_URL = 'https://tomit.click'
BATCH_SIZE = 10

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
log = logging.getLogger(__name__)

from ai_engine import fetch_trending, fetch_popular, generate_meta_tags, generate_bilingual_description, generate_faq, generate_tomito_opinion, generate_page_intro_outro
from mega_bot import get_tmdb_data, fetch_details, create_page, submit_to_bing_indexnow, build_listing_pages
from google_indexer import index_new_page
import generate_search_index

try:
    import build_homepage
except ImportError:
    build_homepage = None


MIN_META_DESC_LENGTH = 150
MAX_META_DESC_LENGTH = 160
MIN_DESC_LENGTH = 150
MAX_DESC_LENGTH = 160


def needs_content_fix(ai_content):
    """فحص إذا كان المحتوى ينقصه شيء."""
    if not ai_content:
        return True

    meta_desc = ai_content.get('meta_desc', '')
    if len(meta_desc) < MIN_META_DESC_LENGTH or len(meta_desc) > MAX_META_DESC_LENGTH:
        return True

    desc_ar_len = len(ai_content.get('desc_ar', ''))
    desc_en_len = len(ai_content.get('desc_en', ''))
    if desc_ar_len < MIN_DESC_LENGTH or desc_ar_len > MAX_DESC_LENGTH:
        return True
    if desc_en_len < MIN_DESC_LENGTH or desc_en_len > MAX_DESC_LENGTH:
        return True

    if not ai_content.get('opinion_ar'):
        return True
    if not ai_content.get('opinion_en'):
        return True

    if not ai_content.get('intro'):
        return True
    if not ai_content.get('outro'):
        return True

    faq = ai_content.get('faq', [])
    if len(faq) < 3:
        return True
    for item in faq:
        a = item.get('a', '')
        a_en = item.get('a_en', '')
        q = item.get('q', '')
        q_en = item.get('q_en', '')
        if not a or not a_en:
            return True
        if not q or not q_en:
            return True
        if len(a) < 30 or len(a_en) < 30:
            return True
        if 'إجابة عن' in a or 'Answer about' in a_en:
            return True
        if 'عمل فني رائع' in a or 'wonderful piece of work' in a_en:
            return True

    return False


def fix_page_content(filepath):
    """إصلاح كل الحقول الناقصة في ai_content."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        log.warning(f"   ❌ Could not read {filepath}: {e}")
        return False

    ai_content = data.get('ai_content', {})

    if not needs_content_fix(ai_content):
        return False

    title_ar = data.get('title_ar') or data.get('title') or 'Unknown'
    title_en = data.get('title_en') or data.get('title') or 'Unknown'
    folder = data.get('folder', 'movie')
    media_type = 'movie' if folder == 'movie' else 'tv'
    year = (data.get('release_date') or '2026')[:4]
    genres_ar = [g.get('name', '') for g in data.get('genres', [])]
    overview_ar = data.get('overview', '')
    overview_en = data.get('overview_en', '') or overview_ar
    media_label_ar = "فيلم" if media_type == 'movie' else "مسلسل"
    changed = False

    log.info(f"   🔧 Fixing content: {title_ar}")

    # 1. meta_desc
    old_meta = ai_content.get('meta_desc', '')
    if len(old_meta) < MIN_META_DESC_LENGTH or len(old_meta) > MAX_META_DESC_LENGTH:
        new_data = generate_meta_tags(title_ar, title_en=title_en, year=year, genres_ar=genres_ar, media_type=media_type)
        new_meta = new_data.get('meta_desc', '')
        if len(new_meta) < MIN_META_DESC_LENGTH:
            padding = " استمتع بمشاهدة هذا العمل بجودة عالية وترجمة احترافية بدون إعلانات مزعجة."
            new_meta = new_meta + padding[:MIN_META_DESC_LENGTH - len(new_meta)]
        if len(new_meta) > MAX_META_DESC_LENGTH:
            new_meta = new_meta[:MAX_META_DESC_LENGTH]
        if new_meta and new_meta != old_meta:
            ai_content['meta_desc'] = new_meta
            changed = True
            log.info(f"   ✅ Fixed meta_desc")

    # 2. desc_ar + desc_en
    desc_ar = ai_content.get('desc_ar', '')
    desc_en = ai_content.get('desc_en', '')
    desc_ar_len = len(desc_ar)
    desc_en_len = len(desc_en)
    if desc_ar_len < MIN_DESC_LENGTH or desc_ar_len > MAX_DESC_LENGTH or desc_en_len < MIN_DESC_LENGTH or desc_en_len > MAX_DESC_LENGTH:
        try:
            tri = generate_bilingual_description(title_ar, title_en, overview_ar, overview_en, year, genres_ar, media_type)
            if tri:
                if tri.get('desc_ar'):
                    ai_content['desc_ar'] = tri['desc_ar'][:MAX_DESC_LENGTH]
                    changed = True
                if tri.get('desc_en'):
                    ai_content['desc_en'] = tri['desc_en'][:MAX_DESC_LENGTH]
                    changed = True
                log.info(f"   ✅ Fixed desc_ar/desc_en")
        except Exception as e:
            log.warning(f"   ⚠️ desc generation failed: {e}")

    # Fallback: if desc_ar still not 150-160, pad from overview
    if not ai_content.get('desc_ar') or len(ai_content['desc_ar']) < MIN_DESC_LENGTH:
        genres_str = ", ".join(genres_ar) if genres_ar else ""
        base = overview_ar or f"يقدم {media_label_ar} {title_ar} تجربة مشاهدة مميزة."
        suffix = f" استمتع بمشاهدة {media_label_ar} {title_ar} ({year}) مترجم بجودة عالية على توميتو{'. يندرج تحت تصنيف ' + genres_str + '.' if genres_str else ''}"
        padded = base + suffix
        if len(padded) < MIN_DESC_LENGTH:
            padded += " شاهد الآن بدون إعلانات وبجودة HD."
        ai_content['desc_ar'] = padded[:MAX_DESC_LENGTH]
        changed = True
        log.info(f"   ✅ Padded desc_ar to {len(ai_content['desc_ar'])} chars")

    # Trim desc_ar if too long
    if len(ai_content.get('desc_ar', '')) > MAX_DESC_LENGTH:
        ai_content['desc_ar'] = ai_content['desc_ar'][:MAX_DESC_LENGTH]
        changed = True

    if not ai_content.get('desc_en') or len(ai_content['desc_en']) < MIN_DESC_LENGTH:
        genres_str = ", ".join(genres_ar) if genres_ar else ""
        base_en = overview_en or f"{title_en} is worth watching."
        suffix_en = f" Watch {title_en} ({year}) fully translated in high quality on Tomito{'. Genre: ' + genres_str + '.' if genres_str else '.'}"
        padded_en = base_en + suffix_en
        if len(padded_en) < MIN_DESC_LENGTH:
            padded_en += " Watch now without ads in HD quality."
        ai_content['desc_en'] = padded_en[:MAX_DESC_LENGTH]
        changed = True
        log.info(f"   ✅ Padded desc_en to {len(ai_content['desc_en'])} chars")

    # Trim desc_en if too long
    if len(ai_content.get('desc_en', '')) > MAX_DESC_LENGTH:
        ai_content['desc_en'] = ai_content['desc_en'][:MAX_DESC_LENGTH]
        changed = True

    # 3. opinion_ar + opinion_en
    opinion_ar = ai_content.get('opinion_ar', '')
    opinion_en = ai_content.get('opinion_en', '')
    if not opinion_ar or not opinion_en:
        try:
            new_opinion_ar = generate_tomito_opinion(title_ar, title_en, year, media_type)
            new_opinion_en = generate_tomito_opinion(title_en, title_en, year, media_type)
            if new_opinion_ar:
                ai_content['opinion_ar'] = new_opinion_ar
                changed = True
            if new_opinion_en:
                ai_content['opinion_en'] = new_opinion_en
                changed = True
            log.info(f"   ✅ Fixed opinion")
        except Exception as e:
            log.warning(f"   ⚠️ opinion generation failed: {e}")

    # 4. intro + outro
    intro = ai_content.get('intro', '')
    outro = ai_content.get('outro', '')
    if not intro or not outro:
        try:
            new_intro, new_outro = generate_page_intro_outro(title_ar, title_en, year, media_type, genres_ar)
            if new_intro:
                ai_content['intro'] = new_intro
                changed = True
            if new_outro:
                ai_content['outro'] = new_outro
                changed = True
            log.info(f"   ✅ Fixed intro/outro")
        except Exception as e:
            log.warning(f"   ⚠️ intro/outro generation failed: {e}")

    # 5. faq
    faq = ai_content.get('faq', [])
    faq_bad = len(faq) < 3
    if not faq_bad:
        for item in faq:
            a = item.get('a', '')
            a_en = item.get('a_en', '')
            q = item.get('q', '')
            q_en = item.get('q_en', '')
            if not a or not a_en or not q or not q_en:
                faq_bad = True
                break
            if len(a) < 30 or len(a_en) < 30:
                faq_bad = True
                break
            if 'إجابة عن' in a or 'Answer about' in a_en:
                faq_bad = True
                break
            if 'عمل فني رائع' in a or 'wonderful piece of work' in a_en:
                faq_bad = True
                break
    if faq_bad:
        try:
            new_faq = generate_faq(title_ar, title_en, year, media_type, overview=overview_ar, genres_ar=genres_ar)
            if new_faq and len(new_faq) >= 3:
                ai_content['faq'] = new_faq
                changed = True
                log.info(f"   ✅ Fixed FAQ ({len(new_faq)} questions)")
        except Exception as e:
            log.warning(f"   ⚠️ FAQ generation failed: {e}")

    # 6. keywords
    if not ai_content.get('keywords'):
        genres_str = ", ".join(genres_ar) if isinstance(genres_ar, list) else str(genres_ar)
        ai_content['keywords'] = f"{title_ar} مترجم, {title_en} مترجم, مشاهدة {title_ar}, {media_label_ar} {year}, {genres_str}"
        changed = True
        log.info(f"   ✅ Fixed keywords")

    if changed:
        data['ai_content'] = ai_content
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        log.info(f"   ✅ Saved: {title_ar}")

    return changed


def load_content_index():
    """تحميل الفهرس + استخراج IDs الموجودة."""
    if os.path.exists(INDEX_FILE):
        try:
            with open(INDEX_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            seen = set()
            int_ids = set()
            for item in data:
                tid = str(item.get('tmdb_id', ''))
                m_type = item.get('folder', 'movie')
                if tid:
                    seen.add(f"{m_type}-{tid}")
                    int_ids.add(int(tid))
            return data, seen, int_ids
        except Exception:
            pass
    return [], set(), set()


def check_page_exists(tmdb_id):
    """التحقق من وجود الصفحة في data/content/."""
    json_path = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
    return os.path.exists(json_path)


def main():
    log.info("🚀 Starting Trending Bot (Complete Pages)...")
    log.info("=" * 60)

    all_index, seen_ids, int_ids = load_content_index()
    log.info(f"📊 Existing pages: {len(all_index)}")

    # جلب التريند من TMDB
    log.info("🔥 Fetching trending content...")
    trending_movies = fetch_trending('movie', available_ids=int_ids)
    trending_tv = fetch_trending('tv', available_ids=int_ids)
    all_trending = (trending_movies or []) + (trending_tv or [])

    new_items = []
    for item in all_trending:
        tmdb_id = str(item.get('tmdb_id', ''))
        media_type = item.get('folder', 'movie')
        unique_key = f"{media_type}-{tmdb_id}"

        if unique_key in seen_ids:
            log.debug(f"   Skipping {item.get('title')} (already exists)")
            continue
        if check_page_exists(tmdb_id):
            log.debug(f"   Skipping {item.get('title')} (file exists)")
            seen_ids.add(unique_key)
            continue
        new_items.append(item)

    # إذا فاضي التريند الجديد → جلب الشائع (What's Popular)
    if not new_items:
        log.info("🌟 No new trending items, fetching popular content...")
        popular_movies = fetch_popular('movie', available_ids=int_ids)
        popular_tv = fetch_popular('tv', available_ids=int_ids)
        all_popular = (popular_movies or []) + (popular_tv or [])

        for item in all_popular:
            tmdb_id = str(item.get('tmdb_id', ''))
            media_type = item.get('folder', 'movie')
            unique_key = f"{media_type}-{tmdb_id}"

            if unique_key in seen_ids:
                continue
            if check_page_exists(tmdb_id):
                seen_ids.add(unique_key)
                continue
            new_items.append(item)

        if new_items:
            log.info(f"✅ Found {len(new_items)} popular items as fallback")

    # إذا فاضي أيضاً → جلب top rated
    if not new_items:
        log.info("⭐ Popular is also empty, fetching top rated content...")
        from ai_engine import fetch_random_high_rated
        top_movie = fetch_random_high_rated('movie', available_ids=int_ids)
        top_tv = fetch_random_high_rated('tv', available_ids=int_ids)
        all_top = [x for x in [top_movie, top_tv] if x]

        for item in all_top:
            tmdb_id = str(item.get('tmdb_id', ''))
            media_type = item.get('folder', 'movie')
            unique_key = f"{media_type}-{tmdb_id}"

            if unique_key in seen_ids:
                continue
            if check_page_exists(tmdb_id):
                seen_ids.add(unique_key)
                continue
            new_items.append(item)

        if new_items:
            log.info(f"✅ Found {len(new_items)} top rated items as fallback")

    if not new_items:
        log.info("✅ All trending items already have pages!")
        log.info("=" * 60)
        return

    log.info(f"🆕 New trending items to create: {len(new_items)}")
    batch = new_items[:BATCH_SIZE]
    log.info(f"📋 Processing batch of {len(batch)} pages")

    created = 0
    for i, item in enumerate(batch):
        tmdb_id = str(item.get('tmdb_id', ''))
        media_type = item.get('folder', 'movie')
        title = item.get('title') or 'Unknown'

        log.info(f"[{i+1}/{len(batch)}] 📥 {media_type.upper()} ID: {tmdb_id} - {title}")

        try:
            details = fetch_details(tmdb_id, media_type, bypass_adult_check=True)
            if not details:
                log.warning(f"   ❌ TMDB fetch failed — skipping")
                continue

            page_path, entry = create_page(details, media_type, is_trend=True, force=True, skip_images=False)

            if entry:
                # ضمان اكتمال الصفحة
                content_file = os.path.join(CONTENT_DIR, f"{tmdb_id}.json")
                if os.path.exists(content_file):
                    fix_page_content(content_file)

                all_index.append(entry)
                created += 1
                seen_ids.add(f"{media_type}-{tmdb_id}")
                log.info(f"   ✅ Created: {page_path}")

                try:
                    full_url = f"https://tomit.click/{page_path}"
                    submit_to_bing_indexnow(full_url)
                    google_status = index_new_page(full_url)
                    log.info(f"   📡 Google: {google_status}")
                except Exception as e:
                    log.warning(f"   ⚠️ Indexing failed: {e}")
            else:
                log.warning(f"   ❌ AI generation failed for {title}")

        except Exception as e:
            log.error(f"   ❌ Error processing {title}: {e}")

        time.sleep(2)

    log.info("=" * 60)
    log.info(f"📈 Statistics:")
    log.info(f"   ✅ Created: {created}/{len(batch)}")
    log.info(f"   📊 Total pages: {len(all_index)}")

    if created > 0:
        os.makedirs(os.path.dirname(INDEX_FILE), exist_ok=True)
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            json.dump(all_index, f, ensure_ascii=False, indent=2)
        log.info(f"💾 content_index.json updated ({len(all_index)} entries)")

        # ── Sync full index to Supabase ─────────────────────────────────────
        try:
            from supabase_helper import get_sb, content_to_sb_record
            sb = get_sb()
            # Batch upsert all entries from the index (for new entries only)
            new_records = []
            for entry in all_index:
                tmdb_id = entry.get('tmdb_id')
                if tmdb_id:
                    # Build a minimal record from index entry
                    record = {
                        "tmdb_id": int(tmdb_id),
                        "slug": entry.get("slug", ""),
                        "title": entry.get("title", ""),
                        "title_ar": entry.get("title_ar", ""),
                        "title_en": entry.get("title_en", ""),
                        "type": entry.get("type", entry.get("folder", "movie")),
                        "folder": entry.get("folder", "movie"),
                        "poster": entry.get("poster", ""),
                        "vote_average": entry.get("rating"),
                        "genres": entry.get("genres", []),
                        "genre_ids": entry.get("genre_ids", []),
                        "timestamp": entry.get("timestamp"),
                        "fixed": entry.get("fixed", False),
                    }
                    new_records.append(record)
            if new_records:
                sb.table("content").upsert(new_records).execute()
                log.info(f"☁️  Supabase index synced ({len(new_records)} entries)")
        except Exception as e:
            log.warning(f"⚠️ Supabase sync failed (JSON is saved): {e}")

        try:
            if build_homepage:
                build_homepage.build()
                if hasattr(build_homepage, 'build_all_pages'):
                    build_homepage.build_all_pages()
            build_listing_pages()
            log.info("🏗️  Homepage and listing pages rebuilt.")
        except Exception as e:
            log.warning(f"Rebuild warning: {e}")

        try:
            generate_search_index.generate()
            log.info("🔍 Search index updated.")
        except Exception as e:
            log.warning(f"Search index warning: {e}")

        try:
            from generate_full_sitemap import generate_sitemaps
            generate_sitemaps()
            log.info("🗺️  Sitemaps regenerated.")
        except Exception as e:
            log.warning(f"Sitemap warning: {e}")

        git_sync = os.path.join(BASE_PATH, 'git_sync.sh')
        if os.path.exists(git_sync):
            try:
                subprocess.run(['bash', git_sync], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    log.info("\n" + "=" * 60)
    log.info("✅ Trending Bot run complete!")
    log.info("=" * 60)


if __name__ == "__main__":
    main()
