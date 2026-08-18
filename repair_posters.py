#!/usr/bin/env python3
"""Re-download empty or corrupt local TMDB images under public/t/p/."""
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
MIN_BYTES = 100
WORKERS = 8
TIMEOUT = 15

DIRS = [
    ("w500", os.path.join(BASE_PATH, "public", "t", "p", "w500")),
    ("original", os.path.join(BASE_PATH, "public", "t", "p", "original")),
]


def is_valid_image(path):
    if not os.path.exists(path) or os.path.getsize(path) < MIN_BYTES:
        return False
    with open(path, "rb") as f:
        header = f.read(12)
    if header[:2] == b"\xff\xd8":
        return True
    if header[:4] == b"\x89PNG":
        return True
    if header[:4] == b"RIFF" and header[8:12] == b"WEBP":
        return True
    return False


def needs_download(path):
    return not is_valid_image(path)


def collect_broken():
    broken = []
    for size_path, directory in DIRS:
        if not os.path.isdir(directory):
            continue
        for name in os.listdir(directory):
            local_path = os.path.join(directory, name)
            if not os.path.isfile(local_path):
                continue
            if needs_download(local_path):
                broken.append((size_path, name, local_path))
    return broken


def download_one(size_path, filename, local_path):
    url = f"https://image.tmdb.org/t/p/{size_path}/{filename}"
    tmp_path = local_path + ".tmp"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        if resp.status_code == 404:
            return "missing", filename, url
        if resp.status_code != 200 or len(resp.content) < MIN_BYTES:
            return "failed", filename, f"status={resp.status_code} bytes={len(resp.content)}"
        header = resp.content[:12]
        valid = (
            header[:2] == b"\xff\xd8"
            or header[:4] == b"\x89PNG"
            or (header[:4] == b"RIFF" and header[8:12] == b"WEBP")
        )
        if not valid:
            return "failed", filename, "invalid image header"
        with open(tmp_path, "wb") as f:
            f.write(resp.content)
        os.replace(tmp_path, local_path)
        return "ok", filename, len(resp.content)
    except Exception as e:
        return "failed", filename, str(e)
    finally:
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass


def main():
    broken = collect_broken()
    print(f"Found {len(broken)} broken local images.")
    if not broken:
        return

    stats = {"ok": 0, "missing": 0, "failed": 0}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = [
            pool.submit(download_one, size_path, name, local_path)
            for size_path, name, local_path in broken
        ]
        for i, future in enumerate(as_completed(futures), 1):
            status, filename, detail = future.result()
            stats[status] += 1
            if status != "ok":
                print(f"  {status}: {filename} ({detail})")
            elif i % 50 == 0 or i == len(broken):
                print(f"  progress {i}/{len(broken)} ok={stats['ok']}")

    remaining = collect_broken()
    print(
        f"Done. ok={stats['ok']} missing={stats['missing']} failed={stats['failed']} still_broken={len(remaining)}"
    )
    if remaining:
        sys.exit(1)


if __name__ == "__main__":
    main()
