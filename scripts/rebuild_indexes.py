#!/usr/bin/env python3
"""Rebuild all JSON indexes from raw assets + CDN + BrawlAPI."""
import json, hashlib, subprocess, sys, re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
DATA_DIR = BASE / "data"
ASSETS_JSON = DATA_DIR / "assets.json"
BRAWLERS_JSON = DATA_DIR / "brawlers.json"
SEARCH_INDEX = DATA_DIR / "search_index.json"
MANIFEST = DATA_DIR / "fankit_manifest.json"
PREVIEW_MANIFEST = DATA_DIR / "preview_manifest.json"
CDN_DIR = BASE / "_cdn_brawlers"
SKINS_JSON = DATA_DIR / "skins.json"
THEMES_JSON = DATA_DIR / "themes.json"
CATEGORIES_JSON = DATA_DIR / "categories.json"

BRAWLIKE_URL = "https://api.brawlapi.com/v1/brawlers"
CDN_URL = "https://cdn.brawlify.com/brawlers"

INVALID_FS_CHARS = str.maketrans('', '', '<>:"|?*')

def normalize(s):
    return s.lower().replace(".", "").replace("-", "").replace(" ", "").replace("&", "and").replace("'", "").replace("_", "")

def fetch_json(url):
    r = subprocess.run(["curl", "-s", url], capture_output=True, text=True, timeout=30)
    return json.loads(r.stdout)

