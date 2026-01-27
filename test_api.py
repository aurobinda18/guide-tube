import os
from googleapiclient.discovery import build

# Read key directly from .env
with open('.env', 'r') as f:
    for line in f:
        if 'YOUTUBE_API_KEY' in line:
            API_KEY = line.split('=')[1].strip()
            break

print(f"Using API key: {API_KEY[:10]}...")

# Test YouTube API
try:
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    
    # Test with a popular coding tutorial video
    request = youtube.videos().list(
        part="snippet",
        id="rfscVS0vtbw"  # Popular Python tutorial
    )
    response = request.execute()
    
    if response['items']:
        video = response['items'][0]
        print(f"\n✅ API Works!")
        print(f"Title: {video['snippet']['title']}")
        print(f"Channel: {video['snippet']['channelTitle']}")
    else:
        print("❌ No video found")
        
except Exception as e:
    print(f"❌ Error: {e}")