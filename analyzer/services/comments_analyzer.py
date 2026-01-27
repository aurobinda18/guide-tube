from googleapiclient.discovery import build
import re
from collections import Counter

class CommentsAnalyzer:
    def __init__(self, api_key):
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Keywords that indicate understanding
        self.understanding_keywords = [
            'thanks', 'thank you', 'helpful', 'understood', 'clear',
            'explained well', 'good explanation', 'easy to understand',
            'samajh aa gaya', 'achha hai', 'bahut badhiya', 'shukriya'
        ]
        
        # Keywords that indicate confusion
        self.confusion_keywords = [
            'confusing', 'not clear', 'difficult', 'hard to understand',
            'did not understand', 'can you explain', 'samajh nahi aaya',
            'mujhe samajh nahi aaya', 'confuse', 'complicated'
        ]
    
    def analyze_video_comments(self, video_id, max_comments=100):
        """Analyze comments for sentiment and understanding"""
        try:
            # Fetch comments
            comments = []
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_comments,
                textFormat="plainText"
            )
            
            response = request.execute()
            
            for item in response.get('items', []):
                comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                comments.append(comment.lower())
            
            if not comments:
                return {
                    'total_comments': 0,
                    'understanding_score': 0,
                    'confusion_score': 0,
                    'sentiment': 'No comments'
                }
            
            # Analyze comments
            understanding_count = 0
            confusion_count = 0
            
            for comment in comments:
                # Check for understanding keywords
                for keyword in self.understanding_keywords:
                    if keyword in comment:
                        understanding_count += 1
                        break
                
                # Check for confusion keywords  
                for keyword in self.confusion_keywords:
                    if keyword in comment:
                        confusion_count += 1
                        break
            
            total_analyzed = len(comments)
            understanding_score = (understanding_count / total_analyzed) * 100
            confusion_score = (confusion_count / total_analyzed) * 100
            
            # Determine overall sentiment
            if understanding_score > confusion_score:
                sentiment = "Positive"
            elif confusion_score > understanding_score:
                sentiment = "Confusing"
            else:
                sentiment = "Mixed"
            
            return {
                'total_comments': total_analyzed,
                'understanding_score': round(understanding_score, 1),
                'confusion_score': round(confusion_score, 1),
                'sentiment': sentiment,
                'sample_comments': comments[:3]  # First 3 comments
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_comments': 0,
                'understanding_score': 0,
                'confusion_score': 0,
                'sentiment': 'Error'
            }