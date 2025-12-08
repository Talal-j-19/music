# 🤖 AI-Powered Music Generation Endpoint

## Overview

The `/generate-ai` endpoint uses **Google's Gemini AI** to automatically analyze your lyrics and generate the perfect music tags, then creates music using the AceStep model.

## ✨ Features

- **Automatic Tag Generation**: AI analyzes lyrics to determine mood, theme, and style
- **Smart Parameter Optimization**: Automatically adjusts quality settings based on duration
- **Detailed AI Analysis**: Get insights into why specific tags were chosen
- **Fallback System**: Works even without Gemini API (uses keyword-based fallback)

## 🚀 How It Works

1. **You provide**: Just lyrics and duration
2. **Gemini analyzes**: Mood, theme, emotional tone, tempo
3. **AI generates**: 5-8 perfect music genre/style tags
4. **AceStep creates**: Professional music with your lyrics
5. **You receive**: MP3 file + AI analysis

## 📝 API Endpoint

**POST** `/generate-ai`

### Request Body

```json
{
  "lyrics": "[verse]\nWalking through the city lights\nFeeling free tonight\n[chorus]\nDancing in the moonlight\nEverything feels right",
  "duration": 60
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `lyrics` | string | ✅ Yes | - | Song lyrics (supports [verse], [chorus], [bridge] tags) |
| `duration` | float | ❌ No | 60 | Duration in seconds (1-300) |

### Response

```json
{
  "success": true,
  "message": "Music generated successfully with AI-powered tag generation",
  "audio_url": "/download/abc123.mp3",
  "generated_tags": "indie, upbeat, electronic, dreamy, synth, energetic",
  "lyrics": "[verse]\nWalking through the city lights...",
  "seed": 42,
  "ai_analysis": "The lyrics convey an uplifting, energetic mood with urban nightlife themes. The repetitive 'dancing' and 'moonlight' imagery suggests electronic indie production with dreamy synth elements."
}
```

## 🔑 Setup

### 1. Get Gemini API Key (Optional but Recommended)

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

### 2. Add to .env File

```bash
# Required
FAL_KEY=your_fal_api_key_here

# Optional - for AI tag generation
GEMINI_API_KEY=your_gemini_api_key_here
```

### 3. Restart Server

```bash
# Press Ctrl+C to stop
.\start.bat
```

## 💡 Usage Examples

### Example 1: Upbeat Pop Song

**Request:**
```json
{
  "lyrics": "[verse]\nSunshine in my eyes\nFeeling so alive\n[chorus]\nThis is our time\nEverything's sublime",
  "duration": 45
}
```

**AI Might Generate:**
- Tags: `pop, upbeat, energetic, bright, guitar, cheerful`
- Analysis: "Optimistic, high-energy lyrics suggesting upbeat pop with bright instrumentation"

### Example 2: Melancholic Ballad

**Request:**
```json
{
  "lyrics": "[verse]\nEmpty streets and silent nights\nMemories fade from sight\n[chorus]\nI'm lost without you here\nWishing you were near",
  "duration": 60
}
```

**AI Might Generate:**
- Tags: `melancholic, ballad, slow, piano, emotional, indie`
- Analysis: "Introspective, sorrowful tone suggesting slow piano ballad with emotional depth"

### Example 3: Electronic Dance

**Request:**
```json
{
  "lyrics": "[verse]\nLights are flashing all around\nFeet don't touch the ground\n[chorus]\nDance until the morning light\nThis is our night",
  "duration": 90
}
```

**AI Might Generate:**
- Tags: `electronic, dance, edm, energetic, synth, club, upbeat`
- Analysis: "High-energy club atmosphere with dance-focused lyrics suggesting electronic dance music"

### Example 4: Chill Lofi

**Request:**
```json
{
  "lyrics": "[verse]\nRainy days and coffee cups\nTaking life slow\n[chorus]\nJust breathe and let it go\nFind your inner glow",
  "duration": 120
}
```

**AI Might Generate:**
- Tags: `lofi, chill, relaxing, ambient, mellow, acoustic`
- Analysis: "Calm, contemplative mood suggesting lofi chill production with mellow acoustic elements"

## 🎯 Automatic Parameter Optimization

The endpoint automatically adjusts quality based on duration:

| Duration | Steps | Quality |
|----------|-------|---------|
| ≤ 30s | 25 | Fast (good for previews) |
| ≤ 60s | 27 | Standard (balanced) |
| ≤ 120s | 30 | High (better quality) |
| > 120s | 35 | Premium (best quality) |

## 🔄 Fallback System

If Gemini API is not configured, the system uses intelligent keyword-based fallback:

| Keywords in Lyrics | Generated Tags |
|-------------------|----------------|
| dance, party, night, club | electronic, dance, upbeat, energetic |
| sad, cry, alone, lost | melancholic, slow, emotional, piano, indie |
| love, heart, together | romantic, pop, melodic, smooth |
| chill, relax, calm, peace | lofi, chill, ambient, relaxing |
| (default) | pop, melodic, contemporary |

## 📊 Comparison: Manual vs AI Endpoint

### Manual Endpoint (`/generate`)
```json
{
  "tags": "lofi, chill, relaxing",  // You choose
  "lyrics": "...",
  "duration": 60,
  "number_of_steps": 27  // You configure
}
```

### AI Endpoint (`/generate-ai`)
```json
{
  "lyrics": "...",  // AI analyzes and chooses tags
  "duration": 60    // Auto-optimizes steps
}
```

## 🎨 What Gemini Analyzes

The AI examines your lyrics for:

1. **Emotional Tone**
   - Happy, sad, energetic, calm, melancholic, uplifting, etc.

2. **Theme & Subject**
   - Love, heartbreak, celebration, introspection, nature, urban life, etc.

3. **Tempo & Energy**
   - Fast/slow, high/low energy, dynamic/static

4. **Style References**
   - Cultural elements, genre hints, instrumentation cues

5. **Structure**
   - Verse/chorus patterns, lyrical flow, repetition

## 🛠️ Using with cURL

```bash
curl -X POST "http://localhost:8000/generate-ai" \
  -H "Content-Type: application/json" \
  -d "{\"lyrics\": \"[verse]\nYour lyrics here\", \"duration\": 60}"
