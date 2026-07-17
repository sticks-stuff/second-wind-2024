#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from slugify import slugify

import requests
import yaml

def hugo_public_path(path: Path) -> Path:
    parts = list(path.parts)

    # slugify directories only, preserve filename
    return Path(
        *[slugify(p) for p in parts[:-1]],
        parts[-1]
    )

def download_album_images(data_path: Path, dest_root: Path, base_url: str) -> int:
    if not data_path.exists():
        print(f"data file not found: {data_path}")
        return 0

    with data_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    images = data.get("images", [])
    if not images:
        print("no images listed in data file")
        return 0

    for item in images:
        name = item.get("name")
        if not name:
            continue
        src = f"{base_url.rstrip('/')}/{name.lstrip('/')}"
        outp = dest_root / Path(name)
        outp.parent.mkdir(parents=True, exist_ok=True)
        if outp.exists():
            print(f"already exists: {outp}")
            continue
        print(f"downloading: {src}")
        r = requests.get(src, stream=True, timeout=60)
        r.raise_for_status()
        with outp.open("wb") as fh:
            for chunk in r.iter_content(8192):
                fh.write(chunk)
    return len(images)


def cleanup_album_images(data_path: Path, dest_root: Path, public_roots=None) -> int:
    if not data_path.exists():
        print(f"data file not found: {data_path}")
        return 0

    with data_path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    public_roots = [Path(p) for p in (public_roots or ["public", "public/photos"])]
    removed = 0
    for item in data.get("images", []):
        name = item.get("name")
        if not name:
            continue
        rel_path = Path(name)
        public_rel_path = hugo_public_path(rel_path)
        candidates = [dest_root / rel_path]

        for public_root in public_roots:
            candidates.extend([
                public_root / public_rel_path,
                public_root / "second-wind-2026" / public_rel_path,
                public_root / "photos" / public_rel_path,
                public_root / "photos" / "second-wind-2026" / public_rel_path,
            ])

        for candidate in candidates:
            if candidate.exists():
                candidate.unlink()
                print(f"removed: {candidate}")
                removed += 1

    roots_to_cleanup = [dest_root, *public_roots]
    for root in roots_to_cleanup:
        if not root.exists():
            continue
        for current_root, dirs, files in os.walk(root, topdown=False):
            if not os.listdir(current_root):
                try:
                    os.rmdir(current_root)
                except OSError:
                    pass
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="Download or clean up album images for Hugo CI builds")
    parser.add_argument("--data", default="data/second_wind_2026_files.yaml")
    parser.add_argument("--dest", default="content/photos/second-wind-2026")
    parser.add_argument("--base-url", default="https://sharlot.memes.nz/second-wind-photos/second-wind-2026")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    data_path = Path(args.data)
    dest_root = Path(args.dest)

    if args.cleanup:
        removed = cleanup_album_images(data_path, dest_root, public_roots=["public", "public/photos"])
        print(f"cleanup complete: removed {removed} files")
        return 0

    downloaded = download_album_images(data_path, dest_root, args.base_url)
    print(f"download complete: processed {downloaded} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
