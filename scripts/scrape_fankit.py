#!/usr/bin/env python3
"""Download all Fankit assets using the direct Frontify API."""
import json, os, subprocess, sys, time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"

FANKIT = "https://fankit.supercell.com"
BRAND = "https://brand.supercell.com"
DOC_ID = "324"
WORKERS = 4
TIMEOUT = 30

HEADERS = [
    "Origin: https://fankit.supercell.com",
    "Referer: https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets",
]

def curl_get(url, output=None, timeout=TIMEOUT):
    cmd = ["curl", "-sL", "-m", str(timeout)]
    if output:
        cmd += ["-o", str(output)]
    for h in HEADERS:
        cmd += ["-H", h]
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout+5)
        return r
    except subprocess.TimeoutExpired:
        return None

def download_one(token):
    try:
        local = RAW_DIR / "game-assets"
        local.mkdir(parents=True, exist_ok=True)

        vd_url = f"{FANKIT}/api/viewer/data/{token}?document_id={DOC_ID}"
        r = curl_get(vd_url, timeout=15)
        if not r or r.returncode != 0:
            return ("err", "viewer_fail")
        try:
            vd = json.loads(r.stdout)
        except:
            return ("err", "viewer_parse")
        if not vd.get("success") or "asset" not in vd:
            return ("err", "viewer_not_ok")

        asset = vd["asset"]
        filename = asset.get("filename", f"asset_{asset['id']}.png")
        fpath = local / filename

        if fpath.exists() and fpath.stat().st_size > 1000:
            return ("cached", filename)

        dl_url = f"{BRAND}/api/screen/download/{token}"
        r = curl_get(dl_url, output=fpath, timeout=60)
        if r and r.returncode == 0 and fpath.exists() and fpath.stat().st_size > 1000:
            return ("ok", filename)
        if fpath.exists():
            fpath.unlink()
        return ("err", "dl_fail")
    except Exception as e:
        return ("err", str(e)[:50])

def main():
    print("=" * 60, flush=True)
    print("Fankit API Scraper", flush=True)
    print("=" * 60, flush=True)

    # Get all token IDs
    print(f"\nSearching document {DOC_ID}...", flush=True)
    r = curl_get(f"{FANKIT}/api/assets/search/{DOC_ID}?limit=1", timeout=30)
    if not r or r.returncode != 0:
        print("FAIL: cannot search", flush=True)
        return
    result = json.loads(r.stdout)
    total = result.get("total", 0)
    print(f"  Total: {total}", flush=True)
    if total == 0:
        return

    r = curl_get(f"{FANKIT}/api/assets/search/{DOC_ID}?limit={total}", timeout=120)
    if not r or r.returncode != 0:
        print("FAIL: cannot get all", flush=True)
        return
    result = json.loads(r.stdout)
    tokens = [item["token"] for item in result.get("data", []) if "token" in item]
    print(f"  Tokens: {len(tokens)}", flush=True)

    t0 = time.time()
    ok = cached = failed = 0
    done = 0
    n = len(tokens)

    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {ex.submit(download_one, t): t for t in tokens}
        for f in as_completed(futures):
            status, name = f.result()
            if status == "ok":
                ok += 1
            elif status == "cached":
                cached += 1
            else:
                failed += 1
            done += 1
            if done % 500 == 0 or done == n:
                print(f"  [{done}/{n}] ok={ok} cached={cached} fail={failed} ({time.time()-t0:.0f}s)", flush=True)

    elapsed = time.time() - t0
    print(f"\nDONE: {ok} new, {cached} cached, {failed} failed ({elapsed:.0f}s)", flush=True)

if __name__ == "__main__":
    main()
