#!/usr/bin/env python3
"""Download all Fankit assets using the direct Frontify API (parallel workers)."""
import json, os, sys, time, urllib.request, ssl
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"

FANKIT_DOMAIN = "https://fankit.supercell.com"
BRAND_DOMAIN = "https://brand.supercell.com"
DOCUMENTS = {
    "game-assets": "324",
}
WORKERS = 12

ssl_ctx = ssl.create_default_context()

def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={
        "Origin": "https://fankit.supercell.com",
        "Referer": "https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ssl_ctx) as r:
            return r.read()
    except Exception as e:
        return None

def download_one(args):
    token, doc_id, folder = args
    try:
        # Get viewer data
        vd_url = f"{FANKIT_DOMAIN}/api/viewer/data/{token}?document_id={doc_id}"
        vd_data = fetch(vd_url)
        if not vd_data:
            return (token, "err_viewer_no_data")
        vd = json.loads(vd_data)
        if not vd.get("success"):
            return (token, f"err_viewer_{vd.get('error','?')}")
        asset = vd["asset"]
        filename = asset.get("filename", f"asset_{asset['id']}.png")

        local = folder / filename
        if local.exists() and local.stat().st_size > 1000:
            return (token, "cached")

        # Download file
        dl_url = f"{BRAND_DOMAIN}/api/screen/download/{token}"
        data = fetch(dl_url, timeout=60)
        if data and len(data) > 1000:
            local.write_bytes(data)
            return (token, "ok")
        return (token, "err_download")
    except Exception as e:
        return (token, f"err_{e}")

def main():
    print("=" * 60, flush=True)
    print("Fankit API Scraper (12 workers)", flush=True)
    print("=" * 60, flush=True)

    for folder_name, doc_id in DOCUMENTS.items():
        print(f"\n[{folder_name}] Searching document {doc_id}...", flush=True)

        search_url = f"{FANKIT_DOMAIN}/api/assets/search/{doc_id}?limit=1"
        data = fetch(search_url)
        if not data:
            print("  ERROR: Could not fetch search endpoint", flush=True)
            continue
        result = json.loads(data)
        total = result.get("total", 0)
        print(f"  Total assets: {total}", flush=True)
        if total == 0:
            continue

        # Get all asset tokens
        search_url = f"{FANKIT_DOMAIN}/api/assets/search/{doc_id}?limit={total}"
        data = fetch(search_url, timeout=120)
        if not data:
            print("  ERROR: Could not fetch all assets", flush=True)
            continue
        result = json.loads(data)
        tokens = [item["token"] for item in result.get("data", []) if "token" in item]
        print(f"  Retrieved {len(tokens)} asset tokens", flush=True)

        folder = RAW_DIR / folder_name
        folder.mkdir(parents=True, exist_ok=True)

        t0 = time.time()
        args_list = [(t, doc_id, folder) for t in tokens]
        ok = cached = failed = 0
        done = 0
        total_tasks = len(args_list)

        with ThreadPoolExecutor(max_workers=WORKERS) as ex:
            futures = {ex.submit(download_one, args): args for args in args_list}
            for future in as_completed(futures):
                _, status = future.result()
                if status == "ok":
                    ok += 1
                elif status == "cached":
                    cached += 1
                else:
                    failed += 1
                done += 1
                if done % 500 == 0 or done == total_tasks:
                    elapsed = time.time() - t0
                    print(f"  [{done}/{total_tasks}] ok={ok} cached={cached} fail={failed} ({elapsed:.0f}s)", flush=True)

        elapsed = time.time() - t0
        print(f"  DONE [{folder_name}]: {ok} new, {cached} cached, {failed} failed ({elapsed:.0f}s)", flush=True)

    print("\n" + "=" * 60, flush=True)
    print("Scrape complete!", flush=True)
    print("=" * 60, flush=True)

if __name__ == "__main__":
    main()
