#!/usr/bin/env python3
"""Scrape Fankit assets using Playwright to bypass AWS WAF challenge."""
import json, sys, time, os
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_fankit_data"
RAW_DIR.mkdir(parents=True, exist_ok=True)
META_FILE = RAW_DIR / "fankit_metadata.json"

URL = "https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets"
FANKIT = "https://fankit.supercell.com"
BRAND = "https://brand.supercell.com"
DOC_ID = "324"

def main():
    print("=" * 60, flush=True)
    print("Fankit Scraper (Playwright)", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-web-security",
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = context.new_page()

        # Track API responses
        tokens = []
        api_responses = []

        def on_response(response):
            # Capture search API responses
            if "/api/assets/search" in response.url:
                try:
                    data = response.json()
                    if "data" in data:
                        for item in data["data"]:
                            if "token" in item:
                                tokens.append(item["token"])
                        api_responses.append(data)
                except:
                    pass

        page.on("response", on_response)

        print(f"[1] Opening {URL} ...", flush=True)
        page.goto(URL, wait_until="networkidle", timeout=120000)
        print(f"    Page loaded: {page.title()}", flush=True)

        # Wait a bit for React to render and API calls to complete
        time.sleep(5)

        # Try to get more assets by scrolling
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

        # Get the total from search response
        total = 0
        if api_responses:
            total = api_responses[-1].get("total", 0)
        print(f"    Total from API: {total}", flush=True)
        print(f"    Tokens collected: {len(tokens)}", flush=True)

        # If we have a total > tokens, make a direct API call through the page
        if total > len(tokens) and total > 0:
            print(f"    Fetching all {total} assets via page JS...", flush=True)
            # Use page.evaluate to make a fetch call (browser handles WAF auth)
            result = page.evaluate(f"""
                async () => {{
                    try {{
                        const r = await fetch('{FANKIT}/api/assets/search/{DOC_ID}?limit={total}');
                        const d = await r.json();
                        return d;
                    }} catch(e) {{
                        return {{error: e.message}};
                    }}
                }}
            """)
            if result and "data" in result:
                for item in result["data"]:
                    if "token" in item:
                        tokens.append(item["token"])
                print(f"    Extended tokens: {len(tokens)}", flush=True)

        # Deduplicate
        tokens = list(dict.fromkeys(tokens))
        print(f"    Unique tokens: {len(tokens)}", flush=True)

        # Now fetch viewer metadata for each token via page JS
        print(f"\n[2] Fetching viewer metadata for {len(tokens)} tokens...", flush=True)
        all_assets = []
        batch_size = 50

        for i in range(0, len(tokens), batch_size):
            batch = tokens[i:i+batch_size]
            batch_assets = page.evaluate(f"""
                async (tokens) => {{
                    const results = [];
                    for (const token of tokens) {{
                        try {{
                            const r = await fetch('{FANKIT}/api/viewer/data/' + token + '?document_id={DOC_ID}');
                            const d = await r.json();
                            if (d.success && d.asset) {{
                                results.push(d.asset);
                            }}
                        }} catch(e) {{
                            // ignore
                        }}
                    }}
                    return results;
                }}
            """, batch)
            if batch_assets:
                all_assets.extend(batch_assets)
            if (i + batch_size) % 500 == 0 or i + batch_size >= len(tokens):
                print(f"    [{min(i+batch_size, len(tokens))}/{len(tokens)}] got={len(all_assets)}", flush=True)

        # Save metadata
        with open(META_FILE, "w") as f:
            json.dump({
                "total": total,
                "tokens_count": len(tokens),
                "assets_count": len(all_assets),
                "assets": all_assets,
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, f, indent=2)
        print(f"\n    Saved {len(all_assets)} asset metadata to {META_FILE}", flush=True)

        # Optionally download files (only new ones, current existing count)
        EXISTING = RAW_DIR / ".." / "_raw_assets"
        EXISTING.mkdir(parents=True, exist_ok=True)
        existing_count = len(list(EXISTING.glob("*.png"))) + len(list(EXISTING.glob("*.jpg")))
        print(f"\n[3] Existing downloaded files: {existing_count}", flush=True)

        downloaded = 0
        for a in all_assets:
            code = a.get("code") or a.get("download_code") or ""
            if not code:
                continue
            fn = a.get("filename", f"asset_{a['id']}.png")
            ext = Path(fn).suffix.lstrip(".") or "png"
            local = EXISTING / f"{code}.{ext}"
            if local.exists() and local.stat().st_size > 1000:
                continue
            # Download via page JS (browser handles WAF)
            result = page.evaluate(f"""
                async () => {{
                    try {{
                        const r = await fetch('{BRAND}/api/screen/download/{code}');
                        if (!r.ok) return 'err';
                        const blob = await r.blob();
                        const buf = await blob.arrayBuffer();
                        return Array.from(new Uint8Array(buf));
                    }} catch(e) {{
                        return 'err';
                    }}
                }}
            """)
            if result and result != "err":
                local.write_bytes(bytes(result))
                downloaded += 1
            if downloaded % 50 == 0 and downloaded > 0:
                print(f"    Downloaded: {downloaded}", flush=True)

        print(f"\n    Downloaded new files: {downloaded}", flush=True)
        print(f"\n    Total in _raw_assets: {len(list(EXISTING.glob('*.png'))) + len(list(EXISTING.glob('*.jpg')))}", flush=True)

        browser.close()

    print(f"\n{'='*60}", flush=True)
    print(f"DONE: {len(all_assets)} assets metadata saved", flush=True)
    print(f"       {downloaded} new files downloaded", flush=True)
    print(f"{'='*60}", flush=True)

if __name__ == "__main__":
    main()
