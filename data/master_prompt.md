# Anti-Generic-AI Rules for Brawl Stars Thumbnails

## Core Principle

A professional thumbnail is not created by adding more elements.
It is created by making deliberate visual decisions.
Generic AI thumbnails maximize DETAIL. Professional thumbnails maximize INTENTION.

---

## Rule 1: No Random Symmetry

**What AI does:** Places the subject in the exact center with mirrored elements on each side.
**Why it fails:** Symmetrical compositions lack visual tension. Brawl Stars is chaotic gameplay — the thumbnail should reflect that energy.
**Solution:** Use rule of thirds or dynamic diagonal compositions. Offset the subject. Let one side of the frame have more visual weight.

## Rule 2: No Generic Centered Compositions

**What AI does:** Subject dead center, background behind, text below, everything aligned.
**Why it fails:** Every YouTube thumbnail from 2015 looks like this. It signals "I used a template."
**Solution:** Place the subject in the left or right third. Let text occupy the opposite third. Create a Z-pattern or diagonal flow.

## Rule 3: Limit Glow Effects

**What AI does:** Glow on every edge, glow behind text, glow on the subject, glow in the corners.
**Why it fails:** Glow is not lighting. Glow is a cheap way to create fake depth. Over-glow makes the image look muddy and low-contrast.
**Solution:** One glow source maximum. It must correspond to a visible light source in the composition. No random glowing edges.

## Rule 4: No Rogue Particles

**What AI does:** Random floating sparkles, dust motes, lens flares scattered everywhere.
**Why it fails:** Particles without a source look like AI noise. They distract from the focal point.
**Solution:** Particles must originate from a specific source (hypercharge activation, explosion, brawler ability). They should flow in a direction, not float randomly. Maximum 2 particle types per thumbnail.

## Rule 5: One Lens Flare Maximum, and It Must Make Sense

**What AI does:** A lens flare in every empty corner.
**Why it fails:** Lens flares imply a camera pointing at a bright light. If there is no bright light source, there is no lens flare.
**Solution:** Only use lens flare if the composition has a strong light source. Place the flare so it interacts with the subject, not just decorates a corner.

## Rule 6: Consistent Lighting Across All Elements

**What AI does:** The brawler is lit from the top-left. The background is lit from above. The text shadow drops right. The effects glow from within.
**Why it fails:** Inconsistent lighting destroys the illusion of a cohesive scene.
**Solution:** 
- Define ONE primary light direction before starting
- Shadows on ALL elements must fall in the same direction
- Highlights on ALL elements must be on the same side
- Text shadows must match the composition's lighting

## Rule 7: No Unrelated Assets

**What AI does:** Adds random fire, ice, lightning, or generic effect PNGs that have nothing to do with the video.
**Why it fails:** The viewer intuitively knows the effect was pasted in. It breaks immersion.
**Solution:** Every asset must relate to:
- The brawler's abilities (fire for Amber, water for Angêlo)
- The video theme (rank push = competitive effects, funny = comic effects)
- The game's visual language (Brawl Stars has a specific cel-shaded, colorful aesthetic)

## Rule 8: Background Must Support, Not Compete

**What AI does:** Highly detailed, contrast-heavy backgrounds with distinct elements.
**Why it fails:** If the background is as detailed as the foreground, there is no depth hierarchy.
**Solution:**
- Background: Lower contrast, darker, blurred, or simpler
- Midground (subject): Full detail, full contrast
- Foreground: Partial elements crossing the frame
- The background should never be more visually interesting than the subject

## Rule 9: Text Is Part of the Composition, Not an Overlay

**What AI does:** Types text in a font, places it where there is empty space, adds a drop shadow.
**Why it fails:** The text feels disconnected from the image. It looks like text "on top of" a picture.
**Solution:**
- Text interacts with the subject (overlaps, is partially behind)
- Text has environmental treatment (gradient matching the scene)
- Text placement follows the composition's flow, not just "empty space"

