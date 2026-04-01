import requests
import json
import os

BASE_URL = "http://localhost:8000"

def test_generate_ai():
    print("Testing POST /generate-ai ...")
    payload = {
        "lyrics": "[verse]\nIn the neon light of the data stream,\nWe find ourselves in a digital dream.\n[chorus]\nBit by bit, we build the code,\nIn this virtual abode.",
        "duration": 30
    }
    print(f"Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(f"{BASE_URL}/generate-ai", json=payload, timeout=300)
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}")
        if data.get("success"):
            print("✅ /generate-ai PASSED")
            return True
    except Exception as e:
        print(f"Error: {e}")
    print("❌ /generate-ai FAILED")
    return False

if __name__ == "__main__":
    test_generate_ai()
