#!/usr/bin/env python3
"""Download all Fankit assets using the direct Frontify API (no Playwright)."""
import json, os, sys, time
from pathlib import Path
from urllib.parse import urlparse, unquote
import subprocess

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
MANIFEST = BASE / "data" / "fankit_manifest.json"

FANKIT_DOMAIN = "https://fankit.supercell.com"
BRAND_DOMAIN = "https://brand.supercell.com"
DOCUMENTS = {
    "game-assets": "324",
    "logo": "325",
    "audio": "373",
}

HEADERS = [
    "Origin: https://fankit.supercell.com",
    "Referer: https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets",
    "Accept: application/json",
]

def curl(url, headers=None, method="GET", output=None, timeout=30):
    cmd = ["curl", "-s", "-m", str(timeout)]
    if output:
        cmd += ["-o", str(output)]
    if method == "HEAD":
        cmd += ["-I"]
    cmd.append(url)
    if headers:
        for h in headers:
            cmd += ["-H", h]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    return r

def main():
    print("=" * 60)
    print("Fankit API Scraper")
    print("=" * 60)

    for folder_name, doc_id in DOCUMENTS.items():
        print(f"\n[{folder_name}] Searching document {doc_id}...")

        # Step 1: Get asset count first
        r = curl(f"{FANKIT_DOMAIN}/api/assets/search/{doc_id}?limit=1", HEADERS)
        try:
            data = json.loads(r.stdout)
            total = data.get("total", 0)
        except:
            print(f"  ERROR: Could not parse search response: {r.stdout[:200]}")
            continue

        print(f"  Total assets: {total}")

        if total == 0:
            continue

        # Step 2: Get all assets
        r = curl(f"{FANKIT_DOMAIN}/api/assets/search/{doc_id}?limit={total}", HEADERS, timeout=120)
        try:
            data = json.loads(r.stdout)
            tokens = [item["token"] for item in data.get("data", []) if "token" in item]
        except:
            print(f"  ERROR: Could not parse search response: {r.stdout[:200]}")
            continue

        print(f"  Retrieved {len(tokens)} asset tokens")

        # Step 3: Get viewer data for each and download
        folder = RAW_DIR / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        downloaded = 0
        cached = 0
        failed = 0
        t0 = time.time()

        for i, token in enumerate(tokens):
            # Get viewer data
            r = curl(f"{FANKIT_DOMAIN}/api/viewer/data/{token}?document_id={doc_id}", HEADERS)
            try:
                vd = json.loads(r.stdout)
                if not vd.get("success"):
                    failed += 1
                    continue
                asset = vd["asset"]
                filename = asset.get("filename", f"asset_{asset['id']}.png")
                width = asset.get("width", 0)
                height = asset.get("height", 0)
                filesize = asset.get("filesize", 0)
            except:
                failed += 1
                continue

            local = folder / filename
            if local.exists() and local.stat().st_size > 1000:
                cached += 1
            else:
                # Download
                r = curl(f"{BRAND_DOMAIN}/api/screen/download/{token}", output=local, timeout=60)
                if r.returncode == 0 and local.exists() and local.stat().st_size > 1000:
                    downloaded += 1
                else:
                    failed += 1
                    continue

            if (i + 1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"  [{i+1}/{len(tokens)}] dl={downloaded} cached={cached} fail={failed} ({elapsed:.0f}s)")

        elapsed = time.time() - t0
        print(f"  DONE [{folder_name}]: {downloaded} new, {cached} cached, {failed} failed ({elapsed:.0f}s)")

    print("\n" + "=" * 60)
    print("Scrape complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
