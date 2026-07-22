# Brawl Stars Thumbnail Typography Rules

## Core Principle

Typography in Brawl Stars thumbnails is not "text on top of an image."
Typography is a structural element of the composition.
Text is a SHAPE first, and readable content second.

## Font Selection Rules

### Rule 1: Only two fonts per thumbnail
- **Primary font:** For the main message (brawler name, video title)
- **Secondary font:** For supporting text (stat, label, call-to-action)
- Never use three or more fonts in a single thumbnail

### Rule 2: Lilita One is the default primary font
- It matches Brawl Stars' brand identity
- Its rounded weight works at small mobile sizes
- Only deviate from Lilita One when the theme demands it (e.g., Anton for competitive, Righteous for retro)

### Rule 3: Font must match the video's emotional tone
| Video Tone | Recommended Font |
|------------|-----------------|
| Competitive / esports | Anton, Passion One |
| Funny / meme | Bangers |
| Guide / educational | Lilita One |
| Story / lore | Lilita One |
| Co-op / team focused | Luckiest Guy |
| Retro / arcade | Righteous |
| Serious / dramatic | Lilita One (narrowed) |

### Rule 4: Never use system default fonts
- DejaVu Sans, Arial, Helvetica = generic content
- Brawl Stars thumbnails must feel intentionally designed
- Download and use display fonts

## Text Length Rules

### Rule 5: Maximum 5 words in the main title
- Mobile thumbnails are viewed at 200-400px wide
- At that size, more than 5 words becomes unreadable
- 2-3 words is optimal

### Rule 6: Maximum 15 characters in the main title line
- Lilita One at reasonable size fits ~15 chars
- Longer text must be split into multiple lines with hierarchy

### Rule 7: Secondary text must be 50-70% smaller than main text
- Creates clear hierarchy
- Ensures the main message reads first

## Typography Scale & Hierarchy

### Rule 8: Three-level hierarchy
```
Level 1: Main title (largest)    — 100% size reference
Level 2: Subtitle / stat         — 50-70% of main
Level 3: Context / label         — 30-40% of main
```

### Rule 9: Main title fills 20-35% of thumbnail height
- Too small = lost on mobile
- Too large = no room for visual content

## Typography Treatment Rules

### Rule 10: Every text element needs an outline
- Minimum 4px outline at 1080p canvas
- Dark outline (#1a1a2e or #000000) with 80-100% opacity
- Outline color must contrast with the fill color

### Rule 11: Every text element needs a shadow
- Offset shadow: 3-8px right, 3-8px down
- Shadow color: dark, matching the darkest tone in the thumbnail
- Blur: 2-4px for sharp look, 0-2px for crisp comic style
- Never use pure black for shadows — sample the  darkest color in the image

### Rule 12: Text must have a fill gradient
- 2-3 color stops
- Top-to-bottom or diagonal
- Colors should be pulled from the brawler's palette or video theme
- Example: Yellow (#FFD700) → Orange (#FF6B00) for a fiery brawler

### Rule 13: Horizontal stretch (105-115%) for main titles
- Creates a wider, more cinematic feel
- Lilita One responds well to stretch
- Never stretch more than 120% — it becomes distorted

### Rule 14: Tight tracking (-5 to -10) for impact text
- Letters closer together = more aggressive
- Loose tracking = weak, casual
- Brawl Stars is energetic — tighten the spacing

## Color & Readability

### Rule 15: Ensure 4:1 contrast ratio between text and background
- Test readability by viewing at 25% size
- If the text disappears when scaled down, it is not bold enough

### Rule 16: Never use pure white text on bright backgrounds
- Use off-white (#F0F0F0) or a tinted highlight color instead
- Add a dark shadow/outline layer beneath

### Rule 17: Pull highlight colors from the brawler's dominant color
- Each brawler has a defined color in brawlers.json
- Use that color as the text fill or gradient accent
- Creates visual cohesion between text and subject

## Advanced Techniques

### Rule 18: Color separation for titles
- Duplicate the text layer three times
- Layer 1 (back): Dark outline, moved 4px right/down
- Layer 2 (middle): Main fill color, shifted 2px
- Layer 3 (front): Highlight color, offset 1px
- Creates a dimensional "3D" text look

### Rule 19: Text intersecting with the subject
- Allow text to partially overlap the brawler
- The outline/shadow creates separation
- This creates depth instead of "text box on top"

### Rule 20: Texture overlay on text
- After text is styled, overlay a subtle noise or grunge texture
- 10-20% opacity
- Makes the text feel like part of the game world, not "typed in Photoshop"

## Typography Anti-Patterns

❌ Centered text for every thumbnail
❌ Text placed in the same position every time
❌ Pure white text with no outline
❌ Text that does not interact with the composition
❌ Shadow direction that contradicts lighting direction
❌ Fonts that do not match the emotional tone
❌ More than 7 words in the main message
❌ Text that covers the subject's face
❌ Text with equal weight — no hierarchy
❌ Text effects that look like default Photoshop styles
