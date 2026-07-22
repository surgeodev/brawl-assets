#!/usr/bin/env python3
"""Download a YouTube video thumbnail as an example reference for the AI."""
import re, sys, json, subprocess, os
from pathlib import Path
from urllib.parse import urlparse, parse_qs

BASE = Path(__file__).parent.parent.resolve()
EXAMPLES_DIR = BASE / "examples"
EXAMPLES_INDEX = BASE / "data" / "examples_index.json"

YT_PATTERNS = [
    r'(?:youtube\.com/watch\?v=)([\w-]+)',
    r'(?:youtu\.be/)([\w-]+)',
    r'(?:youtube\.com/embed/)([\w-]+)',
    r'(?:youtube\.com/shorts/)([\w-]+)',
]

def extract_id(url):
    for p in YT_PATTERNS:
        m = re.search(p, url)
        if m:
            return m.group(1)
    # Try full parse
    parsed = urlparse(url)
    if parsed.netloc in ('youtube.com', 'www.youtube.com'):
        q = parse_qs(parsed.query)
        return q.get('v', [None])[0]
    if parsed.netloc in ('youtu.be', 'www.youtu.be'):
        return parsed.path.lstrip('/')
    return None

def download_thumbnail(video_id, quality='maxresdefault'):
    """Try multiple quality levels."""
    qualities = ['maxresdefault', 'hqdefault', 'sddefault', 'mqdefault', 'default']
    if quality:
        qualities.insert(0, quality)

    for q in qualities:
        url = f"https://img.youtube.com/vi/{video_id}/{q}.jpg"
        r = subprocess.run(["curl", "-sL", "-o", "/dev/null", "--write-out", "%{http_code}", url],
                         capture_output=True, text=True, timeout=10)
        if r.stdout.strip() == "200":
            fname = f"yt_{video_id}_{q}.jpg"
            path = EXAMPLES_DIR / fname
            subprocess.run(["curl", "-sL", "-o", str(path), url], timeout=30)
            if path.exists() and path.stat().st_size > 2000:
                return fname, q
    return None, None

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/youtube_example.py <youtube-url> [quality]")
        print("       python scripts/youtube_example.py <video-id>")
        print("")
        print("Qualities: maxresdefault (best), hqdefault, sddefault, mqdefault, default")
        sys.exit(1)

    url = sys.argv[1]
    quality = sys.argv[2] if len(sys.argv) > 2 else 'maxresdefault'

    video_id = extract_id(url)
    if not video_id:
        # Maybe it's already a video ID
        if re.match(r'^[\w-]{11}$', url):
            video_id = url
        else:
            print(f"❌ Could not extract video ID from: {url}")
            sys.exit(1)

    print(f"📹 Video ID: {video_id}")

    EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    fname, used_quality = download_thumbnail(video_id, quality)
    if not fname:
        print(f"❌ Failed to download thumbnail for {video_id}")
        sys.exit(1)

    path = EXAMPLES_DIR / fname
    size = path.stat().st_size
    print(f"✅ Downloaded: {fname}")
    print(f"   Quality: {used_quality}")
    print(f"   Size: {size/1024:.0f} KB")

    # Get video title from oembed
    title = video_id
    try:
        r = subprocess.run(["curl", "-s", f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"],
                         capture_output=True, text=True, timeout=10)
        if r.returncode == 0:
            data = json.loads(r.stdout)
            title = data.get("title", video_id)
    except:
        pass

    # Build description file
    desc = f"""# {title}
source: youtube
video_id: {video_id}
quality: {used_quality}
url: https://youtube.com/watch?v={video_id}
file: {fname}
size: {size}
"""
    desc_path = EXAMPLES_DIR / f"yt_{video_id}.md"
    with open(desc_path, "w") as f:
        f.write(desc)

    # Update index
    if EXAMPLES_INDEX.exists():
        with open(EXAMPLES_INDEX) as f:
            index = json.load(f)
    else:
        index = []

    index.append({
        "id": video_id,
        "title": title,
        "file": fname,
        "quality": used_quality,
        "url": f"https://youtube.com/watch?v={video_id}",
        "size": size,
    })

    with open(EXAMPLES_INDEX, "w") as f:
        json.dump(index, f, indent=2)

    print(f"📝 Description: {desc_path}")
    print(f"📚 Index: {len(index)} examples")

if __name__ == "__main__":
    main()
