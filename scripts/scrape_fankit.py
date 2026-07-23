#!/usr/bin/env python3
"""Scrape Fankit assets using Playwright (WAF bypass) + curl (fast downloads)."""
import json, sys, time, os, subprocess
from pathlib import Path
from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent.parent.resolve()
RAW_DIR = BASE / "_raw_assets"
FANKIT_DATA = BASE / "_fankit_data"
FANKIT_DATA.mkdir(parents=True, exist_ok=True)
META_FILE = FANKIT_DATA / "fankit_metadata.json"
COOKIE_FILE = FANKIT_DATA / "aws_waf_token.txt"

URL = "https://fankit.supercell.com/d/YvtsWV4pUQVm/game-assets"
FANKIT = "https://fankit.supercell.com"
BRAND = "https://brand.supercell.com"
DOC_ID = "324"
TOKEN_NAME = "aws-waf-token"

def main():
    print("=" * 60, flush=True)
    print("Fankit Scraper (Playwright + curl)", flush=True)
    print("=" * 60, flush=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            "--no-sandbox", "--disable-setuid-sandbox",
            "--disable-dev-shm-usage", "--disable-web-security",
        ])
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US",
        )
        page = context.new_page()

        print(f"[1] Opening {URL} ...", flush=True)
        page.goto(URL, wait_until="networkidle", timeout=120000)
        print(f"    Loaded: {page.title()}", flush=True)
        time.sleep(5)

        # Scroll to trigger lazy-loaded assets
        for _ in range(3):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(3)
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(2)

        # Collect tokens from intercepted API responses
        tokens = []
        api_responses = []

        def on_response(response):
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

        # Re-navigate so we capture fresh responses
        page.goto(URL, wait_until="networkidle", timeout=120000)
        time.sleep(8)

        total = api_responses[-1].get("total", 0) if api_responses else 0
        print(f"    Total: {total}, tokens collected: {len(tokens)}", flush=True)

        # Fetch all tokens via page.evaluate (browser handles WAF)
        if total > len(tokens) and total > 0:
            result = page.evaluate(f"""
                async () => {{
                    const r = await fetch('{FANKIT}/api/assets/search/{DOC_ID}?limit={total}');
                    const d = await r.json();
                    return d;
                }}
            """)
            if result and "data" in result:
                for item in result["data"]:
                    if "token" in item:
                        tokens.append(item["token"])

        tokens = list(dict.fromkeys(tokens))
        print(f"    Unique tokens: {len(tokens)}", flush=True)

        # Fetch viewer metadata for ALL tokens
        print(f"\n[2] Fetching viewer metadata for {len(tokens)} tokens...", flush=True)
        all_assets = []
        for i in range(0, len(tokens), 50):
            batch = tokens[i:i+50]
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
                        }} catch(e) {{}}
                    }}
                    return results;
                }}
            """, batch)
            if batch_assets:
                all_assets.extend(batch_assets)
            if (i + 50) % 500 == 0 or i + 50 >= len(tokens):
                print(f"    [{min(i+50, len(tokens))}/{len(tokens)}] got={len(all_assets)}", flush=True)

        # Save metadata
        with open(META_FILE, "w") as f:
            json.dump({
                "total": total, "tokens_count": len(tokens),
                "assets_count": len(all_assets), "assets": all_assets,
                "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            }, f, indent=2)
        print(f"\n    Saved {len(all_assets)} asset metadata", flush=True)

        # Extract WAF token cookie for curl downloads
        cookies = context.cookies()
        waf_token = None
        for c in cookies:
            if c["name"] == TOKEN_NAME:
                waf_token = c["value"]
                break
        if waf_token:
            COOKIE_FILE.write_text(waf_token)
            print(f"    AWS WAF token: {waf_token[:20]}... (saved to {COOKIE_FILE.name})", flush=True)

        # Check existing files
        RAW_DIR.mkdir(parents=True, exist_ok=True)
        existing = {}
        for s in ["*.png", "*.jpg", "*.jpeg", "*.webp", "*.gif", "*.svg"]:
            for f in RAW_DIR.glob(s):
                existing[f.stem] = f
        print(f"\n[3] Existing raw files: {len(existing)}", flush=True)

        # Download files using curl with WAF token (muuuuch faster than CDP)
        if waf_token:
            print(f"    Downloading new files via curl...", flush=True)
            COOKIES = f"{TOKEN_NAME}={waf_token}"
            downloaded = 0
            skipped = 0
            t0 = time.time()
            refresh_interval = 180  # refresh WAF token every 3 min
            last_refresh = time.time()

            for idx, a in enumerate(all_assets):
                # Refresh WAF token periodically
                if time.time() - last_refresh > refresh_interval:
                    page.goto(URL, wait_until="networkidle", timeout=60000)
                    time.sleep(3)
                    cookies = context.cookies()
                    for c in cookies:
                        if c["name"] == TOKEN_NAME:
                            waf_token = c["value"]
                            COOKIES = f"{TOKEN_NAME}={waf_token}"
                            break
                    last_refresh = time.time()
                    print(f"    [refresh] WAF token renewed at {time.time()-t0:.0f}s", flush=True)

                code = a.get("code") or a.get("download_code") or ""
                if not code:
                    skipped += 1
                    continue
                fn = a.get("filename") or f"asset_{a['id']}.png"
                ext = Path(fn).suffix.lstrip(".") or "png"
                local = RAW_DIR / f"{code}.{ext}"
                if local.exists() and local.stat().st_size > 1000:
                    skipped += 1
                    continue

                # curl with WAF cookie
                dl_url = f"{BRAND}/api/screen/download/{code}"
                r = subprocess.run([
                    "curl", "-sL", "-m", "30",
                    "-H", f"Cookie: {COOKIES}",
                    "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "-H", "Referer: https://fankit.supercell.com/",
                    "-o", str(local), dl_url,
                ], capture_output=True, timeout=35)

                if r.returncode == 0 and local.exists() and local.stat().st_size > 1000:
                    downloaded += 1
                else:
                    if local.exists():
                        local.unlink()
                    skipped += 1

                if (idx + 1) % 200 == 0:
                    elapsed = time.time() - t0
                    rate = downloaded / elapsed if elapsed > 0 else 0
                    print(f"    [{idx+1}/{len(all_assets)}] dl={downloaded} skip={skipped} ({elapsed:.0f}s, {rate:.1f}/s)", flush=True)

            elapsed = time.time() - t0
            print(f"\n    Downloaded: {downloaded}, skipped: {skipped} ({elapsed:.0f}s)", flush=True)

        browser.close()

    print(f"\n{'='*60}", flush=True)
    print(f"DONE: {len(all_assets)} assets metadata", flush=True)
    total_now = len(list(RAW_DIR.glob("*.png"))) + len(list(RAW_DIR.glob("*.jpg"))) + len(list(RAW_DIR.glob("*.webp"))) + len(list(RAW_DIR.glob("*.gif"))) + len(list(RAW_DIR.glob("*.svg")))
    print(f"       {total_now} files in _raw_assets", flush=True)
    print(f"{'='*60}", flush=True)

if __name__ == "__main__":
    main()