## Rule 10: Not Every Element Needs Equal Visual Weight

**What AI does:** Subject, background, effects, text, and decorations all have similar contrast, brightness, and detail level.
**Why it fails:** The viewer does not know where to look. The image feels "busy" without hierarchy.
**Solution:**
- The main subject must have the HIGHEST contrast
- The text must have the SECOND highest contrast
- Background must have the LOWEST contrast
- Effects must not compete with the subject for attention

## Rule 11: No Impossible Typography

**What AI does:** Extremely thin fonts, fonts with strokes that disappear at small sizes, handwritten fonts that are not readable, 3D perspective text with inconsistent perspective.
**Why it fails:** Looks amateur. Does not survive mobile scaling.
**Solution:**
- Only use thick, bold display fonts for main titles
- Test readability at 25% scale
- If a letter becomes unreadable, the font or treatment is wrong

## Rule 12: The "Why" Test

Before placing any element, ask:
- Why is this element here?
- What specific purpose does it serve?
- Does it support the core_message?
- Does it help the focal point?

If an element cannot pass the "why" test, remove it.

---

## The Professional vs AI Checklist

| Element | Generic AI Thumbnail | Professional Thumbnail |
|---------|---------------------|----------------------|
| Subject position | Center | Rule of thirds |
| Lighting | Ambient / None | Directional, consistent |
| Shadows | Drop shadow on everything | Shadow direction matches light |
| Background | High detail, high contrast | Low contrast, supports subject |
| Text | Centered, default font | Integrated, custom styled |
| Effects | Random particles, glows | Source-attached, meaningful |
| Colors | Saturated everything | Controlled palette, hierarchy |
| Depth | Flat layers | 3+ depth layers |
| Readability | Works at full size, fails small | Works at all sizes |

---

## Quick Remediation Checklist

If a thumbnail looks like generic AI:

1. Remove 50% of the effects
2. Add one more depth layer (foreground element)
3. Reduce background contrast by 30%
4. Change text placement to interact with the subject
5. Unify all shadow directions
6. Reduce the number of colors to 3 main colors + 1 accent
7. Check if the composition has a clear focal point
8. Verify that the weakest element is not stealing attention
# Brawl Stars Thumbnail Blueprint System

## Purpose

Before creating any thumbnail, the AI must construct a complete visual blueprint.
The blueprint is NOT the thumbnail. It is the plan for the thumbnail.
Jumping directly to image generation produces generic results.
A blueprint forces deliberate design decisions.

---

## Blueprint Template

