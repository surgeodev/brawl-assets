# Prompt: Design Depth

## Objective
Create a convincing three-dimensional depth structure using the selected assets.

## Input
- Blueprint depth layers
- Selected assets
- Composition layout
- Lighting direction

## Depth Layer System

### Layer 0: Overlay (topmost, 0% depth)
- Text
- Particles crossing in front of everything
- UI elements
- Blend mode: Normal or Screen
- Purpose: These elements exist "in front of" the screen

### Layer 1: Foreground (10-30% depth)
- Elements crossing frame edges
- Blurred or darkened compared to midground
- Usually partially cropped by frame
- Purpose: Frame the composition, create depth reference
- Techniques: 
  - Large scale, partial visibility
  - Darken by 20-30%
  - Add slight blur (2-4px) if appropriate

### Layer 2: Midground (40-70% depth)
- Main subject
- Highest detail, highest contrast
- Full visibility
- Purpose: The focal point of the thumbnail
- Techniques:
  - Full detail rendering
  - Highest contrast in the composition
  - Sharp focus

### Layer 3: Background (80-100% depth)
- Arena or theme background
- Darker, lower contrast than midground
- Purpose: Provide context without competing
- Techniques:
  - Reduce contrast by 30-50%
  - Darken by 20-40%
  - Blur (8-15px) for depth of field effect
  - Gradient darkening on edges

## Depth Creation Techniques

### Size Scaling
Elements further away = smaller. Elements closer = larger.
Rate: Every 10% of depth = roughly 15% size difference.

### Color Saturation
- Foreground: 80-100% saturation
- Midground: 90-100% saturation  
- Background: 40-60% saturation
- Overlay: Variable (text is high contrast)

### Brightness
- Foreground: 60-80% brightness (can be silhouette)
- Midground: 80-100% brightness (full visibility)
- Background: 50-70% brightness (darker)
- Overlay: 90-100% brightness (text must be readable)

### Blur
- Foreground: 0-4px (optional, for motion feel)
- Midground: 0px (sharp)
- Background: 4-15px (depth of field)

### Overlap
Elements in closer layers must physically overlap elements in further layers.
No element should exist in isolation — each layer interacts with the next.

## Depth Anti-Patterns
- ❌ All layers at the same contrast level
- ❌ No blur differentiation between layers
- ❌ Elements that float without touching/interacting
- ❌ Background as bright as the subject
- ❌ Missing foreground layer (flat composition)

## Output
Depth structure with exact specifications for each layer:
- Layer number and name
- Elements assigned
- Blur amount
- Brightness adjustment
- Saturation adjustment
- Scale relative to frame
- Overlap/interaction with adjacent layers
