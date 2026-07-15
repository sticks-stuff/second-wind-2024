#!/usr/bin/env python3
"""
Generate a YAML data file listing image files for a Hugo album and optionally delete the local image files.

Usage:
  python scripts/generate_album_filelist.py \
    --album content/photos/second-wind-2026 \
    --out data/second_wind_2026_files.yaml \
    [--delete]

The script scans the album folder recursively for image files, writes a YAML file containing
filename, relative path and image dimensions, and (if --delete) removes the files from disk.
"""
import argparse
import os
import sys
import yaml
from pathlib import Path

try:
    from PIL import Image
except Exception:
    print("Pillow is required. Install with: pip install pillow")
    sys.exit(2)

IMG_EXTS = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.JPG', '.JPEG', '.PNG')


def gather_images(album_dir: Path):
    items = []
    for root, dirs, files in os.walk(album_dir):
        for f in sorted(files):
            if f.endswith(IMG_EXTS):
                full = Path(root) / f
                rel = full.relative_to(album_dir)
                try:
                    with Image.open(full) as im:
                        w, h = im.size
                except Exception:
                    w, h = None, None
                items.append({
                    'name': str(rel.as_posix()),
                    'filename': f,
                    'width': w,
                    'height': h,
                })
    return items


def write_yaml(out_path: Path, images):
    data = {'images': images}
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open('w', encoding='utf-8') as fh:
        yaml.dump(data, fh, sort_keys=False)


def delete_files(album_dir: Path, images):
    for item in images:
        p = album_dir / Path(item['name'])
        if p.exists():
            try:
                p.unlink()
                print(f"deleted: {p}")
            except Exception as e:
                print(f"failed to delete {p}: {e}")
    # remove any empty directories under album_dir
    for root, dirs, files in os.walk(album_dir, topdown=False):
        if not os.listdir(root):
            try:
                os.rmdir(root)
                print(f"removed empty dir: {root}")
            except Exception:
                pass


def add_gitignore_entry(pattern: str, gitignore_path: Path = Path('.gitignore')):
    gitignore_path = gitignore_path.resolve()
    existing = []
    if gitignore_path.exists():
        with gitignore_path.open('r', encoding='utf-8') as fh:
            existing = [l.rstrip('\n') for l in fh]
    if pattern in existing:
        print(f".gitignore already contains: {pattern}")
        return
    with gitignore_path.open('a', encoding='utf-8') as fh:
        if not existing or existing[-1] != '':
            fh.write('\n')
        fh.write(pattern + '\n')
    print(f"Appended to .gitignore: {pattern}")


def main():
    parser = argparse.ArgumentParser(description='Generate album file list and optionally delete local files')
    parser.add_argument('--album', required=True, help='Path to album folder (e.g. content/photos/second-wind-2026)')
    parser.add_argument('--out', default='data/second_wind_2026_files.yaml', help='Output data YAML file')
    parser.add_argument('--delete', action='store_true', help='Delete the local image files after generating list')
    parser.add_argument('--gitignore', action='store_true', help='Append the album path to .gitignore instead of deleting files')
    args = parser.parse_args()

    album_dir = Path(args.album)
    if not album_dir.exists() or not album_dir.is_dir():
        print(f"Album directory not found: {album_dir}")
        sys.exit(1)

    images = gather_images(album_dir)
    if not images:
        print("No images found in album")
        sys.exit(0)

    out_path = Path(args.out)
    write_yaml(out_path, images)
    print(f"Wrote {len(images)} entries to {out_path}")

    if args.gitignore:
        # add a pattern to .gitignore to keep files locally but untracked
        # pattern used: /content/photos/second-wind-2026/**
        rel = os.path.normpath(str(album_dir)).replace('\\', '/')
        pattern = f"/{rel}/**"
        add_gitignore_entry(pattern)

    if args.delete:
        confirm = input(f"Delete {len(images)} files under {album_dir}? Type YES to confirm: ")
        if confirm == 'YES':
            delete_files(album_dir, images)
        else:
            print("Aborted deletion")


if __name__ == '__main__':
    main()
