#!/usr/bin/env python3
"""Rebuild all indexes from Fankit metadata + local files + CDN."""
import json, subprocess, sys, re
from pathlib import Path
from collections import defaultdict

BASE = Path(__file__).parent.parent.resolve()
DATA_DIR = BASE / "data"
RAW_DIR = BASE / "_raw_assets"
FANKIT_DATA = BASE / "_fankit_data"
ASSETS_JSON = DATA_DIR / "assets.json"
BRAWLERS_JSON = DATA_DIR / "brawlers.json"
SEARCH_INDEX = DATA_DIR / "search_index.json"
PREVIEW_MANIFEST = DATA_DIR / "preview_manifest.json"
CDN_DIR = BASE / "_cdn_brawlers"
PROFILES_DIR = DATA_DIR / "brawler_profiles"

BRAWLIKE_URL = "https://api.brawlapi.com/v1/brawlers"
CDN_URL = "https://cdn.brawlify.com/brawlers"

def curl(url, timeout=15):
    r = subprocess.run(["curl", "-s", "-m", str(timeout), url], capture_output=True, text=True, timeout=timeout+5)
    return r

def normalize(s):
    return s.lower().replace(".", "").replace("-", "").replace(" ", "").replace("&", "and").replace("'", "").replace("_", "")

NAME_MAP = {
    "barley8bit": "barley", "barleyshelly": "barley", "bea_mortis": "bea",
    "lilybuzz": "lily", "frank_pam": "frank", "amber_byron": "amber",
    "dynabrock": "dynamike", "sprout_edgar": "sprout",
    "cherrycharlie": "charlie", "maisie_gale": "maisie",
    "mico_squeak": "mico", "pearl_griff": "pearl",
    "angelo_maisie": "angelo", "ash_bonnie": "ash",
    "berry_byron": "berry", "buster_jacky": "buster",
    "chuck_max": "chuck", "colt_rico": "colt",
    "colette": "colette", "cordelius_gray": "cordelius",
    "draco_brock": "draco", "dynamike_barley": "dynamike",
    "emz_dyna": "emz", "eve_maisie": "eve",
    "fang_primo": "fang", "grom_byron": "grom",
    "hank_frank": "hank", "janet_chester": "janet",
    "jdpenny": "penny", "kendra_lola": "kendra",
    "kit_stu": "kit", "l_and_l": "lily",
    "larryandlawrie": "larryandlawrie",
    "lou_edgar": "lou", "mandy_tick": "mandy",
    "meg_mandy": "meg", "melodie": "melodie",
    "moetrixie": "moe", "nani_bibi": "nani",
    "otis_squeak": "otis", "pam_bonnie": "pam",
    "pearl_griff2": "pearl", "riko": "rico",
    "rosa_edgar": "rosa", "ruffs_belle": "ruffs",
    "sam_colt": "sam", "squeak_edgar": "squeak",
    "stu_crow": "stu", "surge_max": "surge",
    "shelly_dyna": "shelly", "tara_nita": "tara",
    "wareagle": "eagle", "willow_edgar": "willow",
    "bonnie_dyna": "bonnie", "buzz_edgar": "buzz",
}

def classify_asset(filename, width=0, height=0):
    stem = filename.lower()
    dn = Path(filename).stem
    if any(kw in stem for kw in ["logo"]):
        return ("Logos", "General", dn)
    if any(kw in stem for kw in ["loading", "splash"]):
        return ("LoadingScreens", "General", dn)
    if any(kw in stem for kw in ["background", "bg_"]):
        return ("Backgrounds", "General", dn)
    if any(kw in stem for kw in ["spray"]):
        return ("Sprays", "All", dn)
    if any(kw in stem for kw in ["emoji", "emote"]):
        return ("Emojis", "All", dn)
    if any(kw in stem for kw in ["pin", "angry", "happy", "sad", "gg", "clap", "facepalm"]):
        for pt in ["angry", "happy", "sad", "gg", "clap", "facepalm", "phew", "thanks", "stop", "special", "default"]:
            if pt in stem:
                return ("Pins", pt.capitalize(), dn)
        return ("Pins", "Default", dn)
    if any(kw in stem for kw in ["portrait", "portrate"]):
        return ("Portraits", "Unknown", dn)
    if any(kw in stem for kw in ["icon", "badge", "trophy", "token", "coin", "gem", "star", "brawl pass", "season", "rank", "ui_", "button", "panel", "profile", "player"]):
        return ("UI", "Icons", dn)
    if width > 0 and height > 0:
        ratio = max(width, height) / min(width, height) if min(width, height) > 0 else 1
        if ratio > 2.5:
            return ("Backgrounds", "General", dn)
    return ("Brawlers", "Default", dn)

