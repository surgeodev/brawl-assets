#!/usr/bin/env python3
"""Convert all raw assets + CDN to WebP previews."""
import json, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
CDN_DIR = BASE / "_cdn_brawlers"
PREVIEWS_DIR = BASE / "previews"
ASSETS_JSON = BASE / "data" / "assets.json"

PREVIEW_SIZES = {
    "Brawlers": 512, "Backgrounds": 512, "LoadingScreens": 512,
    "Wallpapers": 512, "Misc": 512, "Animations": 512,
    "UI": 256, "Logos": 256, "Icons": 256,
    "Portraits": 256, "Emojis": 256, "Pins": 128, "Sprays": 128,
}

Image.MAX_IMAGE_PIXELS = None

def convert(entry):
    cat = entry["category"]
    sub = entry.get("subcategory", "General")
    stem = entry.get("display_name", entry["id"]).replace(" ", "_")
    ext = entry.get("extension", "png").lstrip(".")
    fname = f"{stem}.{ext}"

    # Source file location
    src = RAW_DIR / fname
    if not src.exists() and entry.get("source") == "brawlify_cdn":
        src = CDN_DIR / entry.get("filename", fname)
    if not src.exists():
        return (entry["id"], False, "not_found")

    dst = PREVIEWS_DIR / cat / sub / f"{stem}.webp"
    if dst.exists():
        return (entry["id"], True, "exists")

    try:
        img = Image.open(str(src))
        max_size = PREVIEW_SIZES.get(cat, 256)
        w, h = img.size
        if max(w, h) > max_size:
            if w > h:
                nw, nh = max_size, max(1, int(h * max_size / w))
            else:
                nh, nw = max_size, max(1, int(w * max_size / h))
            img = img.resize((nw, nh), Image.LANCZOS)
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
        elif img.mode != "RGB":
            img = img.convert("RGB")
        dst.parent.mkdir(parents=True, exist_ok=True)
        img.save(str(dst), "WEBP", quality=78, method=4, lossless=False)
        return (entry["id"], True, "ok")
    except Exception as e:
        return (entry["id"], False, str(e)[:60])

def main():
    print("=" * 60)
    print("Build WebP Previews")
    print("=" * 60)

    with open(ASSETS_JSON) as f:
        entries = json.load(f)

    t0 = time.time()
    done = 0
    ok = 0
    fail = 0

    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(convert, e): e for e in entries}
        for i, future in enumerate(as_completed(futures)):
            _, success, msg = future.result()
            ok += success
            fail += not success
            done += 1
            if done % 500 == 0 or done == len(entries):
                print(f"  [{done}/{len(entries)}] ok={ok} fail={fail} ({time.time()-t0:.0f}s)")

    total_previews = sum(1 for f in PREVIEWS_DIR.rglob("*.webp"))
    print(f"\n  Total previews: {total_previews}")
    print(f"  Time: {(time.time()-t0)/60:.1f} min")

if __name__ == "__main__":
    main()
