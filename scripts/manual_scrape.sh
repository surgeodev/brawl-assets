#!/bin/bash
# Manual scraper — run anytime to update assets
# Usage: bash scripts/manual_scrape.sh

set -e
cd "$(dirname "$0")/.."
BASE=$(pwd)

echo "╔════════════════════════════════════════╗"
echo "║   Brawl Assets — Manual Scraper       ║"
echo "╚════════════════════════════════════════╝"

# 1. Fetch BrawlAPI + CDN portraits
echo ""
echo "[1] Fetching BrawlAPI and CDN portraits..."
python3 scripts/rebuild_indexes.py

# 2. Convert all assets to WebP
echo ""
echo "[2] Converting assets to WebP previews..."
python3 scripts/build_previews.py

# 3. Generate brawler profiles
echo ""
echo "[3] Generating brawler profiles..."
python3 -c "
import json
from pathlib import Path
BASE = Path('.')
with open('data/brawlers.json') as f: brawlers = json.load(f)
with open('data/assets.json') as f: assets = json.load(f)
with open('data/search_index.json') as f: search = json.load(f)
am = {a['id']: a for a in search}
for key, b in brawlers.items():
    ids = set()
    for c in b['asset_types'].values(): ids.update(c)
    ba = [am.get(i,{}) for i in ids if i in am]
    lines = [f'# {b[\"name\"]}', f'Rarity: {b[\"rarity\"]} | Class: {b[\"class\"]}', f'Total assets: {b[\"total_assets\"]}']
    if b['skins']: lines.append(f'Skins: {\", \".join(b[\"skins\"])}')
    lines.append('')
    for cat in ['Brawlers','Portraits','Pins','Emojis','Sprays','Animations','Backgrounds','UI','Misc']:
        ca = [a for a in ba if a.get('category')==cat]
        if not ca: continue
        lines.append(f'\n## {cat} ({len(ca)})')
        for a in sorted(ca, key=lambda x: x.get('display_name',''))[:12]:
            dn = a.get('display_name','')
            pv = f\"previews/{a['category']}/{a['subcategory']}/{dn.replace(' ','_')}.webp\"
            lines.append(f'- {dn} -> {pv}')
        if len(ca) > 12: lines.append(f'  ... +{len(ca)-12} more')
    Path('data/brawler_profiles')/f'{key}.md'
    with open(Path('data/brawler_profiles',f'{key}.md'), 'w') as f:
        f.write('\n'.join(lines))
print(f'Generated {len(brawlers)} profiles')
"

# 4. Build master prompt
echo ""
echo "[4] Building master prompt..."
cat knowledge/*.txt knowledge/*.md 2>/dev/null > data/master_prompt.md 2>/dev/null || true
echo "Master prompt: $(wc -c < data/master_prompt.md) bytes"

# 5. Stats
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   DONE                                ║"
echo "╚════════════════════════════════════════╝"
echo "Brawlers:  $(python3 -c "import json; print(len(json.load(open('data/brawlers.json'))))")"
echo "Assets:    $(python3 -c "import json; print(len(json.load(open('data/assets.json'))))")"
echo "Previews:  $(find previews -name '*.webp' | wc -l)"
echo ""
echo "Site: http://localhost:8080"