def get_brawler_for_filename(fn_norm, api_brawlers):
    for key in sorted(api_brawlers, key=lambda k: -len(k)):
        nn = normalize(api_brawlers[key]["name"])
        if nn in fn_norm:
            return api_brawlers[key]["name"]
    for fn_part, bkey in sorted(NAME_MAP.items(), key=lambda x: -len(x[0])):
        if fn_part in fn_norm:
            return api_brawlers.get(bkey, {}).get("name", bkey.capitalize())
    return None

def main():
    print("="*60, flush=True)
    print("Rebuild Indexes", flush=True)
    print("="*60, flush=True)

    # 1. BrawlAPI
    print("\n[1] BrawlAPI...", flush=True)
    r = curl(BRAWLIKE_URL)
    api_data = json.loads(r.stdout)
    api_brawlers = {}
    for b in api_data["list"]:
        key = b["name"].lower().replace(" ", "_").replace("-", "_").replace(".", "").replace("&", "and").replace("'", "").replace("!", "")
        api_brawlers[key] = b
    print(f"    {len(api_brawlers)} brawlers", flush=True)

    # 2. Load Fankit metadata if available
    meta_file = FANKIT_DATA / "fankit_metadata.json"
    fankit_assets = []
    if meta_file.exists():
        print("\n[2] Loading Fankit metadata...", flush=True)
        data = json.loads(meta_file.read_text())
        fankit_assets = data.get("assets", [])
        print(f"    {len(fankit_assets)} assets from Fankit API", flush=True)

    # 3. Scan _raw_assets for downloaded files
    print("\n[3] Scanning _raw_assets...", flush=True)
    raw_files = {}
    if RAW_DIR.exists():
        suffixes = ["*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg"]
        for s in suffixes:
            for f in RAW_DIR.glob(s):
                raw_files[f.stem] = f
    print(f"    {len(raw_files)} files", flush=True)

    # 4. Build asset list
    print("\n[4] Building assets...", flush=True)
    assets = []
    seen_ids = set()
    brawler_assets = defaultdict(list)
    used_raw = set()

    # Process Fankit metadata (has more info, prefer it)
    for a in fankit_assets:
        fn = a.get("filename") or f"asset_{a['id']}.png"
        code = a.get("code") or a.get("download_code") or ""
        w = a.get("width") or 0
        h = a.get("height") or 0
        aid = f"fa{a['id']}"
        if aid in seen_ids:
            continue
        seen_ids.add(aid)
        ext = Path(fn).suffix.lstrip(".") or "png"
        dn = Path(fn).stem

        # Check if we have the raw file
        raw_path = raw_files.get(code) or raw_files.get(aid)

        cat, sub, _ = classify_asset(fn, w, h)
        bname = get_brawler_for_filename(normalize(dn), api_brawlers)

        entry = {
            "id": aid, "filename": fn, "category": cat, "subcategory": sub,
            "extension": f".{ext}", "display_name": dn,
            "url": f"https://brand.supercell.com/api/screen/download/{code}",
            "source": "fankit_api", "width": w or 0, "height": h or 0,
            "tags": [cat.lower(), sub.lower()], "brawler": bname,
        }
        assets.append(entry)
        if bname:
            bkey = normalize(bname)
            brawler_assets[bkey].append(aid)
        if raw_path:
            used_raw.add(raw_path.stem)

    # Process remaining raw files not in Fankit metadata
    for stem, fpath in raw_files.items():
        if stem in used_raw:
            continue
        aid = f"raw_{stem}"
        if aid in seen_ids:
            continue
        seen_ids.add(aid)
        fn = fpath.name
        ext = fpath.suffix.lstrip(".") or "png"
        dn = fpath.stem
        cat, sub, _ = classify_asset(fn)
        bname = get_brawler_for_filename(normalize(dn), api_brawlers)

        entry = {
            "id": aid, "filename": fn, "category": cat, "subcategory": sub,
            "extension": f".{ext}", "display_name": dn,
            "url": "", "source": "local", "width": 0, "height": 0,
            "tags": [cat.lower(), sub.lower()], "brawler": bname,
        }
        assets.append(entry)
        if bname:
            bkey = normalize(bname)
            brawler_assets[bkey].append(aid)

    print(f"    {len(assets)} total assets", flush=True)

    # 5. CDN portraits for missing brawlers
    print("\n[5] CDN portraits...", flush=True)
    CDN_DIR.mkdir(parents=True, exist_ok=True)

    brawlers_with_fankit = set()
    for a in assets:
        if a["source"] == "fankit_api" and a["category"] == "Brawlers" and a["brawler"]:
            brawlers_with_fankit.add(normalize(a["brawler"]))

    cdn_count = 0
    for key, bb in api_brawlers.items():
        n = normalize(bb["name"])
        if n in brawlers_with_fankit:
            continue
        aid = f"cdn_{key}"
        for suffix, url_key in [("bordered", "imageUrl"), ("borderless", "imageUrl2"), ("emoji", "imageUrl3")]:
            url = bb.get(url_key)
            if not url:
                continue
            ext = url.split(".")[-1]
            fn = f"{key}_{suffix}.{ext}"
            local = CDN_DIR / fn
            subprocess.run(["curl", "-sL", "-o", str(local), url], capture_output=True, timeout=30)
            if local.exists() and local.stat().st_size > 1000:
                aid2 = f"{aid}_{suffix}"
                seen_ids.add(aid2)
                assets.append({
                    "id": aid2, "filename": fn, "category": "Brawlers", "subcategory": key,
                    "extension": f".{ext}", "display_name": f"{key}_{suffix}",
                    "url": url, "source": "brawlify_cdn", "width": 0, "height": 0,
                    "tags": [key, suffix, "brawlify"], "brawler": bb["name"],
                })
                brawler_assets[n].append(aid2)
                cdn_count += 1
    print(f"    {cdn_count} CDN assets added", flush=True)

    # 6. Build brawlers.json
    print("\n[6] Building brawlers.json...", flush=True)
    preview_root = BASE / "previews" / "Brawlers"
    preview_dirs = {}
    if preview_root.exists():
        for d in preview_root.iterdir():
            if d.is_dir():
                preview_dirs[normalize(d.name)] = d.name

    new_brawlers = {}
    for key, bb in api_brawlers.items():
        name = bb["name"]
        ids = brawler_assets.get(normalize(bb["name"]), [])

        # Compute preview_dir
        name_clean = normalize(name)
        pd = None
        for norm_name, actual_dir in preview_dirs.items():
            if norm_name == name_clean:
                pd = actual_dir
                break
        if not pd:
            for dd in preview_dirs:
                if dd.replace("_", "") == name_clean or name_clean in dd:
                    pd = preview_dirs[dd]
                    break
        if not pd:
            pd = name.lower().replace(" ", "").replace("-", "").replace(".", "").replace("&", "and").replace("'", "").replace("!", "")

        asset_types = defaultdict(list)
        for aid in ids:
            for a in assets:
                if a["id"] == aid:
                    asset_types[a["category"]].append(aid)
                    break

        new_brawlers[key] = {
            "name": name, "rarity": bb["rarity"]["name"],
            "class": bb["class"]["name"], "color": bb["rarity"].get("color", "#888"),
            "preview_dir": pd, "total_assets": len(ids), "skins": [],
            "asset_types": {k: v for k, v in sorted(asset_types.items())},
        }

    with open(BRAWLERS_JSON, "w") as f:
        json.dump(new_brawlers, f, indent=2)
    print(f"    {len(new_brawlers)} brawlers", flush=True)

    # 7. Save assets.json
    with open(ASSETS_JSON, "w") as f:
        json.dump(assets, f, indent=2)
    print(f"\n[7] Saved assets.json ({len(assets)})", flush=True)

    # 8. Search index
    print("\n[8] Search index...", flush=True)
    search_index = [{
        "id": a["id"], "display_name": a["display_name"],
        "category": a["category"], "subcategory": a["subcategory"],
        "brawler": a["brawler"] or "", "tags": a["tags"],
        "url": a["url"], "filename": a["filename"],
        "extension": a["extension"], "width": a["width"],
        "height": a["height"], "source": a["source"],
    } for a in assets]
    with open(SEARCH_INDEX, "w") as f:
        json.dump(search_index, f, indent=2)
    print(f"    {len(search_index)} entries", flush=True)

    # 9. Preview manifest (scan existing previews)
    print("\n[9] Preview manifest...", flush=True)
    manifest = []
    preview_dir = BASE / "previews"
    seen_paths = set()
    for a in assets:
        stem = a["display_name"].replace(" ", "_")
        ext = a["extension"].lstrip(".")
        pv_path = f"previews/{a['category']}/{a['subcategory']}/{stem}.{ext}"
        if pv_path in seen_paths:
            continue
        seen_paths.add(pv_path)
        pv_file = preview_dir / a["category"] / a["subcategory"] / f"{stem}.{ext}"
        pw = ph = fsize = 0
        if pv_file.exists():
            fsize = pv_file.stat().st_size
            try:
                from PIL import Image
                with Image.open(str(pv_file)) as img:
                    pw, ph = img.size
            except:
                pass
        manifest.append({
            "id": a["id"], "display_name": a["display_name"],
            "preview_path": pv_path.replace(f".{ext}", ".webp"),
            "original_filename": a["filename"], "original_url": a["url"],
            "preview_width": pw, "preview_height": ph,
            "original_width": a["width"], "original_height": a["height"],
            "filesize": fsize,
        })
    with open(PREVIEW_MANIFEST, "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"    {len(manifest)} entries", flush=True)

    # 10. Profiles
    print("\n[10] Brawler profiles...", flush=True)
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    for key, data in new_brawlers.items():
        ids = set()
        for cat_ids in data["asset_types"].values():
            ids.update(cat_ids)
        b_assets = [a for a in assets if a["id"] in ids]
        lines = [f"# {data['name']}", f"Rarity: {data['rarity']} | Class: {data['class']}", f"Total assets: {data['total_assets']}", ""]
        for cat in ["Brawlers", "Portraits", "Pins", "Emojis", "Sprays", "Backgrounds", "UI", "Logos"]:
            cat_items = [a for a in b_assets if a["category"] == cat]
            if not cat_items:
                continue
            lines.append(f"\n## {cat} ({len(cat_items)})")
            for a in sorted(cat_items, key=lambda x: x.get("display_name", ""))[:10]:
                lines.append(f"  - {a['display_name']}")
            if len(cat_items) > 10:
                lines.append(f"    ... +{len(cat_items)-10} more")
        with open(PROFILES_DIR / f"{key}.md", "w") as f:
            f.write("\n".join(lines))
    print(f"    {len(new_brawlers)} profiles", flush=True)

    print(f"\n{'='*60}", flush=True)
    print(f"DONE: {len(assets)} assets, {len(new_brawlers)} brawlers", flush=True)
    print(f"{'='*60}", flush=True)

if __name__ == "__main__":
    main()
