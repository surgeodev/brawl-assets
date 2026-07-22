# Prompt: Design Effects

## Objective
Add visual effects that enhance the composition without overwhelming it.

## Input
- Completed composition
- Lighting scheme
- Depth structure
- Typography treatment

## Design Rules

### Rule 1: Effects Must Have a Visible Source
- Energy effects → originate from the brawler's attack or super
- Particles → originate from an impact point or ability activation
- Light rays → originate from a visible light source
- Smoke/dust → originate from ground impact or movement

### Rule 2: Effects Must Follow a Direction
All effects must move in a consistent direction matching the composition's energy flow:
- Diagonal: Follows the composition's diagonal
- Radial: Outward from the impact point
- Gravity-affected: Particles drift downward

### Rule 3: Maximum 2 Effect Types Per Thumbnail
Choose from:
- Impact effects (explosion, burst, ring)
- Energy effects (glow, aura, particles)
- Motion effects (speed lines, motion blur, trails)
- Atmospheric effects (dust, light rays, fog)
- Damage effects (scratches, cracks, screen shake indicators)

### Rule 4: Effects Must Not Compete with the Focal Point
- Effects should be 30-50% opacity maximum
- Effects should not cover the subject's face or key details
- Effects should guide the eye toward the focal point, not away from it

## Effect Library

### Speed Lines
```
Usage: Behind the main subject, indicating fast movement
Direction: Opposite to the subject's facing direction
Length: 20-40% of frame
Opacity: 20-40%
Blend: Screen or Linear Dodge
Color: Match the background (lighter)
```

### Impact Burst
```
Usage: At the point of a hit or super activation
Position: On the enemy or impact point
Radius: 15-25% of frame
Opacity: 40-60%
Blend: Screen
Colors: Brawler's energy color + white
```

### Energy Aura
```
Usage: Around the main subject (hypercharge, super ready)
Position: Behind the subject, slightly larger
Scale: 110-130% of subject size
Opacity: 30-50%
Blend: Screen or Overlay
Colors: Match brawler's hypercharge/super color
```

### Light Rays
```
Usage: From the light source direction
Position: Radiating from light source
Number: 3-7 rays
Opacity: 10-25%
Blend: Screen
```

### Floating Particles
```
Usage: Ambient atmosphere
Density: 5-15 particles
Size: 2-10px
Opacity: 30-60%
Motion: Slow drift upward or follow composition flow
```

## Effect Anti-Patterns
- ❌ Effects in every empty space (clutter)
- ❌ Effects that overlap the subject's face
- ❌ Effects without a source or direction
- ❌ Effects brighter than the subject
- ❌ More than 2 effect types in one thumbnail
- ❌ Generic lens flares without a light source

## Output
Effects specification:
- Effect type(s) selected (max 2)
- Position for each effect
- Size/scale relative to frame
- Color matching palette
- Opacity settings
- Blend mode
- How the effect supports the focal point
