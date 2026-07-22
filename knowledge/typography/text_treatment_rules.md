# Brawl Stars Text Treatment Rules

## The Three-Layer Model

Every text element in a Brawl Stars thumbnail is composed of three independent layers:

```
┌────────────────────────────────────────────┐
│  LAYER 3: ENVIRONMENTAL EFFECTS           │
│  (glow, particles, gradient, texture)      │
├────────────────────────────────────────────┤
│  LAYER 2: TEXT STYLE                      │
│  (fill, outline, shadow, extrusion)        │
├────────────────────────────────────────────┤
│  LAYER 1: BARE TEXT                       │
│  (font choice, size, tracking, scale)     │
└────────────────────────────────────────────┘
```

These layers are designed independently.
The font itself is only Layer 1. Changing the font does not fix a poorly treated text block.

---

## LAYER 1: Bare Text

### Font Selection Parameters
| Parameter | Main Title | Subtitle | Context |
|-----------|-----------|----------|---------|
| Font | Lilita One / Bangers | DejaVu Sans Bold / Anton | DejaVu Sans |
| Weight | 400 (display font) | 700 (bold) | 400 (regular) |
| Size (1080p) | 120-200px | 60-100px | 30-50px |
| Tracking | -5 to -10 | 0 to -5 | 0 |
| Line spacing | 80-90% of font size | 100-110% | 120% |
| Horizontal scale | 105-115% | 100% | 100% |
| Max words | 3-5 | 5-10 | 10+ |

### Letterspacing Decision Matrix
| Emotion | Tracking | Character Spacing | Effect |
|---------|----------|-------------------|--------|
| Aggressive | -10 to -15 | Tight | Feels intense, compact |
| Energetic | -5 to -10 | Close | Feels fast, urgent |
| Normal | 0 | Default | Neutral, calm |
| Playful | +5 to +10 | Loose | Feels light, casual |
| Formal | +10 to +20 | Wide | Feels important, slow |

---

## LAYER 2: Text Style

### Outline System

**Main Title (1080p):**
- Thickness: 6-10px
- Color: #1a1a2e or match the darkest element
- Opacity: 100%
- Blend mode: Normal
- Position: Outside (stroke)

**Subtitle:**
- Thickness: 3-5px
- Color: Same as main or lighter
- Opacity: 90%
- Blend mode: Normal

**Context Text:**
- Thickness: 2-3px
- Color: #000000
- Opacity: 80%

### Fill System

**Solid fill (aggressive, clean):**
- Single color matching brawler's dominant tone
- No gradient — pure bold color
- Best for: Competitive, esports, action

**Gradient fill (dynamic, premium):**
- Two color stops:
  - Top: Lighter shade (highlight direction = top-left light source)
  - Bottom: Darker shade
- Three color stops:
  - Top: Highlight
  - Middle: Main color
  - Bottom: Shadow
- Angle: 90° (top to bottom) or 45° (diagonal)
- Best for: Main titles, legendary brawlers

**Texture fill (thematic):**
- Fill with an image texture matching the theme
- Example: Lava texture for fire brawler
- Overlay mode: Multiply or Overlay at 40-60%
- Best for: Thematic thumbnails, skins

**Empty fill (minimalist):**
- No fill — outline only
- Best for: Layered text, overlapping with subject

### Shadow System

| Shadow Type | Offset X | Offset Y | Blur | Opacity | Best For |
|------------|----------|----------|------|---------|----------|
| Hard drop | 4-8px | 4-8px | 0-2px | 80-100% | Comic, bold titles |
| Soft drop | 4-8px | 4-8px | 4-8px | 60-80% | Dramatic, cinematic |
| Long drop | 15-30px | 15-30px | 0-5px | 40-60% | 3D extrusion effect |
| No shadow | 0 | 0 | 0 | 0% | Overlapping subject |

Shadow direction must match the composition's lighting direction.

### Extrusion System

Creates a 3D bevel effect without 3D rendering.

**Method 1: Multi-layer offset**
- Layer 1 (bottom): Shadow color, -2px Y offset
- Layer 2: Shadow color, -4px Y offset
- Layer 3: Shadow color, -6px Y offset
- Layer 4 (top): Fill color, main text

Each layer is 2px apart. The result is a stepped 3D effect.

**Method 2: Hard extrusion**
- One duplicate layer shifted 6-10px down
- Fill with a darker version of the main color
- Creates a solid "block" extrusion

