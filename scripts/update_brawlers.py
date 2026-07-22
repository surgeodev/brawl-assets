#!/usr/bin/env python3
"""Update brawlers database with BrawlAPI + CDN portraits for missing brawlers."""
import json, subprocess, sys, time, hashlib
from pathlib import Path

BASE_DIR = Path("/data/data/com.termux/files/home/BrawlAssets")
ASSETS_JSON = BASE_DIR / "assets.json"
BRAWLERS_JSON = BASE_DIR / "brawlers.json"
FANKIT_DIR = BASE_DIR / "BrawlAssets"
CDN_DIR = BASE_DIR / "cdn_brawlers"
PREVIEWS_DIR = BASE_DIR / "previews"

def fetch_json(url):
    result = subprocess.run(
        ["curl", "-s", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl failed: {url}\n{result.stderr}")
    return json.loads(result.stdout)

def normalize(s):
    return s.lower().replace(".", "").replace("-", "").replace(" ", "").replace("&", "and").replace("'", "").replace("_", "")

def asset_id(prefix, name):
    h = hashlib.md5(f"cdn:{prefix}:{name}".encode()).hexdigest()[:16]
    return h

def download_file(url, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return True
    result = subprocess.run(
        ["curl", "-s", "-o", str(path), url],
        capture_output=True, text=True, timeout=60
    )
    if result.returncode == 0 and path.exists() and path.stat().st_size > 1000:
        return True
    print(f"    ERROR downloading {url}")
    return False

def main():
    print("=" * 60)
    print("Update Brawlers — BrawlAPI + CDN")
    print("=" * 60)

    # 1. Load existing data
    print("\n[1] Loading existing data...")
    with open(ASSETS_JSON) as f:
        assets = json.load(f)
    print(f"    assets.json: {len(assets)} entries")

    try:
        with open(BRAWLERS_JSON) as f:
            old_brawlers = json.load(f)
        old_brawler_names = set(k.lower().replace(".", "").replace("-", "").replace(" ", "").replace("&", "").replace("'", "") for k in old_brawlers.keys())
        print(f"    brawlers.json: {len(old_brawlers)} brawlers")
    except:
        old_brawlers = {}
        old_brawler_names = set()
        print("    brawlers.json: not found")

    # 2. Fetch BrawlAPI brawlers
    print("\n[2] Fetching BrawlAPI data...")
    data = fetch_json("https://api.brawlapi.com/v1/brawlers")
    api_brawlers = data["list"]
    print(f"    BrawlAPI: {len(api_brawlers)} brawlers")

    # 3. Classify brawlers: have Fankit assets vs missing
    print("\n[3] Classifying brawlers...")
    have_fankit = []
    missing_from_fankit = []

    for b in api_brawlers:
        name = b["name"]
        fankit_norm = normalize(b.get("fankit", name))

        count = sum(1 for a in assets if fankit_norm in normalize(a.get("display_name", "")))
        
        # Special: Lumi has only generic team pins, not brawler assets
        if name.lower() == "lumi" and count <= 3:
            brawler_renders = sum(1 for a in assets 
                if fankit_norm in normalize(a.get("display_name", ""))
                and a.get("category", "") == "Brawlers")
            if brawler_renders == 0:
                missing_from_fankit.append(b)
                continue

        if count == 0:
            missing_from_fankit.append(b)
        else:
            have_fankit.append(b)

    print(f"    Have Fankit assets: {len(have_fankit)}")
    print(f"    Missing from Fankit: {len(missing_from_fankit)}")
    for b in missing_from_fankit:
        print(f"      - {b['name']:20s} ({b['rarity']['name']})")

    # 4. Download CDN portraits for missing brawlers
    print("\n[4] Downloading CDN portraits...")
    CDN_DIR.mkdir(parents=True, exist_ok=True)

    new_cdn_assets = []
    downloaded = 0
    for b in missing_from_fankit:
        name = b["name"]
        fankit_slug = b.get("fankit", name)
        subcat = fankit_slug.lower().replace(" ", "_").replace("-", "_").replace("&", "and").replace("'", "")

        # 3 image types
        images = [
            ("bordered", b.get("imageUrl", ""), "Brawlers"),
            ("borderless", b.get("imageUrl2", ""), "Brawlers"),
            ("emoji", b.get("imageUrl3", ""), "Emojis"),
        ]

        for img_type, url, category in images:
            if not url:
                continue
            
            ext = url.split(".")[-1] if "." in url else "png"
            fname = f"{fankit_slug}_{img_type}.{ext}"
            local_path = CDN_DIR / fname
            
            ok = download_file(url, local_path)
            if ok:
                downloaded += 1
                aid = asset_id(img_type, fankit_slug.lower())
                stem = fname.rsplit(".", 1)[0]
                entry = {
                    "id": aid,
                    "filename": fname,
                    "category": category,
                    "subcategory": subcat,
                    "extension": f".{ext}",
                    "display_name": stem,
                    "url": url,
                    "source": "brawlify_cdn",
                    "width": 0,
                    "height": 0,
                    "tags": [name.lower(), img_type, "brawlify"],
                    "brawler": name,
                }
                new_cdn_assets.append(entry)
                print(f"    + {fname:40s} ({category})")

    print(f"\n    Downloaded: {downloaded} images")
    print(f"    New CDN entries: {len(new_cdn_assets)}")

    if not new_cdn_assets:
        print("    Nothing to add.")
    else:
        # 5. Append to assets.json
        print("\n[5] Updating assets.json...")
        assets.extend(new_cdn_assets)
        with open(ASSETS_JSON, "w") as f:
            json.dump(assets, f, indent=2)
        print(f"    assets.json: {len(assets)} entries")

        # Copy CDN files to BrawlAssets dir
        print("\n[6] Copying CDN files to BrawlAssets/...")
        cdn_symlinked = 0
        for entry in new_cdn_assets:
            src = CDN_DIR / entry["filename"]
            dst = FANKIT_DIR / entry["category"] / entry["subcategory"] / entry["filename"]
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_bytes(src.read_bytes())
                cdn_symlinked += 1
        print(f"    Copied: {cdn_symlinked} files to BrawlAssets/")

    # 7. Rebuild brawlers.json
    print("\n[7] Rebuilding brawlers.json...")

    # Map brawler -> list of asset IDs from Fankit + CDN
    brawler_assets = {b["name"].lower(): [] for b in api_brawlers}
    for a in assets:
        dn_norm = normalize(a.get("display_name", ""))
        for b in api_brawlers:
            fankit_norm = normalize(b.get("fankit", b["name"]))
            name_norm = normalize(b["name"])
            if fankit_norm in dn_norm or name_norm in dn_norm:
                brawler_assets[b["name"].lower()].append(a["id"])
                break

    new_brawlers = {}
    for b in api_brawlers:
        name = b["name"]
        key = name.lower().replace(" ", "_").replace("-", "_").replace("&", "and").replace(".", "").replace("'", "")
        
        asset_ids = brawler_assets.get(name.lower(), [])
        
        # Count unique skins (from Fankit display names with skin patterns)
        skin_names = set()
        for a in assets:
            if a["id"] in asset_ids:
                dn = a.get("display_name", "")
                if " " in dn and "Portrait" not in dn and "Pin" not in dn and "Emoji" not in dn:
                    parts = dn.split()
                    if len(parts) >= 3 and parts[1].lower() != "pin":
                        skin_names.add(parts[1])
        
        # Build asset_types
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
    print(f"    brawlers.json: {len(new_brawlers)} brawlers")

    # 8. Update search_index.json
    print("\n[8] Updating search_index.json...")
    search_index = []
    for a in assets:
        brawler_name = a.get("brawler", "")
        if not brawler_name:
            for b in api_brawlers:
                fankit_name = b.get("fankit", b["name"]).lower()
                if fankit_name in a.get("display_name", "").lower():
                    brawler_name = b["name"]
                    break
        
        entry = {
            "id": a["id"],
            "display_name": a.get("display_name", ""),
            "category": a.get("category", ""),
            "subcategory": a.get("subcategory", ""),
            "brawler": brawler_name,
            "tags": a.get("tags", []),
            "url": a.get("url", ""),
            "filename": a.get("filename", ""),
            "extension": a.get("extension", ""),
            "width": a.get("width", 0),
            "height": a.get("height", 0),
            "source": a.get("source", "fankit"),
        }
        search_index.append(entry)

    SEARCH_INDEX = BASE_DIR / "search_index.json"
    with open(SEARCH_INDEX, "w") as f:
        json.dump(search_index, f, indent=2)
    print(f"    search_index.json: {len(search_index)} entries")

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"    brawlers: {len(new_brawlers)}")
    print(f"    assets:   {len(assets)}")
    print(f"    new CDN:  {len(new_cdn_assets)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
