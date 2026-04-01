"""
Retry test for POST /audio-to-audio using the smallest available MP3
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"
GEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_music")

# Pick the smallest MP3 to minimise processing time
mp3_files = []
for f in os.listdir(GEN_DIR):
    if f.endswith(".mp3"):
        path = os.path.join(GEN_DIR, f)
        mp3_files.append((os.path.getsize(path), f, path))

mp3_files.sort()  # smallest first
if not mp3_files:
    print("No MP3 files found.")
    exit(1)

size, name, path = mp3_files[0]
print(f"Using smallest file: {name}  ({size} bytes)")

print("\n[TEST] POST /audio-to-audio")
with open(path, "rb") as f:
    files = {"audio": (name, f, "audio/mpeg")}
    data = {
        "edit_mode": "remix",
        "original_tags": "lofi, chill",
        "original_lyrics": "[inst]",
        "tags": "jazz, smooth",
        "lyrics": "[inst]",
        "number_of_steps": "10"
    }
    r = requests.post(f"{BASE_URL}/audio-to-audio", files=files, data=data, timeout=360)

print(f"Status: {r.status_code}")
try:
    d = r.json()
    print(json.dumps(d, indent=2))
    if r.status_code == 200 and d.get("success"):
        print("\n[PASS] POST /audio-to-audio")
        # Save result for report
        with open("audio_to_audio_result.json", "w") as jf:
            json.dump(d, jf, indent=2)
    else:
        print("\n[FAIL] POST /audio-to-audio")
except Exception as e:
    print(f"Raw: {r.text}")
    print(f"[FAIL] Exception: {e}")
