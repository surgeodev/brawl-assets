#!/usr/bin/env python3
"""Minimal update: convert CDN images to WebP + quick manifest."""
import json, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image

BASE = Path("/data/data/com.termux/files/home/BrawlAssets")
ASSETS_JSON = BASE / "assets.json"
BRAWLERS_JSON = BASE / "brawlers.json"
FANKIT = BASE / "BrawlAssets"
PREVIEWS = BASE / "previews"
SIZES = {"Brawlers": 512, "Backgrounds": 512, "LoadingScreens": 512,
         "UI": 256, "Logos": 256, "Icons": 256, "Pins": 128, "Sprays": 128}

def orig_path(e):
    stem = e.get("display_name", e["id"]).replace(" ", "_")
    ext = e.get("extension", "png").lstrip(".")
    return FANKIT / e["category"] / e.get("subcategory", "General") / f"{stem}.{ext}"

def prev_path(e):
    o = orig_path(e)
    return PREVIEWS / o.relative_to(FANKIT).with_suffix(".webp")

def convert(e):
    try:
        o = orig_path(e)
        if not o.exists():
            return (e["id"], "not_found")
        p = prev_path(e)
        if p.exists():
            return (e["id"], "exists")
        p.parent.mkdir(parents=True, exist_ok=True)
        img = Image.open(str(o))
        ms = SIZES.get(e["category"], 256)
        w, h = img.size
        if w > ms or h > ms:
            r = ms / max(w, h)
            img = img.resize((int(w*r), int(h*r)), Image.LANCZOS)
        img = img.convert("RGBA") if img.mode == "RGBA" else img.convert("RGB")
        img.save(str(p), "WEBP", quality=78, method=4, lossless=False)
        return (e["id"], "ok")
    except Exception as ex:
        return (e["id"], str(ex)[:60])

print("Loading assets.json...")
t0 = time.time()
with open(ASSETS_JSON) as f:
    all_entries = json.load(f)
cdn = [e for e in all_entries if e.get("source") == "brawlify_cdn"]
print(f"  {len(all_entries)} total, {len(cdn)} CDN")

if cdn:
    print("Converting CDN images to WebP...")
    ok, ex, fail = 0, 0, 0
    with ThreadPoolExecutor(max_workers=3) as tp:
        fs = {tp.submit(convert, e): e for e in cdn}
        for f in as_completed(fs):
            _, r = f.result()
            if r == "ok": ok += 1
            elif r == "exists": ex += 1
            else: fail += 1
    print(f"  converted={ok} existed={ex} failed={fail}")
else:
    print("  No CDN entries to convert")

# Count previews
n_prev = len(list(PREVIEWS.rglob("*.webp")))
print(f"  Total previews: {n_prev}")

# Build quick manifest (CDN only added)
print("Building preview_manifest.json...")
mani = []
for e in all_entries:
    p = prev_path(e)
    prv = str(p.relative_to(PREVIEWS)) if p.exists() else "N/A"
    mani.append({
        "id": e["id"],
        "name": e.get("display_name", ""),
        "preview": f"previews/{prv}",
        "cat": e.get("category", ""),
        "url": e.get("url", ""),
        "source": e.get("source", "fankit"),
    })
with open(BASE / "preview_manifest.json", "w") as f:
    json.dump(mani, f, indent=2)
print(f"  {len(mani)} entries written")

# Also save brawlers.json reference
with open(BRAWLERS_JSON) as f:
    brawlers = json.load(f)
print(f"  brawlers.json: {len(brawlers)} brawlers")

print(f"\nDone in {time.time()-t0:.1f}s")