**Method 3: Soft extrusion**
- Duplicate layer shifted 15-30px down
- Apply Gaussian blur (10-20px)
- Reduces to 40-60% opacity
- Creates a soft "glowing trail" effect

---

## LAYER 3: Environmental Effects

### Glow

| Glow Type | Method | Use Case |
|-----------|--------|----------|
| Soft outer | Drop shadow with 10-20px blur, white/yellow | Text in dark areas |
| Hard rim | Duplicate text, scale 105%, blur 2px, low opacity | Backlit text |
| Light source | Gradient radiate from behind text | Atmospheric |
| Color bleed | Duplicate text, blur 15px, saturation +50 | Neon/magical themes |

### Gradient Overlay

Applied above the text style, below environmental effects:
- Linear gradient from top-left to bottom-right
- Colors sampled from the thumbnail's dominant 3 colors
- Blend mode: Overlay or Soft Light
- Opacity: 30-50%

### Texture Overlay

- Noise texture at 15-25% opacity
- Screen or Overlay blend mode
- Never more than 30% opacity — subtle is professional
- Alternative: Apply the same noise texture over the ENTIRE thumbnail for cohesion

---

## Complete Treatment Recipes

### Recipe 1: The Classic Brawl Title
```
FONT:        Lilita One, 160px, tracking -8, horizontal scale 110%
FILL:        Gradient (#FFD700 → #FF8C00)
OUTLINE:     8px, #1a1a2e, outside
SHADOW:      Drop shadow 6px/6px/2px, #000000 85%
EXTRUSION:   None
GLOW:        Soft yellow glow behind, 30px blur, 40%
ENVIRONMENT: Gradient overlay on whole canvas
```

### Recipe 2: The Competitive Callout
```
FONT:        Anton, 140px, tracking -15, horizontal scale 100%
FILL:        Solid #FFFFFF
OUTLINE:     6px, #1a1a2e, outside
SHADOW:      Long drop 20px/20px/0px, #1a1a2e 60%
EXTRUSION:   Hard 8px, darker red
GLOW:        None — clean and sharp
ENVIRONMENT: Subtle scanline overlay
```

### Recipe 3: The Comedy Explosion
```
FONT:        Bangers, 180px, tracking 0, rotation 5°
FILL:        Solid #FF4444
OUTLINE:     10px, #1a1a2e, outside
SHADOW:      Hard drop 8px/8px/0px, #000000 100%
EXTRUSION:   None
GLOW:        None
ENVIRONMENT: Particles, impact lines, comic dots
```

### Recipe 4: The Magical/Mythic Title
```
FONT:        Lilita One, 150px, tracking -5, horizontal scale 108%
FILL:        Image texture (magic swirl) at 60% + Gradient purple→pink
OUTLINE:     6px, #2d1b69, outside
SHADOW:      Soft drop 6px/6px/8px, #000000 70%
EXTRUSION:   Soft, 20px blur, 12px offset, purple, 50%
GLOW:        Hard rim, purple/blue, 40%
ENVIRONMENT: Floating particles, light rays
```

### Recipe 5: The Minimalist Dark
```
FONT:        Lilita One, 120px, tracking 0, horizontal scale 100%
FILL:        Empty (outline only)
OUTLINE:     4px, #FFFFFF, outside
SHADOW:      None
EXTRUSION:   None
GLOW:        None
ENVIRONMENT: None — pure minimal
```

---

## Readability at Mobile Scale

### The 25% Test
1. Create the thumbnail at 1920x1080px
2. Resize to 480x270px (25%)
3. If the text is not perfectly readable, the treatment fails

### Minimum Size Reference
- Main title at 1080p: minimum 100px font size
- At that size, a 4px outline = 1px at mobile viewing size
- 6-8px outline at 1080p = 1.5-2px at mobile size — the minimum for visibility

### Contrast Priority
1. Fill vs background contrast (4:1 minimum)
2. Outline vs fill contrast (must be distinct)
3. Shadow vs background contrast (must create separation)

## Treatment Anti-Patterns

❌ Applying the same treatment to every thumbnail
❌ Using default Photoshop layer styles without customization
❌ Shadows that float in a different direction than the lighting
❌ Outlines that are too thin to read at mobile size
❌ Gradients that wash out the text readability
❌ Texture overlays that make text look dirty at small sizes
❌ Glow effects that bleed into surrounding elements
❌ Extrusion that creates visual noise at small sizes
