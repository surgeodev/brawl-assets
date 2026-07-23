#!/usr/bin/env python3
"""Playwright-based scraper for Supercell Fankit brawl stars game assets."""
import asyncio, json, os, re, sys
from pathlib import Path
from urllib.parse import urlparse, unquote

try:
    from playwright.async_api import async_playwright, TimeoutError as PwTimeout
except ImportError:
    print("ERROR: pip install playwright && playwright install chromium")
    sys.exit(1)

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
ASSETS_JSON = BASE / "data" / "assets.json"
MANIFEST = BASE / "data" / "fankit_manifest.json"
DEBUG_DIR = BASE / "_debug"

FANKIT_URL = "https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets"
DOWNLOAD_WORKERS = 8
TIMEOUT = 120_000

def safe_name(path):
    return re.sub(r'[<>:"/\\|?*]', '_', path)

async def scrape():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        page.on("console", lambda msg: print(f"[browser] {msg.text}", flush=True))
        page.on("pageerror", lambda err: print(f"[browser error] {err}", flush=True))

        try:
            await page.goto(FANKIT_URL, wait_until="domcontentloaded", timeout=TIMEOUT)
        except PwTimeout:
            print("WARNING: initial page load timeout, continuing anyway", flush=True)

        await asyncio.sleep(5)

        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(DEBUG_DIR / "page.png"))
        html = await page.content()
        (DEBUG_DIR / "page.html").write_text(html)

        selectors = [
            '[data-testid="asset-grid-item"]',
            '[data-testid="asset-grid-item"] a',
            "a[href*='/asset/']",
            "[class*='asset-grid'] a",
            "[class*='AssetGrid'] a",
            ".asset-grid-item a",
            "a[download]",
        ]

        found = None
        for sel in selectors:
            try:
                el = await page.wait_for_selector(sel, timeout=5000)
                if el:
                    print(f"Found selector: {sel}", flush=True)
                    found = sel
                    break
            except PwTimeout:
                continue

        if not found:
            links = await page.evaluate("""() => {
                const all = document.querySelectorAll('a');
                return Array.from(all).filter(a => {
                    const h = a.href || '';
                    return h.includes('/asset/') || h.match(/\\.(png|jpg|jpeg|webp|svg|gif)/i);
                }).map(a => ({ href: a.href, text: a.textContent.trim().slice(0,80) }));
            }""")
            print(f"No known selector matched. Found {len(links)} candidate links:", flush=True)
            for l in links[:10]:
                print(f"  {l['text']}: {l['href']}", flush=True)
            if links:
                found = "manual"

        if found == "manual":
            link_data = links
        else:
            link_data = await page.evaluate(f"""() => {{
                const items = document.querySelectorAll('{found}');
                return Array.from(items).map(el => {{
                    const link = el.tagName === 'A' ? el : el.querySelector('a');
                    const nameEl = el.querySelector('[data-testid="asset-name"], [class*="asset-name"], [class*="AssetName"]');
                    return {{
                        url: link ? link.href : '',
                        name: nameEl ? nameEl.textContent.trim() : (link ? link.textContent.trim() : ''),
                    }};
                }});
            }}""")

        if not link_data:
            print("No assets found at all. Dumping page structure...", flush=True)
            structure = await page.evaluate("""() => {
                const walk = (el, depth) => {
                    if (depth > 3) return '';
                    let s = el.tagName;
                    if (el.className) s += '.' + (typeof el.className === 'string' ? el.className.replace(/ /g,'.') : '');
                    if (el.id) s += '#' + el.id;
                    return s + ' > ' + Array.from(el.children).map(c => walk(c, depth+1)).join(' | ');
                };
                return walk(document.body, 0);
            }""")
            print(structure[:2000], flush=True)
            (DEBUG_DIR / "structure.txt").write_text(structure)
            await browser.close()
            return []

        assets = [a for a in link_data if a.get("url")]
        print(f"Found {len(assets)} assets on Fankit page", flush=True)

        if not assets:
            await browser.close()
            return []

        RAW_DIR.mkdir(parents=True, exist_ok=True)
        downloaded = []
        sem = asyncio.Semaphore(DOWNLOAD_WORKERS)

        async def download_one(asset):
            async with sem:
                name = asset.get("name", "")
                url = asset.get("url", "")
                if not url:
                    return None
                parsed = urlparse(url)
                path = unquote(parsed.path)
                ext = os.path.splitext(path)[1] or ".png"
                fname = f"{safe_name(name)}{ext}" if name else os.path.basename(path)
                if not fname:
                    return None
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

        tasks = [download_one(a) for a in assets]
        results = await asyncio.gather(*tasks)
        ok = sum(1 for r in results if r and r["status"] == "ok")
        cached = sum(1 for r in results if r and r["status"] == "cached")
        failed = sum(1 for r in results if r and r["status"] != "ok" and r["status"] != "cached")
        print(f"Downloaded: {ok} new, {cached} cached, {failed} failed", flush=True)

        manifest = [r for r in results if r]
        with open(MANIFEST, "w") as f:
            json.dump(manifest, f, indent=2)

        await browser.close()
        return manifest

if __name__ == "__main__":
    asyncio.run(scrape())