```yaml
blueprint:
  # 1. VIDEO SUBJECT
  video_subject: "What is the video about?"
  # Example: "Pushing Maisie to Rank 30", "Every Secret in the New Update"
  
  # 2. CORE MESSAGE (one sentence)
  core_message: "What should the viewer feel or understand immediately?"
  # Example: "This brawler is unstoppable with the new gadget."
  
  # 3. EMOTION
  emotion: "What feeling does the thumbnail convey?"
  # Options: excitement, intensity, curiosity, humor, shock, triumph, mystery
  
  # 4. VISUAL CONFLICT
  visual_conflict: "What opposing forces exist in the composition?"
  # Example: "Maisie vs. an overwhelming enemy team"
  # Example: "One brawler against a boss"
  # The conflict creates visual tension - a thumbnail without tension is boring.
  
  # 5. MAIN SUBJECT
  main_subject:
    brawler: "Name of main brawler"
    skin: "Skin name if applicable"
    pose: "What is the brawler doing?"
    facing_direction: "Left / Right / Forward"
    scale: "How much of the frame does the brawler fill? (30-80%)"
    expression: "Happy / Angry / Determined / Surprised"
    required_asset_type: "brawler_render / portrait / pin"
  
  # 6. SECONDARY SUBJECT(s)
  secondary_subjects:
    - brawler: "Secondary brawler"
      role: "enemy / ally / boss"
      scale: "Relative to main (%)"
    - type: "effect / item / background element"
      role: "context / environment"
  
  # 7. FOCAL POINT
  focal_point: "Where does the eye land first?"
  # Options: center, rule-of-thirds intersection, top-third, bottom-third
  # The focal point must be the MAIN SUBJECT, not the background or text.
  
  # 8. COMPOSITION TYPE
  composition:
    type: "Rule of thirds / centered / diagonal / dynamic / framed / split"
    grid_placement:
      main_subject: "Which grid section?"
      text: "Which grid section?"
      secondary: "Which grid section?"
  
  # 9. DEPTH STRUCTURE
  depth_layers:
    foreground: "What is closest to camera? (0-20% depth)"
    midground: "Where is the main subject? (40-70% depth)"
    background: "What is behind everything? (80-100% depth)"
    overlay: "Particles, effects, text (0% depth - on top of everything)"
  
  # 10. LIGHTING DIRECTION
  lighting:
    primary_direction: "Top-left / Top-right / Bottom-up / Backlit / Ambient"
    secondary_direction: "Complementary fill direction"
    shadow_direction: "Must match primary direction"
  
  # 11. COLOR PALETTE
  color_palette:
    dominant: "Primary color (usually the brawler's main color)"
    accent: "Secondary color for contrast"
    background: "Background color range"
    text: "Text fill color"
    outline: "Outline/shadow color"
  
  # 12. TEXT CONTENT
  text:
    main_title: "2-5 words — the video title"
    subtitle: "Optional supporting text"
    placement: "Where on the grid does text sit?"
    treatment_recipe: "Which treatment recipe from the typography library?"
  
  # 13. TYPOGRAPHY
  typography:
    primary_font: "Font name"
    secondary_font: "Font name (if used)"
    size_hierarchy:
      main: "px"
      subtitle: "px"
      context: "px"
    effects: ["outline", "shadow", "glow", "extrusion"]
  
  # 14. REQUIRED ASSETS
  required_assets:
    - type: "brawler_render"
      brawler: "Name"
      condition: "Facing right, attacking pose"
    - type: "background"
      theme: "Matching video theme"
      condition: "Dark left side for text placement"
    - type: "effect"
      description: "Explosion / energy / particles"
    - type: "pin or spray"
      description: "Decorative accent"
  
  # 15. EFFECTS
  effects:
    - type: "particle"
      description: "Energy particles floating"
    - type: "light_ray"
      description: "Rim light from top-left"
    - type: "impact_lines"
      description: "Speed lines behind brawler"
  
  # 16. NEGATIVE SPACE
  negative_space: "Where is the empty area for breathing room?"
  # Negative space is NOT wasted space. It is strategic empty area that:
  # - Allows the focal point to breathe
  # - Provides a clean area for text
  # - Creates visual rhythm between dense and empty areas
  
  # 17. MOBILE READABILITY CHECK
  mobile_check:
    main_subject_visible: true/false
    text_readable: true/false
    focal_point_clear: true/false
    colors_distinct: true/false
  
  # 18. FINAL QUALITY CHECK
  quality_check:
    not_generic_ai: "Why does this not look like AI?"
    intentional_design: "What specific design decision makes this work?"
    weakest_element: "What could be better?"
```

---

## Blueprint Usage Workflow

```
1. START with video_subject and core_message
   → This determines EVERYTHING downstream

2. Derive emotion from the core_message
   → A rank push = intensity, a funny moment = humor

3. Define visual_conflict from the video context
   → Every good thumbnail has tension between two forces

4. Select main_subject based on the video content
   → The most important brawler/element

5. Choose composition based on the subject and conflict
   → Diagonal for action, centered for character spotlight

6. Build depth_layers to create a 3D feel
   → Never less than 3 depth layers

7. Design lighting that supports the emotion
   → Dramatic = hard directional, Fun = soft ambient

8. Select color_palette from the brawler's dominant color
   → Pull from brawlers.json color field

9. Write minimal text that communicates instantly
   → 2-5 words for the main message

10. Search assets using the asset database
    → Use the structured asset_search prompt system

11. Verify mobile readability
    → Pass the 25% test

12. Quality check against anti-generic-AI rules
    → Never skip this step
```

