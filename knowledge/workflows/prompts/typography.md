# Prompt: Design Typography

## Objective
Design the text treatment for the thumbnail following the typography rules.

## Input
- Blueprint (text content, font choice, placement)
- Composition (where text sits in the layout)

## Process

### Step 1: Choose Font
If Lilita One is available: use it as default.
If not available: check font_catalog.json for alternatives based on the video's emotional tone.

### Step 2: Set Typography Parameters
```
Main title (at 1920x1080 canvas):
  Font: [name]
  Size: 120-200px (based on word count: fewer words = larger size)
  Tracking: -5 to -10
  Horizontal scale: 105-115%
  Line spacing: 80-90% of font size
  Color: Pulled from brawler palette or video theme
```

### Step 3: Apply Treatment Recipe
Select a treatment recipe from text_treatment_rules.md.
The recipe choice must match the video emotion:
- Classic Brawl Title → General, guides, spotlights
- Competitive Callout → Esports, rank push, serious
- Comedy Explosion → Funny moments, fails
- Magical/Mythic → Special skins, events, lore
- Minimalist Dark → Dramatic, cinematic, story

### Step 4: Position Text
```
Vertical placement:
- Top third: Best for competitive/action (doesn't block subject)
- Bottom third: Best for character focus
- Middle: Only if subject is on opposite side

Horizontal placement:
- Left: Subject is on right
- Right: Subject is on left
- Center: Only in split/framed compositions
```

### Step 5: Adjust for Readability
- Run the 25% test (resize to 480x270)
- If text is not readable at that size, increase:
  - Font size
  - Outline thickness
  - Contrast with background

### Step 6: Verify Integration
- Does the text overlap with the subject naturally?
- Does the shadow direction match the composition's lighting?
- Does the text use colors from the same palette as the rest of the thumbnail?
- Does the text feel like it belongs in the same image?

## Output
A complete typography specification including font, size, tracking, scale, fill, outline, shadow, and placement.
