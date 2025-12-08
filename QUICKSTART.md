# Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Setup (One-time)

Run the setup script:
```bash
setup.bat
```

This will:
- Create a virtual environment
- Install all Python dependencies

### Step 2: Configure API Key

Run the environment setup:
```bash
.\setup_env.bat
```

This will:
1. Create a `.env` file
2. Open it in Notepad
3. Get your API key from [fal.ai dashboard](https://fal.ai/dashboard/keys)
4. Replace `your_fal_api_key_here` with your actual key
5. Save the file

### Step 3: Start the Server

```bash
.\start.bat
```

That's it! The API will be running at http://localhost:8000

---

## 📝 Using the API

### Option 1: Interactive Documentation (Easiest)

1. Open http://localhost:8000/docs in your browser
2. Click on the `/generate` endpoint
3. Click "Try it out"
4. Fill in the parameters:
   - **tags**: `lofi, chill, relaxing`
   - **lyrics**: `[inst]` (for instrumental)
   - **duration**: `30`
5. Click "Execute"
6. Download your music from the response URL!

### Option 2: Using cURL

```bash
curl -X POST "http://localhost:8000/generate" ^
  -H "Content-Type: application/json" ^
  -d "{\"tags\": \"lofi, chill\", \"lyrics\": \"[inst]\", \"duration\": 30}"
```

### Option 3: Using Python Test Client

```bash
venv\Scripts\activate.bat
python test_client.py
```

---

## 🎵 Music Generation Tips

### For Instrumental Music
```json
{
  "tags": "lofi, jazz, chill, ambient",
  "lyrics": "[inst]",
  "duration": 60
}
```

### For Music with Lyrics
```json
{
  "tags": "pop, upbeat, energetic",
  "lyrics": "[verse]\nSunshine in my eyes\n[chorus]\nFeeling so alive",
  "duration": 45
}
```

### Popular Genre Combinations
- **Lofi Chill**: `lofi, hiphop, chill, relaxing`
- **Electronic Dance**: `electronic, dance, edm, energetic`
- **Jazz Smooth**: `jazz, smooth, sophisticated, instrumental`
- **Ambient Meditation**: `ambient, atmospheric, calm, meditation`
- **Rock Energy**: `rock, guitar, energetic, powerful`

---

## ⚙️ Advanced Configuration

### Adjust Quality
Higher steps = better quality but slower:
```json
{
  "number_of_steps": 50
}
```

### Reproducible Results
Use the same seed to get the same output:
```json
{
  "seed": 42
}
```

### Longer Duration
Generate up to 5 minutes:
```json
{
  "duration": 300
}
```

---

## 🔧 Troubleshooting

### ".env file not found"
**Solution**: Run the setup script:
```bash
.\setup_env.bat
```

Or manually create it:
```bash
copy .env.example .env
notepad .env
```
Then add your API key: `FAL_KEY=your_key_here`

### "FFmpeg not found"
**Solution**: Install FFmpeg:
```bash
choco install ffmpeg
```
Or download from https://ffmpeg.org/download.html

### Server won't start
**Solution**: Make sure you're in the virtual environment:
```bash
venv\Scripts\activate.bat
python main.py
```

### Generation is slow
**Solution**: 
- Reduce `number_of_steps` to 20
- Reduce `duration` to 30 seconds
- First request is always slower (model initialization)

---

## 📁 Project Files

- `main.py` - FastAPI server
- `test_client.py` - Test script
- `requirements.txt` - Python dependencies
- `setup.bat` - One-time setup script
- `start.bat` - Start the server
- `README.md` - Full documentation
- `generated_music/` - Your generated music files

---

## 🆘 Need Help?

1. Check the full README.md for detailed documentation
2. Visit http://localhost:8000/docs for interactive API docs
3. Check [fal.ai documentation](https://fal.ai/models/fal-ai/ace-step)

---

## 🎉 Example Workflow

1. **Start the server**: `start.bat`
2. **Open browser**: http://localhost:8000/docs
3. **Try the `/generate` endpoint**:
   - tags: `lofi, chill, relaxing`
   - lyrics: `[inst]`
   - duration: `30`
4. **Click Execute**
5. **Copy the audio_url** from the response
6. **Visit**: http://localhost:8000/download/[filename].mp3
7. **Enjoy your music!** 🎵

Happy music making! 🎶