---

## Blueprint Examples

### Example 1: Competitive Rank Push
```yaml
blueprint:
  video_subject: "Pushing Maisie to Rank 30 Solo"
  core_message: "Maisie is broken with the new hypercharge"
  emotion: intensity
  visual_conflict: "One brawler against a swarm of enemies"
  main_subject:
    brawler: "Maisie"
    pose: "Attacking, hypercharge activated"
    facing_direction: "Right"
    scale: 45%
    expression: "Determined"
  composition:
    type: "diagonal"
    grid_placement:
      main_subject: "Left third"
      text: "Right third"
      secondary: "Lower right"
  depth_layers:
    foreground: "Hypercharge energy particles"
    midground: "Maisie in action pose"
    background: "Dark arena background with enemy silhouettes"
    overlay: "Impact lines, damage numbers"
  lighting:
    primary_direction: "Top-left"
    shadow_direction: "Bottom-right"
  color_palette:
    dominant: "#FFD700"  # Maisie's hypercharge gold
    accent: "#FF4444"    # Enemy threat red
    background: "#1a1a2e" # Dark arena
    text: "White with gold gradient"
  text:
    main_title: "MAISIE R30"
    subtitle: "SOLO QUEUE"
    placement: "Right third, bottom aligned"
  mobile_check:
    main_subject_visible: true
    text_readable: true
```

### Example 2: Funny Montage
```yaml
blueprint:
  video_subject: "The WORST Frank Play You Will Ever See"
  core_message: "This is hilarious and painful"
  emotion: humor
  visual_conflict: "Frank's giant hitbox vs. every enemy attack"
  main_subject:
    brawler: "Frank"
    pose: "About to be hit by everything"
    facing_direction: "Forward (facepalm)"
    scale: 60%
    expression: "Sad/comical"
  composition:
    type: "centered"
    grid_placement:
      main_subject: "Center"
      text: "Top"
  depth_layers:
    foreground: "Dodged projectiles flying past"
    midground: "Frank facepalming"
    background: "Simple arena floor"
    overlay: "Comic impact lines, sweat drops"
  color_palette:
    dominant: "#4A90D9"  # Frank color
    accent: "#FF6B35"    # Comedy orange
    background: "#2d2d4a"
    text: "White with orange outline"
  text:
    main_title: "BRUH"
    placement: "Top center"
  mobile_check:
    main_subject_visible: true
    text_readable: true
```
# User Style Analysis

## Status
No user-created thumbnails or visual references are present in the project.

## Observed Preferences
None — no style references available to analyze.

## Inferred Preferences
Based on the user's decision to build this knowledge system:

- **Likely preference for:** Intentional, professional-looking graphic design over generic AI output
- **Likely preference for:** Composition systems and blueprints over freeform creation
- **Likely preference for:** Reusable, structured workflows over one-off generation
- **Likely preference for:** Using real game assets rather than AI-generated elements
- **Likely preference for:** Education and skill-building (the user invested in coding the database)

## Uncertain Preferences
- Preferred composition style (centered? dynamic? minimal?)
- Preferred text treatment complexity (heavy effects? clean minimal?)
- Preferred color approach (brawler-accurate? high contrast? pastel?)
- Preferred font choices (does the user own any fonts?)
- Preferred density level (packed thumbnails? spacious?)

## Recommendation
When the user creates their first thumbnail with this system, study it carefully.
Update this document with the observed preferences.
Do not assume preferences that are not yet demonstrated.

## Style Development Path
1. Start with the blueprint system — produce the first thumbnail
2. Analyze what feels right and what feels off
3. Document recurring choices as "confirmed preferences"
4. Refine the prompts and rules to match
5. After 5-10 thumbnails, the user's personal style will be clear
