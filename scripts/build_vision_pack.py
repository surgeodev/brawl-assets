#!/usr/bin/env python3
"""
Brawl Stars AI Vision Pack Builder
===================================
Converts every original asset into WebP previews optimized for AI reasoning.
Extracts rich image statistics, generates contact sheets, and builds
semantic indexes for visual search.

Phases:
  1. WebP Conversion (method=4, quality=78)
  2. Image Statistics Extraction
  3. Contact Sheets (per-category + global)
  4. AI Indexes Generation
  5. Embeddings (if available)
"""

import json
import os
import sys
import io
import math
import time
import hashlib
import struct
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import defaultdict, Counter

BASE_DIR = Path(__file__).parent.resolve()
ASSETS_DIR = BASE_DIR / "BrawlAssets"
PREVIEWS_DIR = BASE_DIR / "previews"
CONTACT_SHEETS_DIR = BASE_DIR / "contact_sheets"
ASSETS_JSON = BASE_DIR / "assets.json"
SEARCH_INDEX = BASE_DIR / "search_index.json"

# Filename may contain characters not valid on some filesystems
INVALID_FS_CHARS = str.maketrans('', '', '<>:"|?*')

# Preview sizes per category
PREVIEW_SIZES = {
    "Brawlers": 512,
    "Backgrounds": 512,
    "LoadingScreens": 512,
    "Wallpapers": 512,
    "Misc": 512,
    "Animations": 512,
    "UI": 256,
    "Logos": 256,
    "Icons": 256,
    "Portraits": 256,
    "Emojis": 256,
    "Pins": 128,
    "Sprays": 128,
}

WEBP_QUALITY = 78
WEBP_METHOD = 4
MAX_CONVERT_WORKERS = 8

# Contact sheet config
CS_CELL_SIZE = 160
CS_LABEL_HEIGHT = 24
CS_COLUMNS = 35
CS_MAX_WIDTH = 6000


def ensure_dir(p):
    p.mkdir(parents=True, exist_ok=True)

def asset_rel_path(entry):
    """Return relative path like 'Brawlers/8bit/file.png' matching how files were downloaded."""
    cat = entry["category"]
    sub = entry.get("subcategory", "General")
    stem = entry.get("display_name", entry["id"]).replace(" ", "_")
    ext = entry.get("extension", "png").lstrip(".")
    fname = f"{stem}.{ext}"
    fname_clean = fname.translate(INVALID_FS_CHARS)
    return f"{cat}/{sub}/{fname_clean}"

def original_path(entry):
    return ASSETS_DIR / asset_rel_path(entry)

def get_preview_path(entry):
    rel = Path(asset_rel_path(entry))
    return PREVIEWS_DIR / rel.with_suffix(".webp")


# ── Phase 1: WebP Conversion ──────────────────────────────────────────
def convert_to_webp(entry):
    """Convert single asset to WebP preview."""
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    try:
        original = original_path(entry)
        if not original.exists():
            return (entry, False, "original_not_found")

        # Determine preview size
        max_size = PREVIEW_SIZES.get(entry["category"], 256)

        preview = get_preview_path(entry)
        if preview.exists():
            return (entry, True, "exists")

        img = Image.open(str(original))
        orig_w, orig_h = img.size

        # Resize: longest side = max_size, never upscale
        w, h = img.size
        if max(w, h) > max_size:
            if w > h:
                new_w = max_size
                new_h = max(1, int(h * max_size / w))
            else:
                new_h = max_size
                new_w = max(1, int(w * max_size / h))
            img = img.resize((new_w, new_h), Image.LANCZOS)

        # Preserve alpha
        if img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGBA")
        elif img.mode != "RGB":
            img = img.convert("RGB")

        ensure_dir(preview.parent)
        img.save(str(preview), "WEBP", quality=WEBP_QUALITY,
                 method=WEBP_METHOD, lossless=False)
        return (entry, True, "ok")
    except Exception as e:
        return (entry, False, str(e)[:60])


