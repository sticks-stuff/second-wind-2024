#!/usr/bin/env python3
"""
Download (or clean up) the real images for every remotely-hosted album before/after
a Hugo build.

An album is "remotely hosted" purely by convention: a folder at
content/photos/<album-name>/ is one if there's a matching data/<album-name-with-
underscores>_files.yaml manifest containing a `base_url` and an `images` list. This
script auto-discovers every such album — nothing here is tied to a specific year or
album name, so a brand new album just needs its content folder + a matching data file.

Usage:
  python scripts/prepare_album_ci.py              # download images for every remote album
  python scripts/prepare_album_ci.py --cleanup     # remove them again after the build

  # Or target a single album explicitly (also works for one-off/manual use):
  python scripts/prepare_album_ci.py \
    --data data/second_wind_2026_files.yaml \
    --dest content/photos/second-wind-2026
"""
import argparse
import os
import sys
from pathlib import Path
from slugify import slugify

import requests
import yaml

CONTENT_PHOTOS_ROOT = Path("content/photos")
DATA_ROOT = Path("data")


def discover_remote_albums(content_photos_root: Path = CONTENT_PHOTOS_ROOT, data_root: Path = DATA_ROOT):
    """Find every content/photos/<name>/ folder with a matching data/<name>_files.yaml."""
    albums = []
    if not content_photos_root.exists():
        return albums
    for album_dir in sorted(p for p in content_photos_root.iterdir() if p.is_dir()):
        data_path = data_root / f"{album_dir.name.replace('-', '_')}_files.yaml"
        if data_path.exists():
            albums.append((album_dir.name, data_path, album_dir))
    return albums


def hugo_public_path(path: Path) -> Path:
    parts = list(path.parts)

    # slugify directories only, preserve filename
    return Path(
        *[slugify(p) for p in parts[:-1]],
        parts[-1]
    )


def load_manifest(data_path: Path) -> dict:
    if not data_path.exists():
        print(f"data file not found: {data_path}")
        return {}
    with data_path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def download_album_images(data_path: Path, dest_root: Path, base_url: str = None) -> int:
    data = load_manifest(data_path)

    images = data.get("images", [])
    if not images:
        print(f"no images listed in {data_path}")
        return 0

    base_url = base_url or data.get("base_url")
    if not base_url:
        print(f"no base_url found for {data_path} (pass --base-url or add it to the manifest)")
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


def cleanup_album_images(data_path: Path, dest_root: Path, album_name: str, public_roots=None) -> int:
    data = load_manifest(data_path)

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
                public_root / album_name / public_rel_path,
                public_root / "photos" / public_rel_path,
                public_root / "photos" / album_name / public_rel_path,
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
    parser.add_argument("--data", default=None,
                         help="Manifest for a single album. If omitted, every remote album under "
                              "content/photos/ (as discovered by naming convention) is processed.")
    parser.add_argument("--dest", default=None, help="Only used together with --data.")
    parser.add_argument("--base-url", default=None,
                         help="Overrides the manifest's own base_url, if set. Normally unnecessary "
                              "since the manifest is self-describing.")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    if args.data:
        albums = [(Path(args.dest or ".").name, Path(args.data), Path(args.dest) if args.dest else Path("."))]
    else:
        albums = discover_remote_albums()
        if not albums:
            print("no remote albums discovered under content/photos/")
            return 0
        print(f"discovered {len(albums)} remote album(s): {', '.join(a[0] for a in albums)}")

    total = 0
    for album_name, data_path, dest_root in albums:
        if args.cleanup:
            removed = cleanup_album_images(data_path, dest_root, album_name, public_roots=["public", "public/photos"])
            print(f"[{album_name}] cleanup complete: removed {removed} files")
        else:
            downloaded = download_album_images(data_path, dest_root, args.base_url)
            print(f"[{album_name}] download complete: processed {downloaded} entries")
            total += downloaded

    return 0


if __name__ == "__main__":
    sys.exit(main())
