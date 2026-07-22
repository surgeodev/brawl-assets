#!/usr/bin/env python3
"""Playwright-based scraper for Supercell Fankit brawl stars game assets."""
import asyncio, json, hashlib, os, re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

try:
    from playwright.async_api import async_playwright
except ImportError:
    print("ERROR: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
ASSETS_JSON = BASE / "data" / "assets.json"
MANIFEST = BASE / "data" / "fankit_manifest.json"

FANKIT_URL = "https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets"
DOWNLOAD_WORKERS = 8
TIMEOUT = 120_000

def safe_name(path):
    return re.sub(r'[<>:"/\\|?*]', '_', path)

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(FANKIT_URL, wait_until="networkidle", timeout=TIMEOUT)

        # Wait for asset grid to load
        await page.wait_for_selector('[data-testid="asset-grid-item"]', timeout=TIMEOUT)

        # Extract all asset links + names
        assets = await page.evaluate("""
            () => {
                const items = document.querySelectorAll('[data-testid="asset-grid-item"]');
                return Array.from(items).map(el => {
                    const link = el.querySelector('a');
                    const nameEl = el.querySelector('[data-testid="asset-name"]');
                    return {
                        url: link ? link.href : '',
                        name: nameEl ? nameEl.textContent.trim() : '',
                    };
                });
            }
        """)

        print(f"Found {len(assets)} assets on Fankit page", flush=True)

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        downloaded = []

        # Semaphore for concurrency
        sem = asyncio.Semaphore(DOWNLOAD_WORKERS)

        async def download_one(asset):
            async with sem:
                name = asset["name"]
                url = asset["url"]
                if not url:
                    return None

                # Determine file extension from URL
                parsed = urlparse(url)
                path = unquote(parsed.path)
                ext = os.path.splitext(path)[1] or ".png"
                fname = f"{safe_name(name)}{ext}"
                local = RAW_DIR / fname

                if local.exists():
                    return {"name": name, "filename": fname, "url": url, "status": "cached"}

                try:
                    resp = await page.context.request.get(url)
                    if resp.status == 200:
                        data = await resp.body()
                        if len(data) > 1000:
                            local.write_bytes(data)
                            return {"name": name, "filename": fname, "url": url, "status": "ok"}
                except Exception as e:
                    return {"name": name, "filename": fname, "url": url, "status": f"error: {e}"}
                return None

        # Batch download
        tasks = [download_one(a) for a in assets]
        results = await asyncio.gather(*tasks)

        ok = sum(1 for r in results if r and r["status"] == "ok")
        cached = sum(1 for r in results if r and r["status"] == "cached")
        failed = sum(1 for r in results if r and r["status"] != "ok" and r["status"] != "cached")

        print(f"Downloaded: {ok} new, {cached} cached, {failed} failed", flush=True)

        # Save manifest
        manifest = [r for r in results if r]
        with open(MANIFEST, "w") as f:
            json.dump(manifest, f, indent=2)

        await browser.close()
        return manifest

if __name__ == "__main__":
    asyncio.run(scrape())