def phase1_convert():
    print("=" * 60)
    print("PHASE 1: WebP Conversion")
    print("=" * 60)

    with open(ASSETS_JSON) as f:
        entries = json.load(f)

    ensure_dir(PREVIEWS_DIR)
    converted = 0
    skipped = 0
    failed = 0
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=MAX_CONVERT_WORKERS) as ex:
        futures = {ex.submit(convert_to_webp, e): e for e in entries}
        for i, future in enumerate(as_completed(futures)):
            entry, ok, msg = future.result()
            if ok:
                if msg == "exists":
                    skipped += 1
                else:
                    converted += 1
            else:
                failed += 1

            if (i + 1) % 500 == 0 or i == len(entries) - 1:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(entries)}] converted={converted} skip={skipped} fail={failed} "
                      f"({elapsed:.0f}s)")

    elapsed = time.time() - t0
    total = converted + skipped
    print(f"\n  Result: {total} previews ({converted} new, {skipped} cached, {failed} failed)")
    print(f"  Time: {elapsed/60:.1f} min")
    return entries


# ── Phase 2: Image Statistics ──────────────────────────────────────────
def extract_stats(entry):
    """Extract rich visual statistics from a preview image."""
    from PIL import Image, ImageFilter, ImageStat
    import math
    Image.MAX_IMAGE_PIXELS = None

    try:
        preview = get_preview_path(entry)
        if not preview.exists():
            return (entry, {"error": "no_preview"})

        img = Image.open(str(preview))
        w, h = img.size

        has_alpha = img.mode in ("RGBA", "LA")
        if has_alpha:
            rgb = img.convert("RGBA")
            alpha = rgb.split()[3]
            alpha_data = list(alpha.getdata())
            total_px = len(alpha_data)
            transparent_px = sum(1 for a in alpha_data if a < 10)
            semi_px = sum(1 for a in alpha_data if 10 <= a < 254)
            opacity_px = total_px - transparent_px - semi_px
            transparency_ratio = round(transparent_px / total_px, 4) if total_px > 0 else 0
        else:
            rgb = img.convert("RGB")
            transparency_ratio = 0.0

        # Convert to RGB for analysis
        rgb_img = img.convert("RGB") if img.mode != "RGB" else img.copy()
        pixels = list(rgb_img.getdata())
        num_pixels = len(pixels)

        if num_pixels == 0:
            return (entry, {"error": "empty_image"})

        # Dominant colors (quantized)
        color_counter = Counter()
        for r, g, b in pixels:
            qr, qg, qb = (r // 16) * 16, (g // 16) * 16, (b // 16) * 16
            color_counter[(qr, qg, qb)] += 1

        dominant_colors = []
        total_count = num_pixels
        for (r, g, b), count in color_counter.most_common(8):
            pct = round(count / total_count * 100, 2)
            dominant_colors.append({
                "hex": f"#{r:02x}{g:02x}{b:02x}",
                "rgb": [r, g, b],
                "percentage": pct,
            })

        # Color histogram (16 bins per channel)
        hist_r = [0] * 16
        hist_g = [0] * 16
        hist_b = [0] * 16
        for r, g, b in pixels:
            hist_r[r // 16] += 1
            hist_g[g // 16] += 1
            hist_b[b // 16] += 1

        total_rgb = sum(hist_r) or 1
        histogram = {
            "r": [round(c / total_rgb, 4) for c in hist_r],
            "g": [round(c / total_rgb, 4) for c in hist_g],
            "b": [round(c / total_rgb, 4) for c in hist_b],
        }

        # Brightness (perceived luminance)
        luminance = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b in pixels]
        avg_brightness = round(sum(luminance) / len(luminance) / 255, 4) if luminance else 0

        # Contrast (std of luminance)
        mean_l = sum(luminance) / len(luminance) if luminance else 0
        variance = sum((l - mean_l) ** 2 for l in luminance) / len(luminance) if luminance else 0
        contrast = round(math.sqrt(variance) / 255, 4)

        # Average hue and saturation
        hues = []
        saturations = []
        lightnesses = []
        for r, g, b in pixels:
            mn, mx = min(r, g, b) / 255, max(r, g, b) / 255
            l = (mn + mx) / 2
            lightnesses.append(l)
            if mx - mn < 0.01:
                hues.append(0)
                saturations.append(0)
                continue
            s = (mx - mn) / (1 - abs(2 * l - 1)) if (1 - abs(2 * l - 1)) > 0 else 0
            saturations.append(s)
            # Hue calculation
            rn, gn, bn = r / 255, g / 255, b / 255
            if mx == rn:
                h = 60 * ((gn - bn) / (mx - mn)) % 360
            elif mx == gn:
                h = 60 * ((bn - rn) / (mx - mn)) + 120
            else:
                h = 60 * ((rn - gn) / (mx - mn)) + 240
            hues.append(h)

        avg_hue = round(sum(hues) / len(hues), 2) if hues else 0
        avg_saturation = round(sum(saturations) / len(saturations), 4) if saturations else 0
        avg_lightness = round(sum(lightnesses) / len(lightnesses), 4) if lightnesses else 0

        # Edge density (using simple gradient)
        gray = rgb_img.convert("L")
        edge_img = gray.filter(ImageFilter.FIND_EDGES)
        edge_pixels = list(edge_img.getdata())
        edge_density = round(sum(1 for p in edge_pixels if p > 50) / len(edge_pixels), 4) if edge_pixels else 0

        # Visual complexity: ratio of unique colors to total pixels
        unique_colors = len(set(pixels[:min(5000, len(pixels))]))
        visual_complexity = round(unique_colors / min(5000, num_pixels), 4) if num_pixels > 0 else 0

        # Orientation classification
        if w > h * 1.2:
            orientation = "landscape"
        elif h > w * 1.2:
            orientation = "portrait"
        else:
            orientation = "square"

        stats = {
            "width": w,
            "height": h,
            "orientation": orientation,
            "transparent": has_alpha,
            "transparency_ratio": transparency_ratio,
            "dominant_colors": dominant_colors,
            "color_histogram": histogram,
            "brightness": avg_brightness,
            "contrast": contrast,
            "saturation": avg_saturation,
            "average_hue": avg_hue,
            "average_lightness": avg_lightness,
            "edge_density": edge_density,
            "visual_complexity": visual_complexity,
            "aspect_ratio": round(w / h, 4) if h > 0 else 0,
        }
        return (entry, stats)
    except Exception as e:
        return (entry, {"error": str(e)[:60]})


def load_entries():
    """Load asset entries from assets.json (which has filename)."""
    with open(ASSETS_JSON) as f:
        return json.load(f)

def phase2_stats(entries):
    print("\n" + "=" * 60)
    print("PHASE 2: Image Statistics Extraction")
    print("=" * 60)

    all_stats = []
    t0 = time.time()

    with ThreadPoolExecutor(max_workers=MAX_CONVERT_WORKERS) as ex:
        futures = {ex.submit(extract_stats, e): e for e in entries}
        for i, future in enumerate(as_completed(futures)):
            entry, stats = future.result()
            all_stats.append((entry["id"], stats))
            if (i + 1) % 500 == 0:
                print(f"  [{i+1}/{len(entries)}] processed")

    elapsed = time.time() - t0
    print(f"  Time: {elapsed/60:.1f} min")
    return {sid: s for sid, s in all_stats}


def phase2b_update_assets(stats_map):
    """Append visual statistics into assets.json."""
    print("\n  Updating assets.json with visual statistics...")
    if not ASSETS_JSON.exists():
        print("  assets.json not found, skipping")
        return

    with open(ASSETS_JSON) as f:
        assets = json.load(f)

    updated = 0
    for asset in assets:
        aid = asset["id"]
        if aid in stats_map:
            s = stats_map[aid]
            if "error" not in s:
                asset["preview_width"] = s.get("width", 0)
                asset["preview_height"] = s.get("height", 0)
                asset["dominant_colors"] = s.get("dominant_colors", [])
                asset["brightness"] = s.get("brightness", 0)
                asset["contrast"] = s.get("contrast", 0)
                asset["saturation"] = s.get("saturation", 0)
                asset["transparency_ratio"] = s.get("transparency_ratio", 0)
                asset["edge_density"] = s.get("edge_density", 0)
                asset["average_hue"] = s.get("average_hue", 0)
                asset["average_lightness"] = s.get("average_lightness", 0)
                asset["color_histogram"] = s.get("color_histogram", {})
                asset["visual_complexity"] = s.get("visual_complexity", 0)
                asset["orientation"] = s.get("orientation", asset.get("orientation", ""))
                updated += 1

    with open(ASSETS_JSON, "w") as f:
        json.dump(assets, f, indent=2)
    print(f"  Updated {updated} assets")


def phase2c_manifest(stats_map, entries):
    """Generate preview_manifest.json."""
    print("\n  Generating preview_manifest.json...")
    manifest = []
    for entry in entries:
        aid = entry["id"]
        s = stats_map.get(aid, {})
        prv = Path(asset_rel_path(entry)).with_suffix(".webp")
        manifest.append({
            "id": aid,
            "display_name": entry.get("display_name", ""),
            "preview_path": f"previews/{prv}",
            "original_filename": entry.get("filename", ""),
            "original_url": entry.get("url", ""),
            "preview_width": s.get("width", 0),
            "preview_height": s.get("height", 0),
            "original_width": entry.get("width", 0),
            "original_height": entry.get("height", 0),
            "filesize": s.get("filesize", 0),
        })

    with open(BASE_DIR / "preview_manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"  {len(manifest)} entries")


# ── Phase 3: Contact Sheets ───────────────────────────────────────────
def build_contact_sheet(entries, sheet_name, img_size=(128, 128),
                        columns=35, max_width=6000):
    """Build a contact sheet from a list of asset entries."""
    from PIL import Image, ImageDraw, ImageFont

    cell_w = img_size[0] + 8
    cell_h = img_size[1] + CS_LABEL_HEIGHT + 8

    if columns * cell_w > max_width:
        columns = max(1, max_width // cell_w)

    rows_per_page = max(1, (6000 - CS_LABEL_HEIGHT) // cell_h) if False else 40
    sheet_width = min(columns * cell_w, max_width)

    sheets = []
    current_img = None
    current_draw = None
    current_y = 0
    current_col = 0
    current_row = 0
    page = 0
    coord_map = {}

    # Try to load a font
    try:
        font = ImageFont.truetype("/system/fonts/DroidSans.ttf", 10)
    except:
        font = ImageFont.load_default()

    for entry in entries:
        aid = entry["id"]
        pv = get_preview_path(entry)

        if not pv.exists():
            continue

        try:
            thumb = Image.open(str(pv))
            thumb = thumb.resize(img_size, Image.LANCZOS)
            if thumb.mode != "RGBA":
                thumb = thumb.convert("RGBA")
        except:
            continue

        if current_img is None:
            page += 1
            sheet_w = sheet_width
            sheet_h = rows_per_page * cell_h + CS_LABEL_HEIGHT
            current_img = Image.new("RGBA", (sheet_w, sheet_h), (30, 30, 30, 255))
            current_draw = ImageDraw.Draw(current_img)
            # Page label
            current_draw.text((10, 4), f"{sheet_name} — Page {page}", fill=(200, 200, 200, 255), font=font)
            current_y = CS_LABEL_HEIGHT + 4
            current_row = 0
            current_col = 0

        x = 4 + current_col * cell_w
        y = current_y + current_row * cell_h

        # Paste thumbnail
        if current_img is not None:
            current_img.paste(thumb, (x, y), thumb)
            # Label
            label = entry.get("display_name", aid)[:18]
            current_draw.text((x, y + img_size[1] + 2), label, fill=(180, 180, 180, 255), font=font)

        coord_map[aid] = {
            "sheet": f"{sheet_name}_p{page:02d}.webp",
            "x": x,
            "y": y,
            "width": img_size[0],
            "height": img_size[1],
        }

        current_col += 1
        if current_col >= columns:
            current_col = 0
            current_row += 1
            if current_row >= rows_per_page:
                # Save page
                sheet_path = CONTACT_SHEETS_DIR / f"{sheet_name}_p{page:02d}.webp"
                ensure_dir(sheet_path.parent)
                current_img.save(str(sheet_path), "WEBP", quality=85, method=4)
                sheets.append(str(sheet_path))
                current_img = None

    # Save last page
    if current_img is not None:
        # Trim empty space
        sheet_path = CONTACT_SHEETS_DIR / f"{sheet_name}_p{page:02d}.webp"
        ensure_dir(sheet_path.parent)
        # Crop to actual content
        bbox = current_img.getbbox()
        if bbox:
            current_img = current_img.crop(bbox)
        current_img.save(str(sheet_path), "WEBP", quality=85, method=4)
        sheets.append(str(sheet_path))

    return sheets, coord_map


def phase3_contact_sheets(entries):
    print("\n" + "=" * 60)
    print("PHASE 3: Contact Sheets")
    print("=" * 60)

    # Group by category
    from PIL import Image
    from PIL import ImageDraw
    from PIL import ImageFont

    cat_groups = defaultdict(list)
    for e in entries:
        cat_groups[e["category"]].append(e)

    # Sort each group
    for cat in cat_groups:
        cat_groups[cat].sort(key=lambda x: x.get("display_name", ""))

    ensure_dir(CONTACT_SHEETS_DIR)
    all_coords = {}

    # Per-category sheets
    for cat, group in sorted(cat_groups.items(), key=lambda x: -len(x[1])):
        thumb_size = (128, 128) if cat in ("Pins", "Sprays") else (136, 136)
        print(f"  {cat}: {len(group)} assets...")
        sheets, coords = build_contact_sheet(
            group, cat.lower().replace(" ", "_"),
            img_size=thumb_size,
            columns=35,
        )
        all_coords.update(coords)
        print(f"    -> {len(sheets)} sheets")

    # Global contact sheet (sample every 5th asset)
    print(f"\n  Global: {len(entries)} assets (sampling)...")
    global_entries = entries  # All entries
    # For global, use smaller thumbnails
    sheets, global_coords = build_contact_sheet(
        global_entries, "global",
        img_size=(96, 96),
        columns=40,
    )
    all_coords.update(global_coords)

    # Write coordinate index
    coord_index = []
    for aid, coord in all_coords.items():
        coord_index.append({
            "asset_id": aid,
            "sheet": coord["sheet"],
            "x": coord["x"],
            "y": coord["y"],
            "width": coord["width"],
            "height": coord["height"],
        })

    with open(CONTACT_SHEETS_DIR / "index.json", "w") as f:
        json.dump(coord_index, f, indent=2)
    print(f"  Coordinate index: {len(coord_index)} entries")


# ── Phase 4: AI Indexes ───────────────────────────────────────────────
def phase4_indexes(entries, stats_map):
    print("\n" + "=" * 60)
    print("PHASE 4: AI Indexes")
    print("=" * 60)

    # ── visual_index.json ──
    print("  visual_index.json...")
    vis_idx = []
    for e in entries:
        s = stats_map.get(e["id"], {})
        if "error" in s:
            continue
        vis_idx.append({
            "id": e["id"],
            "name": e.get("display_name", ""),
            "brightness": s.get("brightness", 0),
            "contrast": s.get("contrast", 0),
            "saturation": s.get("saturation", 0),
            "edge_density": s.get("edge_density", 0),
            "visual_complexity": s.get("visual_complexity", 0),
            "average_hue": s.get("average_hue", 0),
            "average_lightness": s.get("average_lightness", 0),
            "transparency_ratio": s.get("transparency_ratio", 0),
            "orientation": s.get("orientation", ""),
            "aspect_ratio": s.get("aspect_ratio", 0),
        })
    with open(BASE_DIR / "visual_index.json", "w") as f:
        json.dump(vis_idx, f, indent=2)
    print(f"    {len(vis_idx)} entries")

    # ── color_index.json ──
    print("  color_index.json...")
    color_idx = {}
    for e in entries:
        s = stats_map.get(e["id"], {})
        if "error" in s:
            continue
        for dc in s.get("dominant_colors", []):
            hexc = dc["hex"]
            if hexc not in color_idx:
                color_idx[hexc] = {
                    "hex": hexc,
                    "rgb": dc["rgb"],
                    "asset_ids": [],
                    "total_percentage": 0,
                }
            color_idx[hexc]["asset_ids"].append(e["id"])
            color_idx[hexc]["total_percentage"] += dc["percentage"]

    # Sort by frequency
    color_sorted = sorted(color_idx.values(), key=lambda x: -x["total_percentage"])
    with open(BASE_DIR / "color_index.json", "w") as f:
        json.dump(color_sorted[:500], f, indent=2)  # Top 500 colors
    print(f"    {len(color_sorted)} unique colors (top 500 saved)")

    # ── theme_index.json ──
    print("  theme_index.json...")
    theme_idx = defaultdict(lambda: {"count": 0, "asset_ids": [],
                                       "avg_brightness": 0, "avg_saturation": 0})
    brightness_sum = defaultdict(float)
    sat_sum = defaultdict(float)
    for e in entries:
        theme = e.get("theme") or "none"
        theme_idx[theme]["count"] += 1
        theme_idx[theme]["asset_ids"].append(e["id"])
        s = stats_map.get(e["id"], {})
        if "error" not in s:
            brightness_sum[theme] += s.get("brightness", 0)
            sat_sum[theme] += s.get("saturation", 0)

    for t in theme_idx:
        c = theme_idx[t]["count"]
        theme_idx[t]["avg_brightness"] = round(brightness_sum[t] / c, 4) if c > 0 else 0
        theme_idx[t]["avg_saturation"] = round(sat_sum[t] / c, 4) if c > 0 else 0

    with open(BASE_DIR / "theme_index.json", "w") as f:
        json.dump(dict(theme_idx), f, indent=2)
    print(f"    {len(theme_idx)} themes")

    # ── brawler_index.json ──
    print("  brawler_index.json...")
    brawler_idx = defaultdict(lambda: {"count": 0, "asset_ids": [],
                                         "avg_brightness": 0, "avg_saturation": 0,
                                         "avg_edge_density": 0})
    for e in entries:
        b = e.get("brawler") or "none"
        brawler_idx[b]["count"] += 1
        brawler_idx[b]["asset_ids"].append(e["id"])
        s = stats_map.get(e["id"], {})
        if "error" not in s:
            brightness_sum[b] += s.get("brightness", 0)
            sat_sum[b] += s.get("saturation", 0)

    for b in brawler_idx:
        c = brawler_idx[b]["count"]
        brawler_idx[b]["avg_brightness"] = round(brightness_sum.get(b, 0) / c, 4) if c > 0 else 0
        brawler_idx[b]["avg_saturation"] = round(sat_sum.get(b, 0) / c, 4) if c > 0 else 0
        # Skin names
        skins = set()
        for e in entries:
            if e.get("brawler") == b and e.get("skin"):
                skins.add(e["skin"])
        brawler_idx[b]["skins"] = sorted(skins)

    with open(BASE_DIR / "brawler_index.json", "w") as f:
        json.dump(dict(brawler_idx), f, indent=2)
    print(f"    {len(brawler_idx)} brawlers")

    # ── category_index.json ──
    print("  category_index.json...")
    cat_idx = defaultdict(lambda: {"count": 0, "asset_ids": [],
                                     "avg_brightness": 0, "avg_visual_complexity": 0})
    for e in entries:
        c = e["category"]
        cat_idx[c]["count"] += 1
        cat_idx[c]["asset_ids"].append(e["id"])
        s = stats_map.get(e["id"], {})
        if "error" not in s:
            brightness_sum[c] += s.get("brightness", 0)
            sat_sum[c] += s.get("visual_complexity", 0)

    for c in cat_idx:
        cnt = cat_idx[c]["count"]
        cat_idx[c]["avg_brightness"] = round(brightness_sum.get(c, 0) / cnt, 4) if cnt > 0 else 0
        cat_idx[c]["avg_visual_complexity"] = round(sat_sum.get(c, 0) / cnt, 4) if cnt > 0 else 0

    with open(BASE_DIR / "category_index.json", "w") as f:
        json.dump(dict(cat_idx), f, indent=2)
    print(f"    {len(cat_idx)} categories")


# ── Phase 5: Attempt Embeddings ───────────────────────────────────────
def phase5_embeddings(entries):
    print("\n" + "=" * 60)
    print("PHASE 5: Embeddings (optional)")
    print("=" * 60)

    try:
        import numpy as np
        print("  numpy available, checking for CLIP...")
    except ImportError:
        print("  numpy not installed. Skipping embeddings.")
        return

    try:
        # Try loading CLIP
        import torch
        import clip
        print("  CLIP found! Generating embeddings...")

        device = "cpu"
        model, preprocess = clip.load("ViT-B/32", device=device)
        print(f"  Model loaded on {device}")
    except ImportError:
        print("  CLIP not available (torch + clip).")
        print("  To enable embeddings: pip install torch torchvision ftfy")
        return
    except Exception as e:
        print(f"  CLIP load failed: {e}")
        return

    import numpy as np

    embeddings_list = []
    embedding_map = {}
    batch = []
    batch_ids = []
    batch_size = 32

    from PIL import Image as PILImage

    t0 = time.time()
    for i, entry in enumerate(entries):
        pv_path = get_preview_path(entry)
        if not pv_path.exists():
            continue

        try:
            img = PILImage.open(str(pv_path)).convert("RGB")
            img_input = preprocess(img).unsqueeze(0).to(device)
            batch.append(img_input)
            batch_ids.append(entry["id"])

            if len(batch) >= batch_size:
                with torch.no_grad():
                    features = model.encode_image(torch.cat(batch))
                    features = features / features.norm(dim=-1, keepdim=True)
                for bid, feat in zip(batch_ids, features.cpu().numpy()):
                    embeddings_list.append(feat)
                    embedding_map[bid] = len(embeddings_list) - 1
                batch = []
                batch_ids = []

            if (i + 1) % 500 == 0:
                print(f"  [{i+1}/{len(entries)}] {len(embeddings_list)} embeddings")
        except:
            continue

    # Process remainder
    if batch:
        with torch.no_grad():
            features = model.encode_image(torch.cat(batch))
            features = features / features.norm(dim=-1, keepdim=True)
        for bid, feat in zip(batch_ids, features.cpu().numpy()):
            embeddings_list.append(feat)
            embedding_map[bid] = len(embeddings_list) - 1

    # Save
    embeddings_np = np.array(embeddings_list, dtype=np.float32)
    np.save(str(BASE_DIR / "embeddings.npy"), embeddings_np)

    embed_json = [{"id": aid, "embedding_index": idx}
                  for aid, idx in embedding_map.items()]
    with open(BASE_DIR / "embeddings.json", "w") as f:
        json.dump(embed_json, f, indent=2)

    elapsed = time.time() - t0
    print(f"\n  Generated {len(embeddings_list)} embeddings")
    print(f"  Shape: {embeddings_np.shape}")
    print(f"  Time: {elapsed/60:.1f} min")


# ── Final Report ────────────────────────────────────────────────────────
def generate_report(entries_count, stats_map, t_start):
    print("\n" + "=" * 60)
    print("AI VISION PACK — BUILD REPORT")
    print("=" * 60)

    # Count previews
    preview_files = list(PREVIEWS_DIR.rglob("*.webp"))
    preview_total = sum(f.stat().st_size for f in preview_files)
    preview_count = len(preview_files)

    # Count contact sheets
    cs_files = list(CONTACT_SHEETS_DIR.rglob("*.webp"))
    cs_total = sum(f.stat().st_size for f in cs_files)
    cs_count = len(cs_files)

    # Original size
    orig_files = list(ASSETS_DIR.rglob("*"))
    orig_total = sum(f.stat().st_size for f in orig_files if f.is_file())
    orig_count = len([f for f in orig_files if f.is_file()])

    compression_ratio = preview_total / orig_total if orig_total > 0 else 0

    # Stats coverage
    stats_ok = sum(1 for s in stats_map.values() if "error" not in s)
    stats_fail = sum(1 for s in stats_map.values() if "error" in s)

    elapsed = time.time() - t_start

    print(f"""
  Originals:     {orig_count} files, {orig_total/1024/1024:.0f}MB
  Previews:      {preview_count} files, {preview_total/1024/1024:.0f}MB
  Compression:   {compression_ratio*100:.1f}%  ({1/compression_ratio:.0f}x smaller)
  Contact Sheets: {cs_count} files, {cs_total/1024/1024:.0f}MB

  Assets indexed: {entries_count}
  Stats extracted: {stats_ok} ok, {stats_fail} failed
  Categories:    10
  Brawlers:      83
  Themes:        {len(set(e.get('theme','') for e in json.load(open(SEARCH_INDEX)) if e.get('theme')))}

  Build time:    {elapsed/60:.1f} min

  Output files:
    previews/                  — {preview_count} WebP previews
    preview_manifest.json      — Preview metadata
    contact_sheets/            — {cs_count} contact sheet pages
    visual_index.json          — Visual similarity rankings
    color_index.json           — Color-based search
    theme_index.json           — Theme visual profiles
    brawler_index.json         — Brawler visual profiles
    category_index.json        — Category visual profiles
""" + ("    embeddings.npy + embeddings.json   — CLIP embeddings\n" if (BASE_DIR / "embeddings.npy").exists() else ""))

    print("=" * 60)


# ── Main ────────────────────────────────────────────────────────────────
def main():
    t_start = time.time()

    print(r"""
  ╔══════════════════════════════════════════════════╗
  ║         Brawl Stars AI Vision Pack v1.0          ║
  ╚══════════════════════════════════════════════════╝
    """)

    # Phase 1: Convert (uses assets.json internally)
    phase1_convert()

    # Load entries for subsequent phases
    entries = load_entries()

    # Phase 2: Stats
    stats_map = phase2_stats(entries)
    phase2b_update_assets(stats_map)
    phase2c_manifest(stats_map, entries)

    # Phase 3: Contact Sheets
    phase3_contact_sheets(entries)

    # Phase 4: Indexes
    phase4_indexes(entries, stats_map)

    # Phase 5: Embeddings (optional)
    phase5_embeddings(entries)

    # Report
    generate_report(len(entries), stats_map, t_start)

    print("\n✅ AI Vision Pack complete!")
    print(f"   Preview library: {PREVIEWS_DIR}")
    print(f"   Contact sheets:  {CONTACT_SHEETS_DIR}")


if __name__ == "__main__":
    main()