```

## 🐍 Using with Python

```python
import requests

response = requests.post(
    "http://localhost:8000/generate-ai",
    json={
        "lyrics": "[verse]\nWalking through the city\n[chorus]\nFeeling so free",
        "duration": 60
    }
)

result = response.json()
print(f"Generated Tags: {result['generated_tags']}")
print(f"AI Analysis: {result['ai_analysis']}")
print(f"Download: http://localhost:8000{result['audio_url']}")
```

## 🌐 Using with JavaScript

```javascript
const response = await fetch('http://localhost:8000/generate-ai', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    lyrics: '[verse]\nYour lyrics here\n[chorus]\nMore lyrics',
    duration: 60
  })
});

const result = await response.json();
console.log('Generated Tags:', result.generated_tags);
console.log('AI Analysis:', result.ai_analysis);
```

## ⚡ Performance

- **With Gemini**: +2-5 seconds for AI analysis
- **Without Gemini**: Instant fallback tag generation
- **Total Time**: 30-90 seconds (mostly AceStep generation)

## 🔒 Privacy & Security

- Lyrics are sent to Gemini API for analysis (Google's privacy policy applies)
- No lyrics are stored permanently
- API keys are stored securely in .env file
- Generated music files are stored locally

## 🆚 When to Use Each Endpoint

### Use `/generate` (Manual) When:
- ✅ You know exactly what genre/style you want
- ✅ You want full control over all parameters
- ✅ You're experimenting with specific tag combinations
- ✅ You don't have Gemini API access

### Use `/generate-ai` (AI-Powered) When:
- ✅ You want AI to choose the best tags for your lyrics
- ✅ You're unsure what genre fits your lyrics
- ✅ You want quick, optimized results
- ✅ You want AI analysis of your lyrics' mood

## 🎵 Tips for Best Results

1. **Structure Your Lyrics**: Use [verse], [chorus], [bridge] tags
2. **Be Descriptive**: More detailed lyrics = better AI analysis
3. **Match Duration**: Longer lyrics work better with longer durations
4. **Review AI Tags**: Check the generated tags to learn what works
5. **Iterate**: Try different lyrical styles to see how AI responds

## 🐛 Troubleshooting

### "GEMINI_API_KEY not set"
- **Not an error!** The endpoint will use fallback tag generation
- To enable AI: Add GEMINI_API_KEY to your .env file

### AI generates unexpected tags
- The AI analyzes mood and theme, not just keywords
- Try being more explicit in your lyrics about the desired mood
- Or use the manual `/generate` endpoint for full control

### Slow response
- AI analysis adds 2-5 seconds
- Most time is spent on music generation (30-90s)
- Consider using shorter durations for faster results

## 📚 Related Documentation

- [QUICKSTART.md](QUICKSTART.md) - Getting started guide
- [README.md](README.md) - Complete documentation
- [ENV_SETUP.md](ENV_SETUP.md) - Environment configuration

---

**Ready to create AI-powered music!** 🎶🤖

Try it now: http://localhost:8000/docs#/default/generate_music_ai_generate_ai_post
