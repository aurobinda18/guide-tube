import nltk
import textstat
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import re

class TranscriptAnalyzer:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.technical_terms = self.load_technical_terms()
    
    def load_technical_terms(self):
        # Basic programming terms - we can expand this later
        terms = [
            # Programming basics
            'algorithm', 'variable', 'function', 'class', 'object', 
            'loop', 'array', 'database', 'api', 'framework',
            'syntax', 'compiler', 'interpreter', 'debugging',
            
            # Python specific
            'python', 'django', 'flask', 'list', 'dictionary',
            'tuple', 'module', 'package', 'import', 'def', 'class',
            
            # Common technical terms
            'recursion', 'iteration', 'inheritance', 'polymorphism',
            'abstraction', 'encapsulation', 'algorithm', 'complexity'
        ]
        return set(terms)
    
    def detect_language(self, text):
        """Simple language detection"""
        # Check for common Hindi words/characters
        hindi_chars = ['़', 'ऽ', 'ा', 'ि', 'ी', 'ु', 'ू', 'े', 'ै', 'ो', 'ौ', 'ं', 'ः', 'ँ']
        english_chars = sum(1 for char in text if 'a' <= char.lower() <= 'z')
        
        hindi_count = sum(1 for char in text if char in hindi_chars)
        total_chars = len(text)
        
        if total_chars == 0:
            return 'en'
        
        hindi_ratio = hindi_count / total_chars
        
        if hindi_ratio > 0.1:  # More than 10% Hindi characters = Hindi
            return 'hi'
        elif english_chars / total_chars > 0.5:  # More than 50% English = English
            return 'en'
        elif hindi_count > 0:  # Any Hindi characters present = Hindi
            return 'hi'
        else:
            return 'en'  # Default to English
    
    def calculate_readability(self, text):
        """Calculate how easy the text is to read"""
        if not text or len(text.split()) < 10:
            return 0
        
        try:
            # Flesch Reading Ease: Higher = easier to read
            flesch_score = textstat.flesch_reading_ease(text)
            
            # Flesch-Kincaid Grade Level: US grade level needed
            fk_grade = textstat.flesch_kincaid_grade(text)
            
            # Convert to 0-100 scale (for our display)
            # Flesch score: 0-30 (college grad), 30-50 (college), 50-60 (high school), 60-70 (8th-9th), 70-80 (7th), 80-90 (6th), 90-100 (5th)
            normalized_score = max(0, min(100, flesch_score))
            
            return {
                'flesch_score': round(flesch_score, 1),
                'fk_grade': round(fk_grade, 1),
                'normalized': round(normalized_score, 1),
                'interpretation': self.interpret_readability(flesch_score)
            }
        except:
            return {'flesch_score': 0, 'fk_grade': 0, 'normalized': 0, 'interpretation': 'Not enough text'}
    
    def interpret_readability(self, score):
        # Standard Flesch Reading Ease interpretation
        if score >= 90:
            return "Very Easy (5th grade)" 
        elif score >= 80:
            return "Easy (6th-7th grade)"
        elif score >= 70:
            return "Fairly Easy (8th grade)"
        elif score >= 60:
            return "Standard (9th-10th grade)"  # Good for tutorials
        elif score >= 50:
            return "Fairly Difficult (11th-12th grade)"
        elif score >= 30:
            return "Difficult (College level)"
        else:
            return "Very Difficult (Professional)"
    
    def analyze_jargon(self, text):
        """Analyze technical jargon density"""
        words = word_tokenize(text.lower())
        
        # Remove punctuation and stop words
        words_clean = [word for word in words if word.isalnum() and word not in self.stop_words]
        
        if not words_clean:
            return 0
        
        # Count technical terms
        technical_count = sum(1 for word in words_clean if word in self.technical_terms)
        jargon_percentage = (technical_count / len(words_clean)) * 100
        
        return {
            'technical_count': technical_count,
            'total_words': len(words_clean),
            'percentage': round(jargon_percentage, 1),
            'level': self.interpret_jargon(jargon_percentage)
        }
    
    def interpret_jargon(self, percentage):
        # Standard for educational/tutorial content
        if percentage < 5:
            return "Very Low (Extremely beginner-friendly)"
        elif percentage < 10:
            return "Low (Beginner-friendly)"  # Good for tutorials
        elif percentage < 15:
            return "Moderate (Intermediate level)"
        elif percentage < 25:
            return "High (Advanced concepts)"
        else:
            return "Very High (Expert level)"
    
    def analyze_pacing(self, transcript_data):
        """Analyze how fast concepts are introduced"""
        if not transcript_data or len(transcript_data) < 10:
            return {'words_per_minute': 0, 'pacing': 'Unknown'}
        
        # Calculate words per minute (approx)
        total_words = sum(len(snippet.text.split()) for snippet in transcript_data)
        total_minutes = transcript_data[-1].start / 60 if hasattr(transcript_data[-1], 'start') else 1
        
        if total_minutes == 0:
            total_minutes = 1
            
        words_per_minute = total_words / total_minutes
        
        return {
            'words_per_minute': round(words_per_minute),
            'pacing': self.interpret_pacing(words_per_minute)
        }
    
    def interpret_pacing(self, wpm):
        # Research: 130-160 WPM optimal for learning, 160-180 for experienced
        if wpm < 110:
            return "Very Slow (May feel dragging)"
        elif wpm < 140:
            return "Slow (Very beginner-friendly)"
        elif wpm < 170:
            return "Moderate (Ideal for learning)"  # Sweet spot!
        elif wpm < 190:
            return "Fast (For experienced learners)"
        else:
            return "Very Fast (Challenging to follow)"
    
    def determine_skill_level(self, analysis_results):
        """Determine if video is Beginner/Intermediate/Advanced using research-based thresholds"""
        readability = analysis_results.get('readability', {}).get('normalized', 0)
        jargon = analysis_results.get('jargon', {}).get('percentage', 0)
        pacing = analysis_results.get('pacing', {}).get('words_per_minute', 0)
        
        score = 0
        
        # READABILITY: 60-80 = good for tutorials (9th-10th grade level)
        if readability >= 60:  # Easy to understand
            score += 3
        elif readability >= 40:  # Moderate difficulty
            score += 2
        else:  # Hard to read
            score += 1
        
        # JARGON: 3-10% = beginner-friendly for tutorial content
        if jargon < 5:  # Very beginner-friendly
            score += 3
        elif jargon < 12:  # Still good for beginners
            score += 2
        elif jargon < 20:  # Getting advanced
            score += 1
        else:  # Expert level
            score += 0
        
        # PACING: 130-160 WPM = optimal for learning
        if 130 <= pacing <= 170:  # Ideal learning pace
            score += 3
        elif pacing < 130 or (170 < pacing <= 190):  # Slightly off
            score += 2
        else:  # Too slow or too fast
            score += 1
        
        # THRESHOLDS: Based on combined score
        if score >= 8:  # 8-9 points = excellent for beginners
            return "Beginner", score, "Perfect for beginners"
        elif score >= 6:  # 6-7 points = good for learning
            return "Intermediate", score, "Best for intermediate learners"
        else:  # 5 or below = advanced
            return "Advanced", score, "Designed for advanced learners"
    
    def determine_hindi_skill_level(self, analysis_results):
        """Special skill level determination for Hindi videos"""
        # Hindi videos often have different characteristics
        jargon = analysis_results.get('jargon', {}).get('percentage', 0)
        pacing = analysis_results.get('pacing', {}).get('words_per_minute', 0)
        
        score = 0
        
        # PACING: Hindi tutorials typically 110-150 WPM (slower than English)
        if 110 <= pacing <= 160:  # Ideal for Hindi teaching
            score += 3
        elif pacing < 110 or (160 < pacing <= 180):  # Slightly off
            score += 2
        else:  # Too extreme
            score += 1
        
        # JARGON: Hindi uses more explanatory language
        if jargon < 8:  # Very accessible
            score += 3
        elif jargon < 15:  # Still good
            score += 2
        else:  # Getting technical
            score += 1
        
        # Hindi teaching bonus (typically more beginner-friendly)
        score += 2
        
        if score >= 7:
            return "Beginner", score, "हिंदी ट्यूटोरियल - शुरुआती के लिए बिल्कुल उपयुक्त"
        elif score >= 5:
            return "Intermediate", score, "हिंदी ट्यूटोरियल - मध्यम स्तर के लिए"
        else:
            return "Advanced", score, "हिंदी ट्यूटोरियल - उन्नत स्तर के लिए"
    
    def analyze_transcript(self, transcript_text, transcript_data):
        """Main analysis function"""
        results = {}
        
        # 0. Detect language
        language = self.detect_language(transcript_text)
        results['language'] = language
        
        # 1. Readability analysis (skip for non-English)
        if language == 'en':
            results['readability'] = self.calculate_readability(transcript_text)
        else:
            results['readability'] = {
                'flesch_score': 'N/A',
                'fk_grade': 'N/A', 
                'normalized': 50,  # Default middle score for non-English
                'interpretation': f'Language: {language.upper()} (analysis limited)'
            }
        
        # 2. Jargon analysis (adjust for non-English)
        jargon_results = self.analyze_jargon(transcript_text)
        if language != 'en':
            jargon_results['level'] = f"Language: {language.upper()}"
        results['jargon'] = jargon_results
        
        # 3. Pacing analysis
        results['pacing'] = self.analyze_pacing(transcript_data)
        
        # 4. Determine skill level (adjust for non-English)
        if language == 'hi':
            # Hindi-specific analysis
            level, score, explanation = self.determine_hindi_skill_level(results)
        else:
            level, score, explanation = self.determine_skill_level(results)
        
        results['skill_level'] = level
        results['level_score'] = score
        results['level_explanation'] = explanation
        
        return results