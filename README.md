# AceStep Music Generator API

A FastAPI-based application that generates music with lyrics using the AceStep AI model from fal.ai.

## Features

- 🎵 Generate music from text prompts and lyrics
- 🎼 Control music style with genre tags
- ⏱️ Customize audio duration (1-300 seconds)
- 🎚️ Adjust generation quality with step count
- 🔄 Automatic conversion to MP3 format
- 📝 Support for structured lyrics (verse, chorus, bridge)
- 🎹 Instrumental music generation

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio conversion)
- fal.ai API key

### Installing FFmpeg

**Windows:**
```bash
# Using Chocolatey
choco install ffmpeg

# Or download from https://ffmpeg.org/download.html
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## Setup

1. **Clone or navigate to the project directory:**
```bash
cd d:\musiclyrics
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/macOS
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up your fal.ai API key:**
   - Get your API key from [fal.ai dashboard](https://fal.ai/dashboard/keys)
   - Create a `.env` file or set environment variable:

```bash
# Windows PowerShell
$env:FAL_KEY="your_api_key_here"

# Windows CMD
set FAL_KEY=your_api_key_here

# Linux/macOS
export FAL_KEY="your_api_key_here"
```

## Running the Application

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API:** http://localhost:8000
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## API Endpoints

### 1. Generate Music
**POST** `/generate`

Generate music from text and lyrics.

**Request Body:**
```json
{
  "tags": "lofi, hiphop, chill",
  "lyrics": "[verse]\nWalking down the street\n[chorus]\nFeeling the beat",
  "duration": 60,
  "number_of_steps": 27,
  "seed": 42
}
```

**Parameters:**
- `tags` (required): Comma-separated genre tags (e.g., "lofi, hiphop, drum and bass, trap, chill")
- `lyrics` (optional): Lyrics to sing. Use `[inst]` or `[instrumental]` for instrumental music. Use `[verse]`, `[chorus]`, `[bridge]` for structure.
- `duration` (optional, default: 60): Duration in seconds (1-300)
- `number_of_steps` (optional, default: 27): Generation steps (10-100, higher = better quality)
- `seed` (optional): Random seed for reproducibility

**Response:**
```json
{
  "success": true,
  "message": "Music generated successfully",
  "audio_url": "/download/abc123.mp3",
  "seed": 42,
  "tags": "lofi, hiphop, chill",
  "lyrics": "[verse]\nWalking down the street..."
}
```

### 2. Download Music
**GET** `/download/{filename}`

Download the generated music file.

### 3. Health Check
**GET** `/health`

Check if the API is running and properly configured.

### 4. Root
**GET** `/`

Get API information and available endpoints.

## Usage Examples

### Using cURL

**Generate instrumental music:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d "{\"tags\": \"lofi, chill, ambient\", \"lyrics\": \"[inst]\", \"duration\": 30}"
```

**Generate music with lyrics:**
```bash
curl -X POST "http://localhost:8000/generate" \
  -H "Content-Type: application/json" \
  -d "{\"tags\": \"pop, upbeat\", \"lyrics\": \"[verse]\nSunshine in my eyes\n[chorus]\nFeeling so alive\", \"duration\": 45}"
```

### Using Python

```python
import requests

# Generate music
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "tags": "jazz, smooth, relaxing",
        "lyrics": "[inst]",
        "duration": 60,
        "number_of_steps": 27
    }
)

result = response.json()
print(f"Generated music: {result['audio_url']}")

# Download the file
if result["success"]:
    audio_response = requests.get(f"http://localhost:8000{result['audio_url']}")
    with open("generated_music.mp3", "wb") as f:
        f.write(audio_response.content)
    print("Music saved to generated_music.mp3")
```

### Using JavaScript/Fetch

```javascript
// Generate music
const response = await fetch('http://localhost:8000/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    tags: 'electronic, dance, energetic',
    lyrics: '[inst]',
    duration: 60,
    number_of_steps: 27
  })
});

const result = await response.json();
console.log('Generated music:', result.audio_url);

// Download the file
if (result.success) {
  const audioResponse = await fetch(`http://localhost:8000${result.audio_url}`);
  const blob = await audioResponse.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'generated_music.mp3';
  a.click();
}
```

## Lyrics Structure

Use these tags to structure your lyrics:

- `[verse]` - Verse section
- `[chorus]` - Chorus section
- `[bridge]` - Bridge section
- `[inst]` or `[instrumental]` - Instrumental music (no lyrics)

**Example:**
```
[verse]
Walking down the empty street
Feeling the rhythm in my feet

[chorus]
Music in the air tonight
Everything feels so right

[bridge]
Let the melody take control

[chorus]
Music in the air tonight
Everything feels so right
```

## Genre Tags Examples

- **Lofi Hip Hop:** `lofi, hiphop, chill, relaxing`
- **Electronic Dance:** `electronic, dance, edm, energetic`
- **Jazz:** `jazz, smooth, sophisticated, instrumental`
- **Rock:** `rock, guitar, energetic, powerful`
- **Ambient:** `ambient, atmospheric, calm, meditation`
- **Pop:** `pop, upbeat, catchy, modern`
- **Classical:** `classical, orchestral, elegant`

## Troubleshooting

### "FAL_KEY environment variable not set"
Make sure you've set the FAL_KEY environment variable with your fal.ai API key.

### "FFmpeg not found" or audio conversion errors
Install FFmpeg following the instructions in the Prerequisites section.

### Generation takes too long
- Reduce `number_of_steps` (minimum 10)
- Reduce `duration`
- The first request may take longer as the model initializes

### Audio quality issues
- Increase `number_of_steps` (up to 100)
- Try different genre tags
- Experiment with different seeds

## Project Structure

```
musiclyrics/
├── main.py              # FastAPI application
├── requirements.txt     # Python dependencies
├── .env.example        # Example environment variables
├── README.md           # This file
└── generated_music/    # Output directory (created automatically)
```

## API Documentation

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

These provide interactive API documentation where you can test endpoints directly.

## License

This project uses the AceStep API from fal.ai. Please refer to [fal.ai's terms of service](https://fal.ai/terms) for API usage terms.

## Support

For issues with:
- **This application:** Create an issue in the project repository
- **AceStep API:** Visit [fal.ai documentation](https://fal.ai/models/fal-ai/ace-step)
- **fal.ai account:** Contact [fal.ai support](https://fal.ai/support)
