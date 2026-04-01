"""
Full API Test Suite for AceStep Music Generator
Tests all endpoints and writes structured results.
"""
import requests
import json
import os
import sys
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"
GEN_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_music")

results = []

def sep(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def log(name, status_code, passed, note="", response_data=None):
    marker = "PASS" if passed else "FAIL"
    results.append({
        "endpoint": name,
        "status_code": status_code,
        "passed": passed,
        "note": note,
        "response_summary": response_data
    })
    print(f"  [{marker}] {name} | HTTP {status_code} | {note}")


# ─────────────────────────────────────────────
#  INFO / UTILITY ENDPOINTS
# ─────────────────────────────────────────────
sep("GROUP 1: Info & Utility Endpoints")

# GET /health
print("\n[1] GET /health")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    d = r.json()
    ok = r.status_code == 200 and d.get("status") == "healthy"
    log("GET /health", r.status_code, ok, d.get("message", ""))
except Exception as e:
    log("GET /health", "ERR", False, str(e))

# GET /
print("\n[2] GET /")
try:
    r = requests.get(f"{BASE_URL}/", timeout=10)
    ct = r.headers.get("content-type", "")
    ok = r.status_code == 200
    log("GET /", r.status_code, ok, f"content-type={ct}")
except Exception as e:
    log("GET /", "ERR", False, str(e))

# GET /api
print("\n[3] GET /api")
try:
    r = requests.get(f"{BASE_URL}/api", timeout=10)
    d = r.json()
    ok = r.status_code == 200 and "version" in d
    log("GET /api", r.status_code, ok, f"version={d.get('version','?')}")
except Exception as e:
    log("GET /api", "ERR", False, str(e))

# GET /download/<missing>  → 404
print("\n[4] GET /download/<nonexistent> (expect 404)")
try:
    r = requests.get(f"{BASE_URL}/download/does_not_exist.mp3", timeout=10)
    ok = r.status_code == 404
    log("GET /download/<missing>", r.status_code, ok, "404 check")
except Exception as e:
    log("GET /download/<missing>", "ERR", False, str(e))

# GET /download/<existing>  → 200 + audio
print("\n[5] GET /download/<existing mp3>")
sample_mp3 = None
if os.path.isdir(GEN_DIR):
    for f in sorted(os.listdir(GEN_DIR)):
        if f.endswith(".mp3"):
            sample_mp3 = f
            break
if sample_mp3:
    try:
        r = requests.get(f"{BASE_URL}/download/{sample_mp3}", timeout=15)
        ok = r.status_code == 200 and "audio" in r.headers.get("content-type", "")
        log("GET /download/<mp3>", r.status_code, ok,
            f"file={sample_mp3}, bytes={len(r.content)}")
    except Exception as e:
        log("GET /download/<mp3>", "ERR", False, str(e))
else:
    log("GET /download/<mp3>", "SKIP", True, "No MP3 in generated_music/")


# ─────────────────────────────────────────────
#  MUSIC GENERATION ENDPOINTS
# ─────────────────────────────────────────────
sep("GROUP 2: Music Generation Endpoints")

# POST /generate  (instrumental)
print("\n[6] POST /generate (instrumental, 15s)")
try:
    payload = {
        "tags": "lofi, chill, piano",
        "lyrics": "[inst]",
        "duration": 15,
        "number_of_steps": 10,
        "seed": 1234
    }
    print(f"     payload: {json.dumps(payload)}")
    r = requests.post(f"{BASE_URL}/generate", json=payload, timeout=300)
    d = r.json()
    ok = r.status_code == 200 and d.get("success") is True
    note = d.get("audio_url", d.get("detail", ""))
    log("POST /generate (instrumental)", r.status_code, ok, note, d)
except Exception as e:
    log("POST /generate (instrumental)", "ERR", False, str(e))

# POST /generate  (with lyrics)
print("\n[7] POST /generate (with lyrics, 15s)")
try:
    payload = {
        "tags": "pop, upbeat",
        "lyrics": "[verse]\nWalking through the city lights\n[chorus]\nFeeling alive tonight",
        "duration": 15,
        "number_of_steps": 10,
        "seed": 5678
    }
    print(f"     payload: {json.dumps(payload)}")
    r = requests.post(f"{BASE_URL}/generate", json=payload, timeout=300)
    d = r.json()
    ok = r.status_code == 200 and d.get("success") is True
    note = d.get("audio_url", d.get("detail", ""))
    log("POST /generate (lyrics)", r.status_code, ok, note, d)
except Exception as e:
    log("POST /generate (lyrics)", "ERR", False, str(e))

# POST /generate-ai
print("\n[8] POST /generate-ai (15s)")
try:
    payload = {
        "lyrics": "[verse]\nNeon dreams in the rain\nRunning through the dark\n[chorus]\nChasing light again",
        "duration": 15
    }
    print(f"     payload: {json.dumps(payload)}")
    r = requests.post(f"{BASE_URL}/generate-ai", json=payload, timeout=300)
    d = r.json()
    ok = r.status_code == 200 and d.get("success") is True
    note = f"tags={d.get('generated_tags','?')} | url={d.get('audio_url','?')}"
    log("POST /generate-ai", r.status_code, ok, note, d)
except Exception as e:
    log("POST /generate-ai", "ERR", False, str(e))

# POST /prompt-to-audio
print("\n[9] POST /prompt-to-audio (15s)")
try:
    payload = {
        "prompt": "Calm lofi hiphop instrumental with gentle piano",
        "instrumental": True,
        "duration": 15,
        "number_of_steps": 10
    }
    print(f"     payload: {json.dumps(payload)}")
    r = requests.post(f"{BASE_URL}/prompt-to-audio", json=payload, timeout=300)
    d = r.json()
    ok = r.status_code == 200 and d.get("success") is True
    note = d.get("audio_url", d.get("detail", ""))
    log("POST /prompt-to-audio", r.status_code, ok, note, d)
except Exception as e:
    log("POST /prompt-to-audio", "ERR", False, str(e))


# ─────────────────────────────────────────────
#  AUDIO-BASED ENDPOINTS (require sample file)
# ─────────────────────────────────────────────
sep("GROUP 3: Audio Upload Endpoints")

if not sample_mp3:
    print("  ⚠ No MP3 found in generated_music/ — skipping audio-upload tests")
    for ep in ["/audio-outpaint", "/audio-inpaint", "/audio-to-audio"]:
        log(f"POST {ep}", "SKIP", True, "No sample audio available")
else:
    audio_file = os.path.join(GEN_DIR, sample_mp3)

    # POST /audio-outpaint
    print(f"\n[10] POST /audio-outpaint (file={sample_mp3})")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": (sample_mp3, f, "audio/mpeg")}
            data = {
                "extend_before_duration": "0",
                "extend_after_duration": "10",
                "tags": "lofi, chill",
                "lyrics": "[inst]",
                "number_of_steps": "10"
            }
            r = requests.post(f"{BASE_URL}/audio-outpaint", files=files, data=data, timeout=300)
        d = r.json()
        ok = r.status_code == 200 and d.get("success") is True
        log("POST /audio-outpaint", r.status_code, ok, d.get("audio_url", d.get("detail", "")), d)
    except Exception as e:
        log("POST /audio-outpaint", "ERR", False, str(e))

    # POST /audio-inpaint
    print(f"\n[11] POST /audio-inpaint (file={sample_mp3})")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": (sample_mp3, f, "audio/mpeg")}
            data = {
                "start_time_relative_to": "start",
                "start_time": "0",
                "end_time_relative_to": "start",
                "end_time": "10",
                "tags": "lofi, chill",
                "lyrics": "[inst]",
                "variance": "0.5",
                "number_of_steps": "10"
            }
            r = requests.post(f"{BASE_URL}/audio-inpaint", files=files, data=data, timeout=300)
        d = r.json()
        ok = r.status_code == 200 and d.get("success") is True
        log("POST /audio-inpaint", r.status_code, ok, d.get("audio_url", d.get("detail", "")), d)
    except Exception as e:
        log("POST /audio-inpaint", "ERR", False, str(e))

    # POST /audio-to-audio
    print(f"\n[12] POST /audio-to-audio (file={sample_mp3})")
    try:
        with open(audio_file, "rb") as f:
            files = {"audio": (sample_mp3, f, "audio/mpeg")}
            data = {
                "edit_mode": "remix",
                "original_tags": "lofi, chill",
                "original_lyrics": "[inst]",
                "tags": "jazz, smooth",
                "lyrics": "[inst]",
                "number_of_steps": "10"
            }
            r = requests.post(f"{BASE_URL}/audio-to-audio", files=files, data=data, timeout=300)
        d = r.json()
        ok = r.status_code == 200 and d.get("success") is True
        log("POST /audio-to-audio", r.status_code, ok, d.get("audio_url", d.get("detail", "")), d)
    except Exception as e:
        log("POST /audio-to-audio", "ERR", False, str(e))


# ─────────────────────────────────────────────
#  SUMMARY
# ─────────────────────────────────────────────
sep("FINAL SUMMARY")
total  = len(results)
passed = sum(1 for r in results if r["passed"])
failed = total - passed
print(f"\n  Passed : {passed}/{total}")
print(f"  Failed : {failed}/{total}")
print()
for r in results:
    m = "PASS" if r["passed"] else "FAIL"
    print(f"  [{m}]  {r['endpoint']}  (HTTP {r['status_code']})")
    if r["note"]:
        print(f"         {r['note']}")

# Write machine-readable JSON for the report script
with open("test_run_output.json", "w") as jf:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "results": results,
        "summary": {"total": total, "passed": passed, "failed": failed}
    }, jf, indent=2)
print("\n  Raw results saved to test_run_output.json")
