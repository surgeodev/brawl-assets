# Prompt: Design Lighting

## Objective
Create a consistent lighting system across all elements in the thumbnail.

## Input
- Blueprint lighting direction
- Selected assets
- Composition layout

## Lighting Rules

### Rule 1: One Primary Light Source
Define ONE direction light comes from:
- Top-left (default, most natural)
- Top-right
- Side (dramatic)
- Bottom-up (dramatic, horror)
- Backlight (epic, cinematic)

### Rule 2: Shadow Consistency
ALL shadows in the thumbnail must fall in the opposite direction of the light source.
- Light from top-left → Shadows fall bottom-right
- Light from top → Shadows fall bottom
- Backlight → No drop shadows, only rim light

### Rule 3: Highlight Placement
Highlights must be on the side FACING the light source:
- Top-left light → Highlights on top and left edges
- Rim light → Highlights on all edges facing the viewer

### Rule 4: Three-Value Lighting
Every element should have:
1. **Highlight area** (facing light): 10-20% brighter
2. **Mid-tone area** (the base color): 60-80% of the element
3. **Shadow area** (facing away): 20-40% darker

### Rule 5: Atmosphere
- Distance from light = less contrast
- Foreground: highest contrast
- Background: lowest contrast
- This creates natural depth

## Lighting Effects Library

### Top-Left Studio Lighting
```
Primary:      45° angle from top-left
Highlights:   Top and left edges of subject
Shadows:      Bottom and right of subject
Background:   Darker on bottom-right, lighter on top-left
Texture:      Gradient on background matching light direction
Best for:     Clean, professional, readable thumbnails
```

### Dramatic Side Lighting
```
Primary:      Directly from left or right
Highlights:   One full side of the subject
Shadows:      Opposite side, deep shadow
Background:   Dark on shadow side, lighter on light side
Best for:     Intense, competitive, serious content
```

### Cinematic Backlight
```
Primary:      From behind the subject, slightly above
Highlights:   Rim light on subject's edges
Shadows:      Front of subject is darker
Background:   Bright behind subject, darker at edges
Best for:     Epic, legendary, hypercharge moments
```

### Ambient Glow (No Direction)
```
Primary:      Diffuse light from the center
Highlights:   Center of subject
Shadows:      Edges of frame (vignette)
Best for:     Magical, themed, special event content
```

## Lighting Anti-Patterns
- ❌ Shadows that fall in different directions on different elements
- ❌ Highlights on the wrong side of the subject
- ❌ All elements lit the same way (no depth differentiation)
- ❌ Text shadow that contradicts the composition's lighting
- ❌ No visible shadow on the main subject (feels flat)

## Output
Lighting scheme specification with:
- Primary direction
- Highlight placement per element
- Shadow placement per element  
- Background gradient to reinforce lighting
- Text shadow alignment confirmation
