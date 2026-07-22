# Prompt: Search for Assets

## Objective
Search the Brawl Stars asset database to find the best assets matching the blueprint requirements.

## Context
The asset database contains 5,186 entries across categories: Brawlers, Pins, Sprays, Backgrounds, LoadingScreens, Portraits, UI, Animations, Emojis, Misc.
Each asset has: id, display_name, category, subcategory, brawler, tags, url, preview_path.

## Search Strategy

### Strategy 1: By Brawler + Type
```
Search the database for assets matching these criteria:
- brawler: [name]
- category: [Brawlers / Portraits / Pins / Emojis]
- type: [render / portrait / pin / emoji]
- condition: [facing direction, expression, skin]

Use search_index.json or preview_manifest.json to find the best match.
Filter results by:
1. Correct brawler name
2. Correct category
3. Visual condition match (check preview_manifest.json preview path)
4. Preferred orientation
```

### Strategy 2: By Theme + Category
```
Search for assets matching:
- theme: [theme name from themes.json]
- category: [Backgrounds / LoadingScreens / Sprays / Misc]
- subcategory: [specific if known]

Use themes.json or categories.json to find asset IDs, then look up details in assets.json.
```

### Strategy 3: By Color / Visual Compatibility
```
When searching for complementary assets:
1. Extract the dominant color of the main brawler from brawlers.json (color field)
2. Search for assets with compatible colors in the same theme
3. Use color_index.json if available for color-based searches
```

### Strategy 4: By UI Function
```
Search for UI elements by:
- category: UI
- subcategory: [Button / Icon / Banner / AppIcon / etc.]
- keywords in display_name matching the video theme
```

## Comparison Process

When comparing multiple candidate assets, prefer:
1. The asset whose pose/facing direction matches the blueprint
2. The asset with the most compatible scale
3. The asset with the clearest silhouette
4. The asset that leaves space for text placement

## Output Format
```yaml
selected_assets:
  main_subject:
    id: "asset_id"
    name: "display_name"
    preview: "path/to/preview.webp"
    reason: "Why this asset was chosen"
  
  background:
    id: "asset_id"
    name: "display_name"
    preview: "path/to/preview.webp"
    reason: "Why this background"
  
  secondary:
    - id: "asset_id"
      name: "display_name"
      reason: "Purpose in composition"
```

## Evaluation Criteria
- Every required_asset from the blueprint has a candidate
- Each asset is chosen for a specific compositional reason
- Assets are NOT chosen by keyword matching alone — visual compatibility is considered
- Preview paths are verified to exist
