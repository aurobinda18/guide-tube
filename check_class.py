from youtube_transcript_api import YouTubeTranscriptApi

# Check class methods
print("YouTubeTranscriptApi methods:")
api_class = YouTubeTranscriptApi
methods = [method for method in dir(api_class) if not method.startswith('_')]
print(methods)

# Try to create instance and check
print("\nTrying to create instance...")
try:
    api = YouTubeTranscriptApi()
    print("Instance created")
    print("Instance methods:", [method for method in dir(api) if not method.startswith('_')])
except Exception as e:
    print(f"Error creating instance: {e}")