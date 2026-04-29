from fastapi import FastAPI, HTTPException, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import asyncio
import fal_client
import os
import httpx
from pathlib import Path
import uuid
from pydub import AudioSegment
import tempfile
from dotenv import load_dotenv
import google.generativeai as genai
import shutil
from contextlib import suppress
from datetime import datetime, timedelta, timezone

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

app = FastAPI(
    title="AceStep Music Generator API",
    description="Generate music with lyrics using AceStep AI",
    version="1.0.0"
)

# Add CORS middleware to allow frontend to communicate with API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create output directory for generated files
OUTPUT_DIR = Path("generated_music")
OUTPUT_DIR.mkdir(exist_ok=True)
GENERATED_MUSIC_RETENTION_DAYS = int(os.getenv("GENERATED_MUSIC_RETENTION_DAYS", "2"))
GENERATED_MUSIC_CLEANUP_INTERVAL_SECONDS = int(
    os.getenv("GENERATED_MUSIC_CLEANUP_INTERVAL_SECONDS", str(24 * 60 * 60))
)


def cleanup_generated_music_files() -> int:
    """Delete generated audio files older than the retention window."""
    cutoff_time = datetime.now(timezone.utc) - timedelta(days=GENERATED_MUSIC_RETENTION_DAYS)
    deleted_files = 0

    for file_path in OUTPUT_DIR.iterdir():
        if not file_path.is_file():
            continue

        try:
            modified_time = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
        except FileNotFoundError:
            continue

        if modified_time < cutoff_time:
            file_path.unlink(missing_ok=True)
            deleted_files += 1

    return deleted_files


async def cleanup_generated_music_loop() -> None:
    while True:
        try:
            deleted_files = await asyncio.to_thread(cleanup_generated_music_files)
            if deleted_files:
                print(f"Cleaned up {deleted_files} expired generated music file(s)")
        except Exception as exc:
            print(f"Error cleaning generated music files: {exc}")

        await asyncio.sleep(GENERATED_MUSIC_CLEANUP_INTERVAL_SECONDS)


cleanup_task: asyncio.Task | None = None


class MusicGenerationRequest(BaseModel):
    """Request model for music generation"""
    tags: str = Field(
        ...,
        description="Comma-separated list of genre tags (e.g., 'lofi, hiphop, drum and bass, trap, chill')",
        example="lofi, hiphop, chill"
    )
    lyrics: str = Field(
        default="",
        description="Lyrics to be sung. Use [inst] or [instrumental] for instrumental music. Use [verse], [chorus], [bridge] for structure.",
        example="[verse]\nWalking down the street\n[chorus]\nFeeling the beat"
    )
    duration: float = Field(
        default=60,
        ge=1,
        le=300,
        description="Duration of the audio in seconds (1-300)",
        example=60
    )
    number_of_steps: int = Field(
        default=27,
        ge=10,
        le=100,
        description="Number of generation steps (higher = better quality but slower)",
        example=27
    )
    seed: int | None = Field(
        default=None,
        description="Random seed for reproducibility. Leave empty for random generation.",
        example=42
    )



class MusicGenerationResponse(BaseModel):
    """Response model for music generation"""
    success: bool
    message: str
    audio_url: str | None = None
    seed: int | None = None
    tags: str | None = None
    lyrics: str | None = None


class AIGenerationRequest(BaseModel):
    """Request model for AI-powered music generation with automatic tag generation"""
    lyrics: str = Field(
        ...,
        description="Lyrics for the song. The AI will analyze the mood and theme to generate appropriate music tags.",
        example="[verse]\nWalking through the city lights\nFeeling free tonight\n[chorus]\nDancing in the moonlight\nEverything feels right"
    )
    duration: float = Field(
        default=60,
        ge=1,
        le=300,
        description="Duration of the audio in seconds (1-300)",
        example=60
    )


class AIGenerationResponse(BaseModel):
    """Response model for AI-powered music generation"""
    success: bool
    message: str
    audio_url: str | None = None
    generated_tags: str | None = None
    lyrics: str | None = None
    seed: int | None = None
    ai_analysis: str | None = None


