# Prompt: Generate Thumbnail Concept

## Objective
Generate a structured thumbnail concept from a video idea.

## Context
The AI has a video idea or topic. Before any visual work, it must produce a concept that defines the communication goal.

## Input
- Video title or description
- Video content summary
- Target audience knowledge

## Process

### Step 1: Extract Core Message
From the video content, extract ONE sentence that captures the most important takeaway.

### Step 2: Define Emotion
What should the viewer feel in the 2 seconds they see the thumbnail?
- Excitement: "This is going to be epic"
- Curiosity: "What happens next?"
- Intensity: "This is serious"
- Humor: "This is funny"
- Shock: "I can't believe this"

### Step 3: Identify Visual Conflict
Every compelling thumbnail has tension:
- Brawler vs. enemy team
- Underdog vs. favorite
- Before vs. after
- Player vs. challenge

### Step 4: Determine Main Subject
Which brawler or element is the most important visual?

### Step 5: Determine Secondary Subjects
What supports the main subject?

### Step 6: Define Focal Point Priority
In order of visual importance:
1. The main subject (always #1)
2. The text (if critical to understanding)
3. Secondary subjects
4. Effects
5. Background

## Output Format
```yaml
concept:
  video_subject: "..."
  core_message: "..."
  emotion: "..."
  visual_conflict: "..."
  main_subject: "..."
  secondary_subjects: ["..."]
  focal_priority: ["main subject", "text", "..."]
```

## Evaluation Criteria
- The core_message is ONE sentence
- The emotion is one of the defined options
- The visual_conflict involves opposing forces
- The focal_priority has the main subject at #1
