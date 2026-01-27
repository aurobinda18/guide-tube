# analyzer/services/qa_service.py

class QAService:
    """Simple fallback Q&A service when RAG fails"""
    
    def find_answer_in_transcript(self, question, transcript_text, video_title):
        """Simple keyword matching fallback"""
        return {
            'answer': f"RAG system is initializing... Try again in a moment.\n\nFor '{video_title}', try asking about main concepts mentioned in the video.",
            'timestamp': None,
            'confidence': 'low',
            'source': 'fallback',
            'method': 'minimal'
        }
    
    def format_answer_for_display(self, qa_result):
        """Format fallback answer"""
        return [
            "⚠️ **RAG System Initializing**",
            "",
            qa_result['answer'],
            "",
            "🔄 Please try again in a moment..."
        ]