class PromptToAudioRequest(BaseModel):
    """Request model for prompt to audio generation"""
    prompt: str = Field(..., description="Prompt to control the style of the generated audio.")
    instrumental: bool = Field(default=False, description="Whether to generate an instrumental version.")
    duration: float = Field(default=60, ge=1, le=300)
    number_of_steps: int = Field(default=27, ge=10, le=100)


@app.on_event("startup")
async def start_generated_music_cleanup() -> None:
    cleanup_generated_music_files()
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_generated_music_loop())


@app.on_event("shutdown")
async def stop_generated_music_cleanup() -> None:
    global cleanup_task
    if cleanup_task is None:
        return

    cleanup_task.cancel()
    with suppress(asyncio.CancelledError):
        await cleanup_task
    cleanup_task = None
    seed: int | None = Field(default=None)



@app.get("/")
async def root():
    """Serve the HTML frontend"""
    html_file = Path("index.html")
    if html_file.exists():
        return FileResponse(html_file, media_type="text/html")
    else:
        # Fallback to JSON if HTML file doesn't exist
        return {
            "message": "AceStep Music Generator API",
            "docs": "/docs",
            "endpoints": {
                "generate": "/generate - POST request to generate music",
                "health": "/health - Check API health",
                "web_ui": "/ - Web interface (index.html not found)"
            }
        }


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "message": "AceStep Music Generator API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "generate": "/generate - POST request to generate music",
            "health": "/health - Check API health",
            "web_ui": "/ - Web interface"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check if FAL_KEY is set
    fal_key = os.getenv("FAL_KEY")
    if not fal_key:
        return {
            "status": "unhealthy",
            "message": "FAL_KEY environment variable not set"
        }
    return {
        "status": "healthy",
        "message": "API is running and FAL_KEY is configured"
    }


