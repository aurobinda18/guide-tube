#!/usr/bin/env python
"""
Test script to verify video URL parsing and API functionality
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'guide_tube.settings')
django.setup()

from analyzer.views import extract_video_id
from analyzer.views_comparison import extract_video_id as extract_video_id_comparison
from django.conf import settings
from googleapiclient.discovery import build

def test_url_parsing():
    """Test URL parsing with various formats"""
    print("=" * 60)
    print("Testing URL Parsing")
    print("=" * 60)
    
    test_urls = [
        ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/shorts/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://m.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
        ('https://www.youtube.com/watch?v=dQw4w9WgXcQ&feature=share', 'dQw4w9WgXcQ'),
        ('https://invalid-website.com/video', None),
        ('', None),
        ('http://example.com', None),
    ]
    
    all_passed = True
    
    for url, expected in test_urls:
        result_main = extract_video_id(url)
        result_comparison = extract_video_id_comparison(url)
        
        status_main = "✅" if result_main == expected else "❌"
        status_comparison = "✅" if result_comparison == expected else "❌"
        
        print(f"\nURL: {url[:50]:<50}")
        print(f"  Expected:    {expected}")
        print(f"  Main view:   {result_main} {status_main}")
        print(f"  Comparison:  {result_comparison} {status_comparison}")
        
        if result_main != expected or result_comparison != expected:
            all_passed = False
    
    return all_passed

def test_api_keys():
    """Test if API keys are properly loaded"""
    print("\n" + "=" * 60)
    print("Testing API Keys")
    print("=" * 60)
    
    youtube_key = settings.YOUTUBE_API_KEY
    groq_key = settings.GROQ_API_KEY
    
    print(f"\nYouTube API Key: {'✅ SET (' + youtube_key[:20] + '...)' if youtube_key else '❌ NOT SET'}")
    print(f"GROQ API Key:    {'✅ SET (' + groq_key[:20] + '...)' if groq_key else '❌ NOT SET'}")
    
    return bool(youtube_key and groq_key)

def test_youtube_api():
    """Test if YouTube API actually works"""
    print("\n" + "=" * 60)
    print("Testing YouTube API Connection")
    print("=" * 60)
    
    try:
        youtube = build('youtube', 'v3', developerKey=settings.YOUTUBE_API_KEY)
        request = youtube.videos().list(
            part="snippet,contentDetails",
            id="dQw4w9WgXcQ"
        )
        response = request.execute()
        
        if response.get('items'):
            video = response['items'][0]
            title = video['snippet']['title']
            channel = video['snippet']['channelTitle']
            duration = video['contentDetails']['duration']
            
            print(f"\n✅ API Connection Successful!")
            print(f"   Test Video: {title}")
            print(f"   Channel: {channel}")
            print(f"   Duration: {duration}")
            return True
        else:
            print("\n❌ API returned no items")
            return False
            
    except Exception as e:
        print(f"\n❌ API Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("VIDEO URL & API DIAGNOSTICS")
    print("=" * 60)
    
    results = {
        'URL Parsing': test_url_parsing(),
        'API Keys': test_api_keys(),
        'YouTube API': test_youtube_api()
    }
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name:<20} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Please review the errors above")
    print("=" * 60 + "\n")
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