def download_file(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return True
    r = subprocess.run(["curl", "-sL", "-o", str(path), url], capture_output=True, text=True, timeout=60)
    return r.returncode == 0 and path.exists() and path.stat().st_size > 1000

def asset_id(prefix, name):
    return hashlib.md5(f"cdn:{prefix}:{name}".encode()).hexdigest()[:16]

def classify_asset(path):
    """Classify a raw asset into category/subcategory/display_name based on path."""
    stem = path.stem
    parts = stem.split("_")
    if len(parts) >= 3 and parts[0].lower() in ("profile", "player"):
        cat = "UI"
        sub = "Icons"
        dn = stem
    elif any(kw in stem.lower() for kw in ["pin", "angry", "happy", "sad", "gg", "clap", "facepalm", "phew", "thanks", "stop", "special"]):
        cat = "Pins"
        sub = parts[-1].capitalize() if parts[-1].lower() in ("angry","happy","sad","gg","clap","facepalm","phew","thanks","stop","special","default") else "Default"
        dn = stem
    elif any(kw in stem.lower() for kw in ["portrait", "portrate"]):
        cat = "Portraits"
        sub = "Unknown"
        dn = stem
    elif any(kw in stem.lower() for kw in ["background", "bg"]):
        cat = "Backgrounds"
        sub = "General"
        dn = stem
    elif any(kw in stem.lower() for kw in ["spray"]):
        cat = "Sprays"
        sub = "All"
        dn = stem
    elif any(kw in stem.lower() for kw in ["emoji", "emote"]):
        cat = "Emojis"
        sub = "All"
        dn = stem
    elif any(kw in stem.lower() for kw in ["logo", "splash", "loading"]):
        cat = "LoadingScreens"
        sub = "General"
        dn = stem
    else:
        cat = "Brawlers"
        sub = parts[0].lower().replace(" ", "_") if parts else "general"
        dn = stem

    return cat, sub, dn

def main():
    print("=" * 60)
    print("Rebuild Indexes")
    print("=" * 60)

    # 1. Fetch BrawlAPI
    print("\n[1] Fetching BrawlAPI...")
    api_data = fetch_json(BRAWLIKE_URL)
    api_brawlers = api_data["list"]
    print(f"    {len(api_brawlers)} brawlers")

    # 2. Index raw assets
    print("\n[2] Indexing raw assets...")
    assets = []
    if RAW_DIR.exists():
        for f in sorted(RAW_DIR.rglob("*")):
            if f.is_file() and f.suffix.lower() in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
                cat, sub, dn = classify_asset(f)
                aid = hashlib.md5(f.name.encode()).hexdigest()[:16]
                ext = f.suffix.lstrip(".")
                entry = {
                    "id": aid,
                    "filename": f.name,
                    "category": cat,
                    "subcategory": sub,
                    "extension": f".{ext}",
                    "display_name": dn,
                    "url": "",
                    "source": "fankit",
                    "width": 0,
                    "height": 0,
                    "tags": [cat.lower(), sub.lower()],
                    "brawler": None,
                }
                assets.append(entry)
    print(f"    Fankit assets: {len(assets)}")

    # 3. Download CDN portraits for brawlers with no Brawlers assets
    print("\n[3] Checking for missing CDN portraits...")
    CDN_DIR.mkdir(parents=True, exist_ok=True)

    # Build set of brawler names present in fankit Brawlers assets
    fankit_brawler_names = set()
    for a in assets:
        if a["category"] == "Brawlers":
            name = a["display_name"].split("_")[0] if "_" in a["display_name"] else a["display_name"]
            fankit_brawler_names.add(normalize(name))

    cdn_new = []
    for b in api_brawlers:
        name = b["name"]
        fankit_norm = normalize(b.get("fankit", name))
        name_norm = normalize(name)

        has_brawler_asset = False
        for a in assets:
            dn_norm = normalize(a.get("display_name", ""))
            if a["category"] == "Brawlers" and (fankit_norm in dn_norm or name_norm in dn_norm):
                has_brawler_asset = True
                break

        if not has_brawler_asset:
            slug = fankit_norm
            images = [
                ("bordered", b.get("imageUrl"), "Brawlers"),
                ("borderless", b.get("imageUrl2"), "Brawlers"),
                ("emoji", b.get("imageUrl3"), "Emojis"),
            ]
            for img_type, url, category in images:
                if not url:
                    continue
                ext = url.split(".")[-1] if "." in url else "png"
                fname = f"{b.get('fankit', name)}_{img_type}.{ext}"
                local = CDN_DIR / fname
                if download_file(url, local):
                    aid = asset_id(img_type, name.lower())
                    stem = fname.rsplit(".", 1)[0]
                    entry = {
                        "id": aid,
                        "filename": fname,
                        "category": category,
                        "subcategory": slug,
                        "extension": f".{ext}",
                        "display_name": stem,
                        "url": url,
                        "source": "brawlify_cdn",
                        "width": 0,
                        "height": 0,
                        "tags": [name.lower(), img_type, "brawlify"],
                        "brawler": name,
                    }
                    assets.append(entry)
                    cdn_new.append(entry)
                    print(f"    + {name:20s} {img_type}")

    print(f"    CDN new entries: {len(cdn_new)}")

    # 4. Assign brawler field for all assets
    print("\n[4] Assigning brawler fields...")
    for a in assets:
        dn_norm = normalize(a.get("display_name", ""))
        for b in api_brawlers:
            fankit_norm = normalize(b.get("fankit", b["name"]))
            name_norm = normalize(b["name"])
            if fankit_norm in dn_norm or name_norm in dn_norm:
                a["brawler"] = b["name"]
                break

    # 5. Save assets.json
    print(f"\n[5] Saving assets.json ({len(assets)} entries)...")
    with open(ASSETS_JSON, "w") as f:
        json.dump(assets, f, indent=2)

    # 6. Build brawlers.json
    print("\n[6] Building brawlers.json...")
    brawler_assets = {b["name"].lower(): [] for b in api_brawlers}
    for a in assets:
        bname = a.get("brawler")
        if bname and bname.lower() in brawler_assets:
            brawler_assets[bname.lower()].append(a["id"])
        else:
            for b in api_brawlers:
                if normalize(b["name"]) in normalize(a.get("display_name", "")):
                    brawler_assets[b["name"].lower()].append(a["id"])
                    break

    new_brawlers = {}
    for b in api_brawlers:
        name = b["name"]
        key = name.lower().replace(" ", "_").replace("-", "_").replace("&", "and").replace(".", "").replace("'", "")
        asset_ids = brawler_assets.get(name.lower(), [])

        skin_names = set()
        for a in assets:
            if a["id"] in asset_ids:
                dn = a.get("display_name", "")
                if " " in dn and "Portrait" not in dn and "Pin" not in dn and "Emoji" not in dn:
                    parts = dn.split()
                    if len(parts) >= 3:
                        skin_names.add(parts[1])

        asset_types = {}
        for a in assets:
            if a["id"] in asset_ids:
                cat = a.get("category", "Misc")
                if cat not in asset_types:
                    asset_types[cat] = []
                asset_types[cat].append(a["id"])

        new_brawlers[key] = {
            "name": name,
            "rarity": b["rarity"]["name"],
            "class": b["class"]["name"],
            "color": b["rarity"].get("color", "#888888"),
            "total_assets": len(asset_ids),
            "skins": sorted(skin_names) if skin_names else [],
            "asset_types": {k: v for k, v in sorted(asset_types.items())},
        }

    with open(BRAWLERS_JSON, "w") as f:
        json.dump(new_brawlers, f, indent=2)
    print(f"    {len(new_brawlers)} brawlers")

    # 7. Build search_index.json
    print("\n[7] Building search_index.json...")
    search_index = []
    for a in assets:
        search_index.append({
            "id": a["id"],
            "display_name": a.get("display_name", ""),
            "category": a.get("category", ""),
            "subcategory": a.get("subcategory", ""),
            "brawler": a.get("brawler", ""),
            "tags": a.get("tags", []),
            "url": a.get("url", ""),
            "filename": a.get("filename", ""),
            "extension": a.get("extension", ""),
            "width": a.get("width", 0),
            "height": a.get("height", 0),
            "source": a.get("source", "fankit"),
        })
    with open(SEARCH_INDEX, "w") as f:
        json.dump(search_index, f, indent=2)
    print(f"    {len(search_index)} entries")

    # 8. Build preview_manifest.json (scans actual previews)
    print("\n[8] Building preview_manifest.json...")
    previews_dir = BASE / "previews"
    manifest = []
    for a in assets:
        cat = a["category"]
        sub = a.get("subcategory", "General")
        stem = a.get("display_name", a["id"]).replace(" ", "_")
        fname_clean = f"{stem}.{a.get('extension', 'png').lstrip('.')}".translate(INVALID_FS_CHARS)

        pv_file = previews_dir / cat / sub / f"{stem}.webp"
        pw, ph, fsize = 0, 0, 0
        if pv_file.exists():
            fsize = pv_file.stat().st_size
            try:
                from PIL import Image
                with Image.open(str(pv_file)) as img:
                    pw, ph = img.size
            except:
                pass

        manifest.append({
            "id": a["id"],
            "display_name": a.get("display_name", ""),
            "preview_path": f"previews/{cat}/{sub}/{stem}.webp",
            "original_filename": a.get("filename", ""),
            "original_url": a.get("url", ""),
            "preview_width": pw,
            "preview_height": ph,
            "original_width": a.get("width", 0),
            "original_height": a.get("height", 0),
            "filesize": fsize,
        })

    with open(PREVIEW_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"    {len(manifest)} entries")

    # 9. Generate brawler profiles
    print("\n[9] Generating brawler profiles...")
    profiles_dir = DATA_DIR / "brawler_profiles"
    profiles_dir.mkdir(parents=True, exist_ok=True)

    for key, data in new_brawlers.items():
        bname = data["name"]
        asset_ids = set()
        for cat_ids in data["asset_types"].values():
            asset_ids.update(cat_ids)

        # Collect stats for this brawler's assets
        brawler_assets_list = [a for a in assets if a["id"] in asset_ids]

        lines = []
        lines.append(f"# {bname}")
        lines.append(f"Rarity: {data['rarity']} | Class: {data['class']}")
        lines.append(f"Total assets: {data['total_assets']}")
        if data["skins"]:
            lines.append(f"Skins: {', '.join(data['skins'])}")
        lines.append("")

        # Group by category for display
        for cat in ["Brawlers", "Portraits", "Pins", "Emojis", "Sprays", "Animations", "Backgrounds", "UI"]:
            cat_assets = [a for a in brawler_assets_list if a["category"] == cat]
            if not cat_assets:
                continue
            lines.append(f"\n## {cat} ({len(cat_assets)})")
            for a in sorted(cat_assets, key=lambda x: x.get("display_name", ""))[:10]:
                dn = a.get("display_name", "")
                preview_path = f"previews/{a['category']}/{a['subcategory']}/{dn.replace(' ', '_')}.webp"
                lines.append(f"  - {dn}")
                lines.append(f"    preview: {preview_path}")
            if len(cat_assets) > 10:
                lines.append(f"    ... +{len(cat_assets)-10} more")

        with open(profiles_dir / f"{key}.md", "w") as f:
            f.write("\n".join(lines))

    print(f"    {len(new_brawlers)} profiles generated")

    print("\n" + "=" * 60)
    print(f"DONE")
    print(f"  assets.json:  {len(assets)}")
    print(f"  brawlers.json: {len(new_brawlers)}")
    print(f"  profiles:     {len(new_brawlers)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
