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
