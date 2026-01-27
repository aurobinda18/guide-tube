import re
from collections import Counter

class ChapterExtractor:
    def extract_chapters_from_description(self, description):
        """Extract timestamps and chapters from video description"""
        if not description:
            return []
        
        chapters = []
        
        # Multiple patterns for timestamps
        patterns = [
            r'(\d{1,3}:\d{2})\s*[-–]\s*(.+)',  # 00:00 - Topic
            r'(\d{1,3}:\d{2}:\d{2})\s*[-–]\s*(.+)',  # 00:00:00 - Topic
            r'(\d{1,3})\s*[:.]\s*(\d{2})\s*[-–]\s*(.+)',  # 0:00 - Topic
            r'^(\d{1,3}:\d{2})\s+(.+)',  # 00:00 Topic (no dash)
        ]
        
        for line in description.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    if len(match.groups()) == 2:
                        time, topic = match.groups()
                    else:
                        time = f"{match.group(1)}:{match.group(2)}"
                        topic = match.group(3)
                    
                    # Clean up topic
                    topic = self._clean_topic(topic)
                    
                    # Only add if meaningful topic (not just "Intro" etc.)
                    if len(topic) > 3 and not self._is_generic_topic(topic):
                        chapters.append({
                            'time': time.strip(),
                            'topic': topic,
                            'full_line': line
                        })
                    break
        
        return chapters
    
    def _clean_topic(self, topic):
        """Clean and format topic title"""
        # Remove extra symbols
        topic = re.sub(r'[\[\](){}|]', '', topic)
        
        # Capitalize first letter of each word (for short topics)
        if len(topic.split()) <= 5:
            topic = ' '.join(word.capitalize() for word in topic.split())
        
        return topic.strip()
    
    def _is_generic_topic(self, topic):
        """Check if topic is too generic"""
        generic_terms = {'intro', 'introduction', 'outro', 'conclusion', 
                        'summary', 'recap', 'welcome', 'thanks', 'thank you',
                        'end', 'start', 'beginning', 'closing'}
        
        return topic.lower() in generic_terms
    
    def generate_learning_summary_from_chapters(self, chapters, video_title):
        """Generate 'What You'll Learn' from actual chapters"""
        if not chapters:
            return self._generate_fallback_summary(video_title)
        
        summary = []
        
        # Add header
        summary.append("📋 **What You'll Learn (Video Chapters):**")
        
        # Add top 5-7 most important chapters (skip intro/outro)
        meaningful_chapters = [c for c in chapters 
                             if not self._is_generic_topic(c['topic'])]
        
        for i, chapter in enumerate(meaningful_chapters[:7]):
            summary.append(f"⏱️ **{chapter['time']}** - {chapter['topic']}")
        
        # If we have chapters, we can infer prerequisites
        if meaningful_chapters:
            tech_terms = self._extract_tech_terms([c['topic'] for c in meaningful_chapters])
            if tech_terms:
                summary.append(f"🔧 **Covers:** {', '.join(tech_terms[:3])}")
        
        # Estimate prerequisites based on content
        if any(term in video_title.lower() for term in ['advanced', 'expert', 'master']):
            summary.append("📝 **Prerequisites:** Solid foundational knowledge required")
        elif any(term in video_title.lower() for term in ['beginner', 'basics', 'introduction']):
            summary.append("📝 **Prerequisites:** No prior experience needed")
        else:
            summary.append("📝 **Prerequisites:** Basic understanding helpful")
        
        return summary
    
    def _extract_tech_terms(self, topics):
        """Extract technical terms from chapter topics"""
        common_tech_terms = {
            'python', 'javascript', 'react', 'django', 'flask', 'html', 'css',
            'machine learning', 'ai', 'data science', 'analysis', 'visualization',
            'langchain', 'llm', 'vector', 'database', 'api', 'web', 'mobile',
            'design', 'ui', 'ux', 'photoshop', 'figma', 'excel', 'powerpoint'
        }
        
        found_terms = []
        for topic in topics:
            topic_lower = topic.lower()
            for term in common_tech_terms:
                if term in topic_lower:
                    found_terms.append(term)
        
        return list(set(found_terms))
    
    def _generate_fallback_summary(self, video_title):
        """Fallback if no chapters found"""
        summary = []
        summary.append("📋 **Course Content Overview**")
        
        # Generic based on title keywords
        title_lower = video_title.lower()
        
        if 'python' in title_lower:
            summary.append("🐍 **Python programming concepts**")
            summary.append("💻 **Hands-on coding examples**")
        elif 'data' in title_lower or 'analysis' in title_lower:
            summary.append("📊 **Data analysis techniques**")
            summary.append("📈 **Practical data applications**")
        elif 'web' in title_lower:
            summary.append("🌐 **Web development fundamentals**")
            summary.append("🖥️ **Building functional websites**")
        elif 'design' in title_lower:
            summary.append("🎨 **Design principles and techniques**")
            summary.append("🖌️ **Creative project work**")
        else:
            summary.append("📚 **Core concepts and practical skills**")
            summary.append("🔧 **Step-by-step implementation**")
        
        summary.append("📝 **Prerequisites:** Willingness to learn and practice")
        
        return summary
    
    