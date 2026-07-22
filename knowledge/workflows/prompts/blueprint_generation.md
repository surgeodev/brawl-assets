# Prompt: Create Visual Blueprint

## Objective
Convert a concept into a structured visual blueprint that can be used to search for assets and design the composition.

## Input
- Concept (from concept_generation.md)
- Brawl Stars asset database knowledge

## Process

### Step 1: Choose Composition Type
```
Composition Matrix:
| Type | Best For | Subject Position | Text Position |
|------|----------|-----------------|---------------|
| Diagonal | Action, energy | Left or right third | Opposite diagonal |
| Rule of Thirds | Balanced, readable | Left or right third | Bottom third |
| Centered | Character focus | Center | Top or bottom |
| Framed | Depth, context | Center with frame elements | Bottom |
| Split | Comparison, vs | Left and right halves | Center |
```

### Step 2: Define Depth Layers
Minimum 3 layers:
- Foreground (0-20% depth): crossing elements, particles
- Midground (40-70% depth): main subject
- Background (80-100% depth): environment

### Step 3: Design Lighting
- Choose primary direction
- Ensure shadow direction matches
- Document both highlight and shadow placement

### Step 4: Build Color Palette
- Pull dominant color from the brawler's data (brawlers.json)
- Select accent color with 120-180° hue contrast
- Choose background color (darker, lower saturation)
- Choose text color (high contrast against background)

### Step 5: Plan Text
- Write 2-5 word main title
- Position according to composition grid
- Select font pairing
- Choose treatment recipe

### Step 6: List Required Assets
- Type (render, portrait, background, pin, spray, UI element)
- Brawler name
- Condition (pose, facing direction, expression)
- Theme or skin requirement

## Output Format
Complete the full blueprint template from thumbnail_blueprint.md.

## Evaluation Criteria
- All 18 blueprint sections are filled
- Depth structure has ≥3 layers
- Lighting direction is documented and consistent
- Color palette has exactly 3 colors + 1 accent
- Text is 2-5 words
- Required assets list is specific enough to search with
