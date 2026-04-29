# 🧠 Gemini Prompt Refinement

## Goal
Optimize the AI tag generation to produce more focused, high-quality results for the AceStep model.

## Changes Made

### 1. Tag Limit
- **Old**: 5-8 tags
- **New**: **3-7 tags** (Strict limit)
- **Reason**: Fewer, more precise tags often yield better generation results than a long list of potentially conflicting tags.

### 2. Tag Categories
Defined specific categories compatible with AceStep:
1. **Primary Genre** (e.g., pop, rock, electronic, lofi)
2. **Mood/Energy** (e.g., upbeat, melancholic, chill)
3. **Tempo/Style** (e.g., fast, slow, atmospheric)
4. **Instrumentation** (e.g., piano, guitar, synth)

### 3. Critical Rules
- Choose only the **MOST ESSENTIAL** tags
- Prioritize genre and mood over instrumentation
- Tags must be single words or short phrases
- Tags must work harmoniously together

### 4. Analysis Requirements
- Identify primary emotion/mood
- Explain tag choices concisely (1 sentence)

## Example Output

**Lyrics:**
*"Empty streets and silent nights, memories fade from sight"*

**Old Output:**
`melancholic, ballad, slow, piano, emotional, indie, sad, acoustic`

**New Output:**
`lofi, melancholic, piano, chill`

## Benefits
- **Better Music Quality**: Focused tags reduce model confusion
- **More Consistent Results**: Strict categories ensure compatibility
- **Faster Generation**: Fewer tags to process
- **Clearer Analysis**: Concise explanation of choices

## Fallback System Updated
The keyword-based fallback system was also updated to respect the 3-7 tag limit:
- Sad lyrics: `melancholic, slow, piano, indie` (4 tags)
- Love lyrics: `pop, romantic, melodic, smooth` (4 tags)
