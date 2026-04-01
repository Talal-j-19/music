"""
Basic endpoint tests for AceStep Music Generator API
Tests: /, /api, /health, /download (404 check)
"""
import requests
import json
import os

BASE_URL = "http://localhost:8000"

results = {}

def check(name, status, passed, note=""):
    marker = "PASS" if passed else "FAIL"
    results[name] = {"status": status, "passed": passed, "note": note}
    print(f"  [{marker}] {name} | HTTP {status} | {note}")

print("=" * 60)
print("AceStep Music Generator API - Full Endpoint Test Suite")
print("=" * 60)

# 1. GET /health
print("\n--- GET /health ---")
try:
    r = requests.get(f"{BASE_URL}/health", timeout=10)
    data = r.json()
    passed = r.status_code == 200 and data.get("status") == "healthy"
    check("GET /health", r.status_code, passed, data.get("message", ""))
except Exception as e:
    check("GET /health", "ERR", False, str(e))

# 2. GET /
print("\n--- GET / ---")
try:
    r = requests.get(f"{BASE_URL}/", timeout=10)
    ct = r.headers.get("content-type", "")
    passed = r.status_code == 200
    check("GET /", r.status_code, passed, f"content-type: {ct}")
except Exception as e:
    check("GET /", "ERR", False, str(e))

# 3. GET /api
print("\n--- GET /api ---")
try:
    r = requests.get(f"{BASE_URL}/api", timeout=10)
    data = r.json()
    passed = r.status_code == 200 and "version" in data
    check("GET /api", r.status_code, passed, f"version: {data.get('version','')}")
except Exception as e:
    check("GET /api", "ERR", False, str(e))

# 4. GET /download/nonexistent.mp3  -> expect 404
print("\n--- GET /download/<missing> ---")
try:
    r = requests.get(f"{BASE_URL}/download/missing_file.mp3", timeout=10)
    passed = r.status_code == 404
    check("GET /download/missing", r.status_code, passed, "should return 404")
except Exception as e:
    check("GET /download/missing", "ERR", False, str(e))

# 5. GET /download/<existing mp3>
print("\n--- GET /download/<existing mp3> ---")
sample_audio = None
gen_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_music")
if os.path.isdir(gen_dir):
    for f in sorted(os.listdir(gen_dir)):
        if f.endswith(".mp3"):
            sample_audio = f
            break
if sample_audio:
    try:
        r = requests.get(f"{BASE_URL}/download/{sample_audio}", timeout=15)
        passed = r.status_code == 200 and "audio" in r.headers.get("content-type", "")
        check("GET /download/<mp3>", r.status_code, passed, f"file={sample_audio}, size={len(r.content)} bytes")
    except Exception as e:
        check("GET /download/<mp3>", "ERR", False, str(e))
else:
    check("GET /download/<mp3>", "SKIP", True, "No MP3 files in generated_music/")

print("\n=" * 60)
print("BASIC TESTS SUMMARY")
print("=" * 60)
passed_count = sum(1 for v in results.values() if v["passed"])
print(f"Passed: {passed_count}/{len(results)}")
for name, info in results.items():
    m = "PASS" if info["passed"] else "FAIL"
    print(f"  [{m}] {name}")
