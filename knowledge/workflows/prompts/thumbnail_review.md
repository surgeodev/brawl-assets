# Prompt: Review Thumbnail

## Objective
Critically evaluate a completed or in-progress thumbnail against the quality standards.

## Process

### Step 1: Check Core Requirements
```
□ Is the core_message communicated in 2 seconds?
□ Is the emotion appropriate for the video?
□ Is the main subject immediately identifiable?
□ Can a viewer understand the video topic from the thumbnail alone?
```

### Step 2: Check Composition
```
□ Is the composition one of the defined types (diagonal, rule-of-thirds, etc.)?
□ Is there a clear focal point?
□ Does the eye follow a path (Z, diagonal, circular)?
□ Is visual weight distributed asymmetrically (60:40 or 40:60)?
□ Is there sufficient negative space (20-30%)?
```

### Step 3: Check Depth
```
□ Are there at least 3 depth layers?
□ Is the main subject in the midground?
□ Is the background lower contrast than the midground?
□ Is there a foreground element framing the composition?
□ Do layers overlap and interact?
```

### Step 4: Check Lighting
```
□ Is there one primary light direction?
□ Do ALL shadows fall in the same direction?
□ Do ALL highlights face the light source?
□ Does text shadow match the composition's lighting?
□ Is there a three-value system (highlight, midtone, shadow)?
```

### Step 5: Check Color
```
□ Are there 3 dominant colors maximum + 1 accent?
□ Is the dominant color pulled from the brawler's palette?
□ Is contrast adequate (4:1 minimum for text)?
□ Are adjacent colors distinct enough?
```

### Step 6: Check Typography
```
□ Is the font appropriate for the video's emotion?
□ Is the main text 2-5 words?
□ Does the text have outline + shadow?
□ Is text readable at 25% scale?
□ Does text placement interact with the composition?
□ Is the treatment recipe followed?
```

### Step 7: Check Effects
```
□ Are there 2 effect types maximum?
□ Do effects have visible sources?
□ Do effects have clear direction?
□ Do effects support the focal point?
□ Are effects not overpowering the subject?
```

### Step 8: Anti-Generic-AI Check
```
□ Is the composition NOT centered/symmetrical?
□ Is the background NOT competing with the subject?
□ Is the lighting consistent across all elements?
□ Are there no random/unrelated assets?
□ Is there a clear visual hierarchy?
□ Is the text treated as part of the composition?
□ Does the thumbnail NOT rely on excessive glow/particles?
```

## Review Output

```yaml
review_result:
  passed: true/false
  score: "out of 8 sections passed"
  
  failures:
    - section: "Composition"
      issue: "Specific problem"
      fix: "How to fix it"
  
  strengths:
    - "What works well"
  
  verdict: "pass / minor_fixes / major_rework"
  
  if_pass:
    - "Ready for export"
  
  if_minor_fixes:
    - "List of specific fixes needed"
  
  if_major_rework:
    - "Return to concept phase with specific feedback"
```

## Evaluation Criteria
- A thumbnail must pass ALL 8 sections to be considered complete
- Minor fixes = issues in 1-2 sections that take <5 minutes each
- Major rework = issues in 3+ sections or fundamental problems with concept/blueprint
- If major rework is needed, restart from concept_generation.md with the review feedback
