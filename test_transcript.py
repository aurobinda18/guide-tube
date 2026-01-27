from youtube_transcript_api import YouTubeTranscriptApi

# Test with a video that DEFINITELY has transcripts
test_videos = [
    "rfscVS0vtbw",  # Python tutorial (English)
    "dQw4w9WgXcQ",  # Random popular video
]

for video_id in test_videos:
    print(f"\nTesting video: {video_id}")
    try:
        api = YouTubeTranscriptApi()
        transcript_list = api.list(video_id)
        print(f"✅ Transcript list found")
        
        # Try to get English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
            print(f"✅ English transcript available")
            data = list(transcript.fetch())
            print(f"✅ Fetched {len(data)} segments")
        except Exception as e:
            print(f"❌ English transcript error: {e}")
            
    except Exception as e:
        print(f"❌ Overall error: {e}")