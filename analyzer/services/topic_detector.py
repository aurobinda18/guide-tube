import nltk
from nltk import pos_tag, word_tokenize
from nltk.corpus import stopwords
from collections import Counter
import re

class TopicDetector:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Common technical terms across domains
        self.technical_indicators = {
            'programming': ['code', 'function', 'variable', 'loop', 'algorithm', 'syntax', 'debug'],
            'data': ['data', 'analysis', 'dataset', 'visualization', 'statistic', 'chart', 'graph'],
            'design': ['design', 'layout', 'color', 'interface', 'ui', 'ux', 'prototype'],
            'business': ['business', 'marketing', 'finance', 'strategy', 'management', 'analysis'],
            'academic': ['theory', 'concept', 'principle', 'research', 'study', 'paper'],
            'practical': ['tutorial', 'guide', 'step', 'practice', 'exercise', 'project']
        }
    
    def detect_topics(self, transcript_text, title):
        """Dynamically detect topics from transcript"""
        # Combine title and transcript for better context
        full_text = f"{title} {transcript_text}".lower()
        
        # Extract key terms
        key_terms = self._extract_key_terms(full_text)
        
        # Categorize topics
        topics = self._categorize_topics(key_terms, full_text)
        
        # Determine domain
        domain = self._identify_domain(topics, full_text)
        
        return {
            'key_terms': key_terms,
            'topics': topics,
            'domain': domain,
            'is_technical': self._is_technical(full_text)
        }
    
    def _extract_key_terms(self, text, n=10):
        """Extract most frequent and meaningful terms"""
        # Tokenize and clean
        words = word_tokenize(text)
        words = [word.lower() for word in words if word.isalnum() and len(word) > 2]
        
        # Remove stopwords
        filtered = [word for word in words if word not in self.stop_words]
        
        # Count frequency
        word_freq = Counter(filtered)
        
        # Get most common (excluding generic terms)
        common_terms = word_freq.most_common(n + 20)
        
        # Filter out overly generic terms
        generic_terms = {'video', 'tutorial', 'learn', 'course', 'channel', 'like', 'subscribe'}
        meaningful = [(term, freq) for term, freq in common_terms 
                     if term not in generic_terms and freq > 1]
        
        return meaningful[:n]
    
    def _categorize_topics(self, key_terms, text):
        """Categorize into topic areas"""
        topics = set()
        
        # Check for programming/tech topics
        if any(term in text for term in ['python', 'javascript', 'java', 'code', 'program']):
            topics.add('programming')
        
        # Check for data topics
        if any(term in text for term in ['data', 'analysis', 'excel', 'spreadsheet', 'chart']):
            topics.add('data_analysis')
        
        # Check for creative topics
        if any(term in text for term in ['design', 'photoshop', 'edit', 'creative', 'art']):
            topics.add('creative')
        
        # Check for business topics
        if any(term in text for term in ['business', 'marketing', 'finance', 'excel', 'presentation']):
            topics.add('business')
        
        # Check difficulty level indicators
        if any(term in text for term in ['beginner', 'basic', 'introduction', 'start', 'first']):
            topics.add('beginner_level')
        elif any(term in text for term in ['advanced', 'expert', 'deep', 'complex', 'master']):
            topics.add('advanced_level')
        else:
            topics.add('intermediate_level')
        
        return list(topics)
    
    def _identify_domain(self, topics, text):
        """Identify the main domain/subject"""
        domain_indicators = {
            'programming': ['python', 'javascript', 'java', 'c++', 'html', 'css', 'react', 'django'],
            'data_science': ['data', 'machine learning', 'ai', 'analysis', 'excel', 'sql', 'statistics'],
            'web_dev': ['web', 'website', 'frontend', 'backend', 'html', 'css', 'javascript'],
            'design': ['photoshop', 'figma', 'ui', 'ux', 'design', 'graphic', 'illustrator'],
            'business': ['excel', 'marketing', 'finance', 'presentation', 'powerpoint', 'management'],
            'language': ['english', 'spanish', 'language', 'grammar', 'vocabulary', 'speaking']
        }
        
        for domain, indicators in domain_indicators.items():
            if any(indicator in text for indicator in indicators):
                return domain
        
        return 'general'
    
    def _is_technical(self, text):
        """Determine if content is technical"""
        technical_terms = ['code', 'function', 'variable', 'algorithm', 'syntax', 
                          'data', 'analysis', 'formula', 'equation', 'technical']
        return any(term in text for term in technical_terms)
    
    def generate_learning_summary(self, topics_info, skill_level, word_count):
        """Generate dynamic learning summary based on detected topics"""
        summary = []
        
        # Domain-specific summaries
        domain = topics_info['domain']
        if domain == 'programming':
            summary.append("💻 **Programming concepts and code examples**")
            summary.append("🔧 **Practical coding exercises and projects**")
        elif domain == 'data_science':
            summary.append("📊 **Data analysis techniques and tools**")
            summary.append("📈 **Visualization and interpretation methods**")
        elif domain == 'web_dev':
            summary.append("🌐 **Web development fundamentals**")
            summary.append("🖥️ **Frontend/backend implementation**")
        elif domain == 'design':
            summary.append("🎨 **Design principles and creative techniques**")
            summary.append("🖌️ **Practical design projects**")
        elif domain == 'business':
            summary.append("📈 **Business tools and analysis methods**")
            summary.append("💼 **Practical business applications**")
        else:
            summary.append("📚 **Core concepts and practical applications**")
        
        # Add key topics from detection
        if topics_info['key_terms']:
            key_topics = [term for term, freq in topics_info['key_terms'][:3]]
            summary.append(f"🎯 **Focus areas:** {', '.join(key_topics)}")
        
        # Prerequisites based on level and domain
        if skill_level == 'Beginner':
            summary.append("📝 **Prerequisites:** No prior experience needed")
        elif topics_info['is_technical']:
            if domain == 'programming':
                summary.append("📝 **Prerequisites:** Basic computer literacy, logical thinking")
            elif domain == 'data_science':
                summary.append("📝 **Prerequisites:** Basic math understanding, analytical mindset")
            else:
                summary.append("📝 **Prerequisites:** Foundational knowledge in the subject")
        else:
            summary.append("📝 **Prerequisites:** Interest and willingness to learn")
        
        # Length indicator
        if word_count > 30000:
            summary.append("⏳ **Comprehensive coverage** - In-depth exploration")
        elif word_count > 15000:
            summary.append("⏳ **Detailed tutorial** - Thorough explanation with examples")
        else:
            summary.append("⏳ **Quick overview** - Concise introduction to key concepts")
        
        return summary