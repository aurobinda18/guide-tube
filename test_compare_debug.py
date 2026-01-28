#!/usr/bin/env python
"""
Debug script to test comparison feature
Run: python manage.py shell < test_compare_debug.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guide_tube.settings')
django.setup()

from django.conf import settings
from googleapiclient.discovery import build
from analyzer.views_comparison import extract_video_id

def test_api_key():
    """Test if API key is configured"""
    print("\n" + "="*60)
    print("1. Testing API Key Configuration")
    print("="*60)
    api_key = settings.YOUTUBE_API_KEY
    if api_key:
        print(f"✅ API Key found: {api_key[:20]}...{api_key[-10:]}")
    else:
        print("❌ API Key NOT configured!")
        return False
    return True

def test_url_parsing():
    """Test URL parsing"""
    print("\n" + "="*60)
    print("2. Testing URL Parsing")
    print("="*60)
    
    test_urls = [
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
        'https://youtu.be/dQw4w9WgXcQ',
        'https://www.youtube.com/watch?v=rfscVS0vtbw',
        'https://www.youtube.com/shorts/dQw4w9WgXcQ',
    ]
    
    all_passed = True
    for url in test_urls:
        vid = extract_video_id(url)
        status = "✅" if vid else "❌"
        print(f"{status} {url[:50]:<50} → {vid}")
        if not vid:
            all_passed = False
    
    return all_passed

def test_youtube_api():
    """Test actual YouTube API call"""
    print("\n" + "="*60)
    print("3. Testing YouTube API Connection")
    print("="*60)
    
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        print("❌ No API key to test")
        return False
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Test with Rick Roll (very popular, always available)
        video_id = 'dQw4w9WgXcQ'
        print(f"\nTesting with video ID: {video_id}")
        
        request = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        
        print(f"🔄 Calling API...")
        response = request.execute()
        
        print(f"✅ API Response received!")
        print(f"   Items count: {len(response.get('items', []))}")
        
        if response.get('items'):
            video = response['items'][0]
            print(f"   Title: {video['snippet']['title']}")
            print(f"   Channel: {video['snippet']['channelTitle']}")
            print(f"✅ API Works Correctly!")
            return True
        else:
            print(f"❌ No items in response!")
            return False
            
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

def test_multiple_videos():
    """Test with multiple video IDs"""
    print("\n" + "="*60)
    print("4. Testing Multiple Videos")
    print("="*60)
    
    api_key = settings.YOUTUBE_API_KEY
    if not api_key:
        print("❌ No API key to test")
        return False
    
    test_videos = [
        ('dQw4w9WgXcQ', 'Rick Roll'),
        ('rfscVS0vtbw', 'Popular Python tutorial'),
        ('jNQXAC9IVRw', 'Me at the zoo'),
    ]
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        for vid, description in test_videos:
            print(f"\n📌 Testing: {description} ({vid})")
            request = youtube.videos().list(
                part="snippet",
                id=vid
            )
            response = request.execute()
            
            if response.get('items'):
                video = response['items'][0]
                print(f"   ✅ Found: {video['snippet']['title'][:50]}")
            else:
                print(f"   ❌ Not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPARISON FEATURE DEBUG TEST")
    print("="*60)
    
    results = {
        'API Key': test_api_key(),
        'URL Parsing': test_url_parsing(),
        'YouTube API': test_youtube_api(),
        'Multiple Videos': test_multiple_videos(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All tests passed! Comparison should work.")
    else:
        print("⚠️  Some tests failed. Check errors above.")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()
