"""
Simple test client for the AceStep Music Generator API
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"


def test_health():
    """Test the health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")
    return response.json()


def test_generate_instrumental():
    """Test generating instrumental music"""
    print("Generating instrumental music...")
    
    payload = {
        "tags": "lofi, hiphop, chill, relaxing",
        "lyrics": "[inst]",
        "duration": 30,
        "number_of_steps": 27
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json=payload,
        timeout=300  # 5 minutes timeout
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    
    return result


def test_generate_with_lyrics():
    """Test generating music with lyrics"""
    print("Generating music with lyrics...")
    
    payload = {
        "tags": "pop, upbeat, energetic",
        "lyrics": """[verse]
Walking down the street
Feeling the beat

[chorus]
Music in the air tonight
Everything feels so right""",
        "duration": 45,
        "number_of_steps": 27,
        "seed": 42
    }
    
    print(f"Request: {json.dumps(payload, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/generate",
        json=payload,
        timeout=300
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(f"Response: {json.dumps(result, indent=2)}\n")
    
    return result


def download_music(audio_url, filename="test_music.mp3"):
    """Download the generated music file"""
    print(f"Downloading music from {audio_url}...")
    
    response = requests.get(f"{BASE_URL}{audio_url}")
    
    if response.status_code == 200:
        with open(filename, "wb") as f:
            f.write(response.content)
        print(f"Music saved to {filename}\n")
        return True
    else:
        print(f"Failed to download: {response.status_code}\n")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("AceStep Music Generator API - Test Client")
    print("=" * 60 + "\n")
    
    try:
        # Test health
        health = test_health()
        
        if health.get("status") != "healthy":
            print("⚠️  API is not healthy. Please check your FAL_KEY configuration.")
            return
        
        # Test instrumental generation
        print("-" * 60)
        result1 = test_generate_instrumental()
        
        if result1.get("success"):
            print("✅ Instrumental generation successful!")
            download_music(result1["audio_url"], "instrumental_test.mp3")
        else:
            print("❌ Instrumental generation failed!")
        
        # Test generation with lyrics
        print("-" * 60)
        result2 = test_generate_with_lyrics()
        
        if result2.get("success"):
            print("✅ Lyrics generation successful!")
            download_music(result2["audio_url"], "lyrics_test.mp3")
        else:
            print("❌ Lyrics generation failed!")
        
        print("-" * 60)
        print("\n🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running.")
        print("   Run: python main.py")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