def generate_tags_from_lyrics(lyrics: str) -> tuple[str, str]:
    """
    Use Gemini AI to analyze lyrics and generate appropriate music tags
    
    Returns:
        tuple: (tags_string, analysis_text)
    """
    if not GEMINI_API_KEY:
        # Fallback to default tags if Gemini is not configured
        return "pop, melodic, emotional", "Gemini API not configured - using default tags"
    
    try:
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Refined prompt for precise tag generation
        prompt = f"""You are an expert music producer specializing in the AceStep AI music generation model. Your task is to analyze lyrics and generate ONLY 3-7 precise, essential tags that will produce the best possible music.

LYRICS TO ANALYZE:
{lyrics}

ACETSTEP MODEL TAG SPECIFICATIONS:
The AceStep model works best with tags from these categories:

1. PRIMARY GENRE (choose 1-2):
   - pop, rock, jazz, electronic, hiphop, classical, ambient, indie, folk, country, blues, metal, reggae, soul, funk, disco, house, techno, trance, dubstep, trap, lofi, chillwave

2. MOOD/ENERGY (choose 1-2):
   - upbeat, energetic, chill, relaxing, melancholic, dreamy, dark, bright, peaceful, intense, aggressive, romantic, nostalgic, mysterious, playful, dramatic, ethereal, groovy

3. TEMPO/STYLE (choose 0-1):
   - fast, slow, medium tempo, uptempo, downtempo, atmospheric, minimalist, layered, raw, polished, acoustic, synthetic

4. INSTRUMENTATION (choose 0-2, only if essential):
   - piano, guitar, synth, strings, drums, bass, orchestral, vocal, saxophone, violin, electronic beats

CRITICAL RULES:
- Generate EXACTLY 3-7 tags total
- **NEVER use tags like 'instrumental', 'no vocals', 'karaoke' (unless lyrics are '[inst]')**
- **AVOID tags that degrade vocal clarity** (e.g., 'noisy', 'distortion', 'shoegaze') unless the lyrics explicitly demand it
- If the lyrics are standard songs, **prioritize tags that support clear vocals** (e.g., 'pop', 'vocal', 'melodic', 'clean')
- Choose only the MOST ESSENTIAL tags that capture the core essence
- Each tag must be from the approved categories above
- Tags must be comma-separated, lowercase, single words or short phrases
- Prioritize genre and mood tags over instrumentation
- Tags should work harmoniously together

ANALYSIS REQUIREMENTS:
- Identify the PRIMARY emotion/mood (1-2 sentences)
- Explain why these tags fit AND how they support the vocals (1 sentence)
- Keep analysis concise and focused

OUTPUT FORMAT (STRICT):
TAGS: [exactly 3-7 comma-separated tags]

ANALYSIS: [2-3 sentences total explaining the mood and tag choices]

EXAMPLE 1:
TAGS: lofi, melancholic, piano, vocal, chill
ANALYSIS: The lyrics express introspective sadness. 'Lofi' and 'chill' set the mood, while 'vocal' ensures the intimate lyrics remain the focus against the gentle piano backing.

EXAMPLE 2:
TAGS: pop, upbeat, energetic, synth, clear vocals
ANALYSIS: The lyrics convey joy and celebration. 'Pop' and 'synth' provide the modern energy, while 'clear vocals' ensures the fast-paced lyrics are delivered distinctively.

EXAMPLE 3:
TAGS: indie, dreamy, atmospheric, slow, melodic
ANALYSIS: The lyrics suggest a wistful quality. 'Dreamy' and 'atmospheric' create the vibe, but 'melodic' and 'indie' keep the song structured enough for the vocals to shine.

Now analyze the provided lyrics and generate ONLY 3-7 essential tags:"""


        # Generate response
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Parse the response
        tags = ""
        analysis = ""
        
        lines = response_text.split('\n')
        for i, line in enumerate(lines):
            if line.startswith('TAGS:'):
                tags = line.replace('TAGS:', '').strip()
            elif line.startswith('ANALYSIS:'):
                # Get analysis (might span multiple lines)
                analysis = line.replace('ANALYSIS:', '').strip()
                # Check if analysis continues on next lines
                for j in range(i + 1, len(lines)):
                    if lines[j].strip() and not lines[j].startswith('TAGS:'):
                        analysis += " " + lines[j].strip()
                    else:
                        break
        
        # Fallback if parsing failed
        if not tags:
            tags = "pop, melodic, emotional"
            analysis = "AI analysis completed - using generated tags"
        
        return tags, analysis
        
    except Exception as e:
        print(f"Error generating tags with Gemini: {str(e)}")
        # Fallback tags based on simple heuristics
        lyrics_lower = lyrics.lower()
        
        if any(word in lyrics_lower for word in ['dance', 'party', 'night', 'club']):
            return "electronic, dance, upbeat, energetic", "Auto-generated based on lyric keywords"
        elif any(word in lyrics_lower for word in ['sad', 'cry', 'alone', 'lost', 'broken']):
            return "melancholic, slow, piano, indie", "Auto-generated based on lyric keywords"
        elif any(word in lyrics_lower for word in ['love', 'heart', 'together', 'forever']):
            return "pop, romantic, melodic, smooth", "Auto-generated based on lyric keywords"
        elif any(word in lyrics_lower for word in ['chill', 'relax', 'calm', 'peace']):
            return "lofi, chill, ambient, relaxing", "Auto-generated based on lyric keywords"
        else:
            return "pop, melodic, contemporary", "Auto-generated default tags"



