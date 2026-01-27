# Let's see what the actual transcript contains
from youtube_transcript_api import YouTubeTranscriptApi

video_id = "bL92ALSZ2Cg"  # The CampusX LangChain video

try:
    api = YouTubeTranscriptApi()
    transcript_list = api.list(video_id)
    
    # Try English first, then Hindi
    try:
        transcript_obj = transcript_list.find_transcript(['en'])
    except:
        transcript_obj = transcript_list.find_transcript(['hi'])
    
    transcript_data = list(transcript_obj.fetch())
    transcript_text = ' '.join([snippet.text for snippet in transcript_data])
    
    print(f"Transcript length: {len(transcript_text)} characters")
    print(f"First 500 characters:\n{transcript_text[:500]}\n")
    
    # Check for our keywords
    keywords = ['langchain', 'document', 'loader', 'vector', 'rag', 'llm', 'lang chain']
    print("Keyword search:")
    for keyword in keywords:
        if keyword in transcript_text.lower():
            print(f"✅ Found '{keyword}'")
        else:
            print(f"❌ NOT found '{keyword}'")
            
except Exception as e:
    print(f"Error: {e}")