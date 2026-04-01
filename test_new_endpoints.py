"""
Test client for the new AceStep Music Generator API endpoints:
  POST /prompt-to-audio
  POST /audio-outpaint
  POST /audio-inpaint
  POST /audio-to-audio
Requires the server to be running: python main.py
"""
import requests
import json
import os
import sys

BASE_URL = "http://localhost:8000"

# Pick any existing MP3 as the sample audio input
SAMPLE_AUDIO_DIR = os.path.join(os.path.dirname(__file__), "generated_music")
sample_audio_path = None
for f in os.listdir(SAMPLE_AUDIO_DIR):
    if f.endswith(".mp3"):
        sample_audio_path = os.path.join(SAMPLE_AUDIO_DIR, f)
        break

def sep():
    print("-" * 60)


def test_health():
    print("Testing /health ...")
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    data = r.json()
    print(f"Status: {r.status_code}  Response: {json.dumps(data, indent=2)}\n")
    return data


def test_prompt_to_audio():
    sep()
    print("Testing POST /prompt-to-audio ...")
    payload = {
        "prompt": "A calm lofi hiphop instrumental track with gentle piano",
        "instrumental": True,
        "duration": 15,
        "number_of_steps": 15
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")
    r = requests.post(f"{BASE_URL}/prompt-to-audio", json=payload, timeout=300)
    print(f"Status: {r.status_code}")
    try:
        data = r.json()
        print(f"Response: {json.dumps(data, indent=2)}")
    except Exception:
        print(f"Raw response: {r.text}")
        return None
    if r.status_code == 200 and data.get("success"):
        print("✅ /prompt-to-audio PASSED")
    else:
        print("❌ /prompt-to-audio FAILED")
    return data


def test_audio_outpaint(audio_path):
    sep()
    print("Testing POST /audio-outpaint ...")
    if not audio_path:
        print("❌ No sample audio available, skipping.")
        return None
    with open(audio_path, "rb") as f:
        files = {"audio": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {
            "extend_before_duration": 0,
            "extend_after_duration": 10,
            "tags": "lofi, chill",
            "lyrics": "[inst]",
            "number_of_steps": 15
        }
        print(f"Form data: {data}  File: {audio_path}")
        r = requests.post(f"{BASE_URL}/audio-outpaint", files=files, data=data, timeout=300)
    print(f"Status: {r.status_code}")
    try:
        resp = r.json()
        print(f"Response: {json.dumps(resp, indent=2)}")
    except Exception:
        print(f"Raw response: {r.text}")
        return None
    if r.status_code == 200 and resp.get("success"):
        print("✅ /audio-outpaint PASSED")
    else:
        print("❌ /audio-outpaint FAILED")
    return resp


def test_audio_inpaint(audio_path):
    sep()
    print("Testing POST /audio-inpaint ...")
    if not audio_path:
        print("❌ No sample audio available, skipping.")
        return None
    with open(audio_path, "rb") as f:
        files = {"audio": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {
            "start_time_relative_to": "start",
            "start_time": 0,
            "end_time_relative_to": "start",
            "end_time": 10,
            "tags": "lofi, chill",
            "lyrics": "[inst]",
            "variance": 0.5,
            "number_of_steps": 15
        }
        print(f"Form data: {data}  File: {audio_path}")
        r = requests.post(f"{BASE_URL}/audio-inpaint", files=files, data=data, timeout=300)
    print(f"Status: {r.status_code}")
    try:
        resp = r.json()
        print(f"Response: {json.dumps(resp, indent=2)}")
    except Exception:
        print(f"Raw response: {r.text}")
        return None
    if r.status_code == 200 and resp.get("success"):
        print("✅ /audio-inpaint PASSED")
    else:
        print("❌ /audio-inpaint FAILED")
    return resp


def test_audio_to_audio(audio_path):
    sep()
    print("Testing POST /audio-to-audio ...")
    if not audio_path:
        print("❌ No sample audio available, skipping.")
        return None
    with open(audio_path, "rb") as f:
        files = {"audio": (os.path.basename(audio_path), f, "audio/mpeg")}
        data = {
            "edit_mode": "remix",
            "original_tags": "lofi, chill",
            "original_lyrics": "[inst]",
            "tags": "jazz, smooth",
            "lyrics": "[inst]",
            "number_of_steps": 15
        }
        print(f"Form data: {data}  File: {audio_path}")
        r = requests.post(f"{BASE_URL}/audio-to-audio", files=files, data=data, timeout=300)
    print(f"Status: {r.status_code}")
    try:
        resp = r.json()
        print(f"Response: {json.dumps(resp, indent=2)}")
    except Exception:
        print(f"Raw response: {r.text}")
        return None
    if r.status_code == 200 and resp.get("success"):
        print("✅ /audio-to-audio PASSED")
    else:
        print("❌ /audio-to-audio FAILED")
    return resp


def main():
    print("=" * 60)
    print("AceStep Music Generator API - New Endpoint Tests")
    print("=" * 60 + "\n")

    if sample_audio_path:
        print(f"Sample audio: {sample_audio_path}")
    else:
        print("⚠️  No existing MP3 found in generated_music/ - audio-based tests will be skipped.")

    try:
        health = test_health()
        if health.get("status") != "healthy":
            print("⚠️  API is not healthy. Is FAL_KEY set? Is the server running?")
            sys.exit(1)

        test_prompt_to_audio()
        test_audio_outpaint(sample_audio_path)
        test_audio_inpaint(sample_audio_path)
        test_audio_to_audio(sample_audio_path)

        sep()
        print("\n🎉 All new endpoint tests completed!")

    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API.")
        print("   Start the server first with:  .\\venv\\Scripts\\python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