async def download_audio(url: str, output_path: Path) -> Path:
    """Download audio file from URL"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        
        with open(output_path, "wb") as f:
            f.write(response.content)
    
    return output_path


def convert_to_mp3(input_path: Path, output_path: Path) -> Path:
    """Convert audio file to MP3 format"""
    # Load audio file
    audio = AudioSegment.from_file(str(input_path))
    
    # Export as MP3
    audio.export(str(output_path), format="mp3", bitrate="192k")
    
    return output_path


async def process_fal_audio_result(result: dict, success_message: str) -> MusicGenerationResponse:
    """Helper method to process fal.ai response, download and convert the generated audio."""
    if not result or "audio" not in result:
        raise HTTPException(
            status_code=500,
            detail="Invalid response from AceStep API: No audio in response"
        )
    
    audio_info = result["audio"]
    audio_url = audio_info.get("url")
    
    if not audio_url:
        raise HTTPException(
            status_code=500,
            detail="Invalid response from AceStep API: No audio URL in response"
        )
    
    # Generate unique filename
    file_id = str(uuid.uuid4())
    
    # Download the audio file
    temp_file = OUTPUT_DIR / f"{file_id}_temp{Path(audio_url).suffix}"
    await download_audio(audio_url, temp_file)
    
    # Convert to MP3 if not already MP3
    output_file = OUTPUT_DIR / f"{file_id}.mp3"
    
    if temp_file.suffix.lower() != ".mp3":
        print(f"Converting {temp_file.suffix} to MP3...")
        convert_to_mp3(temp_file, output_file)
        # Remove temporary file
        temp_file.unlink()
    else:
        # Just rename if already MP3
        temp_file.rename(output_file)
    
    # Return response with file path
    return MusicGenerationResponse(
        success=True,
        message=success_message,
        audio_url=f"/download/{output_file.name}",
        seed=result.get("seed"),
        tags=result.get("tags", ""),
        lyrics=result.get("lyrics", "")
    )


@app.post("/generate", response_model=MusicGenerationResponse)
async def generate_music(request: MusicGenerationRequest):
    """
    Generate music using AceStep API
    
    This endpoint:
    1. Accepts user input (tags, lyrics, duration)
    2. Calls the AceStep API via fal.ai
    3. Downloads the generated audio
    4. Converts to MP3 if necessary
    5. Returns the MP3 file
    """
    
    # Check if FAL_KEY is set
    if not os.getenv("FAL_KEY"):
        raise HTTPException(
            status_code=500,
            detail="FAL_KEY environment variable not set. Please configure your fal.ai API key."
        )
    
    try:
        # Prepare arguments for fal.ai API
        arguments = {
            "tags": request.tags,
            "lyrics": request.lyrics,
            "duration": request.duration,
            "number_of_steps": request.number_of_steps,
        }
        
        # Add seed if provided
        if request.seed is not None:
            arguments["seed"] = request.seed
        
        # Call fal.ai API using the correct method
        print(f"Calling AceStep API with arguments: {arguments}")
        
        # Use fal_client.run() which is the correct method for the current API
        result = fal_client.run(
            "fal-ai/ace-step",
            arguments=arguments
        )
        
        print(f"API Response: {result}")
        
        # Extract audio URL from result
        if not result or "audio" not in result:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AceStep API: No audio in response"
            )
        
        audio_info = result["audio"]
        audio_url = audio_info.get("url")
        
        if not audio_url:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AceStep API: No audio URL in response"
            )
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        
        # Download the audio file
        temp_file = OUTPUT_DIR / f"{file_id}_temp{Path(audio_url).suffix}"
        await download_audio(audio_url, temp_file)
        
        # Convert to MP3 if not already MP3
        output_file = OUTPUT_DIR / f"{file_id}.mp3"
        
        if temp_file.suffix.lower() != ".mp3":
            print(f"Converting {temp_file.suffix} to MP3...")
            convert_to_mp3(temp_file, output_file)
            # Remove temporary file
            temp_file.unlink()
        else:
            # Just rename if already MP3
            temp_file.rename(output_file)
        
        # Return response with file path
        return MusicGenerationResponse(
            success=True,
            message="Music generated successfully",
            audio_url=f"/download/{output_file.name}",
            seed=result.get("seed"),
            tags=result.get("tags"),
            lyrics=result.get("lyrics")
        )
        
    except Exception as e:
        print(f"Error generating music: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating music: {str(e)}"
        )


@app.post("/generate-ai", response_model=AIGenerationResponse)
async def generate_music_ai(request: AIGenerationRequest):
    """
    AI-Powered Music Generation with Automatic Tag Generation
    
    This endpoint:
    1. Takes lyrics from the user
    2. Uses Gemini AI to analyze the lyrics and generate appropriate music tags
    3. Automatically sets optimal parameters for music generation
    4. Calls the AceStep API to generate music
    5. Returns the generated music file with AI analysis
    
    The AI analyzes:
    - Mood and emotional tone
    - Theme and subject matter
    - Tempo and energy level
    - Appropriate genre and style tags
    """
    
    # Check if FAL_KEY is set
    if not os.getenv("FAL_KEY"):
        raise HTTPException(
            status_code=500,
            detail="FAL_KEY environment variable not set. Please configure your fal.ai API key."
        )
    
    # Check if GEMINI_API_KEY is set (optional, will use fallback if not)
    if not GEMINI_API_KEY:
        print("Warning: GEMINI_API_KEY not set. Using fallback tag generation.")
    
    try:
        # Step 1: Generate tags from lyrics using Gemini AI
        print(f"Analyzing lyrics with AI...")
        generated_tags, ai_analysis = generate_tags_from_lyrics(request.lyrics)
        print(f"Generated tags: {generated_tags}")
        print(f"AI Analysis: {ai_analysis}")
        
        # Step 2: Prepare arguments for fal.ai API with auto-optimized parameters
        # Automatically set optimal parameters based on duration
        if request.duration <= 30:
            number_of_steps = 25  # Faster for short clips
        elif request.duration <= 60:
            number_of_steps = 27  # Standard quality
        elif request.duration <= 120:
            number_of_steps = 30  # Better quality for medium length
        else:
            number_of_steps = 35  # Best quality for longer tracks
        
        arguments = {
            "tags": generated_tags,
            "lyrics": request.lyrics,
            "duration": request.duration,
            "number_of_steps": number_of_steps,
        }
        
        # Step 3: Call fal.ai API
        print(f"Calling AceStep API with AI-generated tags and arguments: {arguments}")
        
        result = fal_client.run(
            "fal-ai/ace-step",
            arguments=arguments
        )
        
        print(f"API Response: {result}")
        
        # Extract audio URL from result
        if not result or "audio" not in result:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AceStep API: No audio in response"
            )
        
        audio_info = result["audio"]
        audio_url = audio_info.get("url")
        
        if not audio_url:
            raise HTTPException(
                status_code=500,
                detail="Invalid response from AceStep API: No audio URL in response"
            )
        
        # Step 4: Download the audio file
        file_id = str(uuid.uuid4())
        temp_file = OUTPUT_DIR / f"{file_id}_temp{Path(audio_url).suffix}"
        await download_audio(audio_url, temp_file)
        
        # Step 5: Convert to MP3 if not already MP3
        output_file = OUTPUT_DIR / f"{file_id}.mp3"
        
        if temp_file.suffix.lower() != ".mp3":
            print(f"Converting {temp_file.suffix} to MP3...")
            convert_to_mp3(temp_file, output_file)
            temp_file.unlink()
        else:
            temp_file.rename(output_file)
        
        # Return response with AI analysis
        return AIGenerationResponse(
            success=True,
            message="Music generated successfully with AI-powered tag generation",
            audio_url=f"/download/{output_file.name}",
            generated_tags=generated_tags,
            lyrics=request.lyrics,
            seed=result.get("seed"),
            ai_analysis=ai_analysis
        )
        
    except Exception as e:
        print(f"Error in AI-powered music generation: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating music: {str(e)}"
        )



@app.post("/prompt-to-audio", response_model=MusicGenerationResponse)
async def generate_music_prompt(request: PromptToAudioRequest):
    """
    Generate music from a simple prompt using AceStep
    """
    if not os.getenv("FAL_KEY"): raise HTTPException(status_code=500, detail="FAL_KEY environment variable not set.")
    try:
        arguments = { "prompt": request.prompt, "instrumental": request.instrumental, "duration": request.duration, "number_of_steps": request.number_of_steps }
        if request.seed is not None: arguments["seed"] = request.seed
        print(f"Calling fal-ai/ace-step/prompt-to-audio with: {arguments}")
        result = fal_client.run("fal-ai/ace-step/prompt-to-audio", arguments=arguments)
        return await process_fal_audio_result(result, "Prompt-to-audio generated successfully")
    except Exception as e:
        print(f"Error in prompt-to-audio generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")


@app.post("/audio-outpaint", response_model=MusicGenerationResponse)
async def generate_music_outpaint(
    audio: UploadFile = File(..., description="Audio file to be outpainted"),
    extend_before_duration: float = Form(0, description="Seconds to extend from start"),
    extend_after_duration: float = Form(30, description="Seconds to extend from end"),
    tags: str = Form("", description="Genre tags"),
    lyrics: str = Form("", description="Lyrics to be sung"),
    number_of_steps: int = Form(27),
    seed: int | None = Form(None)
):
    """
    Extend the beginning or end of provided audio with lyrics and/or style using AceStep
    """
    if not os.getenv("FAL_KEY"): raise HTTPException(status_code=500, detail="FAL_KEY environment variable not set.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename or "").suffix or ".wav") as temp_in:
        shutil.copyfileobj(audio.file, temp_in)
        temp_input_path = temp_in.name
        
    try:
        audio_url = fal_client.upload_file(temp_input_path)
        arguments = { "audio_url": audio_url, "extend_before_duration": extend_before_duration, "extend_after_duration": extend_after_duration, "tags": tags, "lyrics": lyrics, "number_of_steps": number_of_steps }
        if seed is not None: arguments["seed"] = seed
        print(f"Calling fal-ai/ace-step/audio-outpaint with: {arguments}")
        result = fal_client.run("fal-ai/ace-step/audio-outpaint", arguments=arguments)
        return await process_fal_audio_result(result, "Audio outpainted successfully")
    except Exception as e:
        print(f"Error in audio outpaint generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)


@app.post("/audio-inpaint", response_model=MusicGenerationResponse)
async def generate_music_inpaint(
    audio: UploadFile = File(..., description="Audio file to be inpainted"),
    start_time_relative_to: str = Form("start", description="start or end"),
    start_time: float = Form(0, description="Start time in seconds"),
    end_time_relative_to: str = Form("start", description="start or end"),
    end_time: float = Form(30, description="End time in seconds"),
    tags: str = Form("", description="Genre tags"),
    lyrics: str = Form("", description="Lyrics to be sung"),
    variance: float = Form(0.5, description="Variance"),
    number_of_steps: int = Form(27),
    seed: int | None = Form(None)
):
    """
    Modify a portion of provided audio with lyrics and/or style using AceStep
    """
    if not os.getenv("FAL_KEY"): raise HTTPException(status_code=500, detail="FAL_KEY environment variable not set.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename or "").suffix or ".wav") as temp_in:
        shutil.copyfileobj(audio.file, temp_in)
        temp_input_path = temp_in.name
        
    try:
        audio_url = fal_client.upload_file(temp_input_path)
        arguments = { "audio_url": audio_url, "start_time_relative_to": start_time_relative_to, "start_time": start_time, "end_time_relative_to": end_time_relative_to, "end_time": end_time, "tags": tags, "lyrics": lyrics, "variance": variance, "number_of_steps": number_of_steps }
        if seed is not None: arguments["seed"] = seed
        print(f"Calling fal-ai/ace-step/audio-inpaint with: {arguments}")
        result = fal_client.run("fal-ai/ace-step/audio-inpaint", arguments=arguments)
        return await process_fal_audio_result(result, "Audio inpainted successfully")
    except Exception as e:
        print(f"Error in audio inpaint generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)


@app.post("/audio-to-audio", response_model=MusicGenerationResponse)
async def generate_music_audio_to_audio(
    audio: UploadFile = File(..., description="Audio file to be modified"),
    edit_mode: str = Form("remix", description="lyrics or remix"),
    original_tags: str = Form("", description="Original tags of the audio file"),
    original_lyrics: str = Form("", description="Original lyrics of the audio file"),
    tags: str = Form("", description="New genre tags"),
    lyrics: str = Form("", description="New lyrics"),
    number_of_steps: int = Form(27),
    seed: int | None = Form(None)
):
    """
    Generate music from a lyrics and example audio using AceStep
    """
    if not os.getenv("FAL_KEY"): raise HTTPException(status_code=500, detail="FAL_KEY environment variable not set.")
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(audio.filename or "").suffix or ".wav") as temp_in:
        shutil.copyfileobj(audio.file, temp_in)
        temp_input_path = temp_in.name
        
    try:
        audio_url = fal_client.upload_file(temp_input_path)
        arguments = { "audio_url": audio_url, "edit_mode": edit_mode, "original_tags": original_tags, "original_lyrics": original_lyrics, "tags": tags, "lyrics": lyrics, "number_of_steps": number_of_steps }
        if seed is not None: arguments["seed"] = seed
        print(f"Calling fal-ai/ace-step/audio-to-audio with: {arguments}")
        result = fal_client.run("fal-ai/ace-step/audio-to-audio", arguments=arguments)
        return await process_fal_audio_result(result, "Audio remixed/edited successfully")
    except Exception as e:
        print(f"Error in audio-to-audio generation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating music: {str(e)}")
    finally:
        if os.path.exists(temp_input_path):
            os.remove(temp_input_path)



@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Download generated music file
    """
    file_path = OUTPUT_DIR / filename
    
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="File not found"
        )
    
    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=filename,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
