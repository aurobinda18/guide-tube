# analyzer/services/learning_path_service.py

class LearningPathService:
    def generate_learning_path(self, video_title, chapters, skill_level, word_count):
        """Generate universal learning path that works for ANY subject"""
        
        # Step 1: Analyze what kind of content this is
        content_type = self._analyze_content_type(video_title, chapters, word_count)
        
        # Step 2: Generate universal learning guidance
        return self._generate_universal_guidance(video_title, content_type, skill_level)
    
    def _analyze_content_type(self, video_title, chapters, word_count):
        """Analyze what type of learning content this is"""
        title_lower = video_title.lower()
        
        # Check content depth
        if word_count > 20000:
            depth = 'comprehensive'
        elif word_count > 8000:
            depth = 'detailed'
        else:
            depth = 'overview'
        
        # Check content style
        if any(word in title_lower for word in ['project', 'build', 'create', 'make']):
            style = 'project-based'
        elif any(word in title_lower for word in ['tutorial', 'guide', 'how to']):
            style = 'tutorial'
        elif any(word in title_lower for word in ['theory', 'concept', 'fundamental']):
            style = 'theoretical'
        elif any(word in title_lower for word in ['crash course', 'fast', 'quick']):
            style = 'quick-start'
        else:
            style = 'general'
        
        # Check if it has structure
        has_structure = len(chapters) > 3
        
        return {
            'depth': depth,
            'style': style,
            'has_structure': has_structure,
            'chapter_count': len(chapters)
        }
    
    def _generate_universal_guidance(self, video_title, content_type, skill_level):
        """Generate guidance that works for ANY subject"""
        guidance = []
        
        # Header
        guidance.append("📚 **Your Learning Journey Guide**")
        guidance.append(f"🎯 **Video:** {video_title}")
        guidance.append("")
        
        # Part 1: How to study THIS video
        guidance.append("👨‍🏫 **How to Get the Most from This Video:**")
        guidance.append("")
        
        if content_type['depth'] == 'overview':
            guidance.append("• **This is an overview** - Don't expect mastery")
            guidance.append("• **Take notes on key concepts** - Focus on the big picture")
            guidance.append("• **Identify what interests you** - Note topics to explore deeper")
        elif content_type['depth'] == 'detailed':
            guidance.append("• **This is detailed content** - Set aside focused time")
            guidance.append("• **Practice as you watch** - Pause and implement")
            guidance.append("• **Bookmark complex sections** - Return to them later")
        else:  # comprehensive
            guidance.append("• **This is comprehensive** - Break into multiple sessions")
            guidance.append("• **Create a study schedule** - 30-60 minute chunks")
            guidance.append("• **Review previous sections** - Before starting new ones")
        
        if content_type['has_structure']:
            guidance.append("• **Use the chapter timestamps** - Jump to what you need")
            guidance.append("• **Focus on core chapters** - Skip intro/outro if needed")
        
        guidance.append("")
        
        # Part 2: What to do AFTER this video (Universal progression)
        guidance.append("🎯 **Your Next Learning Steps:**")
        guidance.append("")
        
        # Universal learning progression
        guidance.append("1. **Immediate Practice (Next 24 hours)**")
        guidance.append("   → Apply what you learned immediately")
        guidance.append("   → Even if it's small, make it complete")
        guidance.append("")
        
        guidance.append("2. **Deepen Understanding (This week)**")
        
        if skill_level.lower() == 'beginner':
            guidance.append("   → Find 2-3 more beginner videos on this topic")
            guidance.append("   → Different explanations help understanding")
        elif skill_level.lower() == 'intermediate':
            guidance.append("   → Find a project tutorial using these concepts")
            guidance.append("   → Build something real, not just follow along")
        else:  # advanced
            guidance.append("   → Read official documentation or research papers")
            guidance.append("   → Explore edge cases and limitations")
        
        guidance.append("")
        
        guidance.append("3. **Build Portfolio (This month)**")
        guidance.append("   → Create something showcase-worthy")
        guidance.append("   → Document your learning journey")
        guidance.append("   → Share with community for feedback")
        guidance.append("")
        
        # Part 3: Universal learning principles
        guidance.append("💡 **Universal Learning Principles:**")
        guidance.append("")
        guidance.append("• **Spaced Repetition:** Review after 1 day, 1 week, 1 month")
        guidance.append("• **Active Recall:** Test yourself without looking at notes")
        guidance.append("• **Interleaving:** Mix different but related topics")
        guidance.append("• **Deliberate Practice:** Focus on your weak areas")
        guidance.append("• **Teach Others:** The best way to learn is to teach")
        guidance.append("")
        
        # Part 4: Subject-specific if we can detect
        detected_subjects = self._detect_possible_subjects(video_title)
        if detected_subjects:
            main_subject = detected_subjects[0].upper()  # Get first detected subject
            guidance.append(f"🔍 **Detected Field:** {main_subject}")
            guidance.append(f"   → Search for: '{main_subject} projects for beginners'")
            guidance.append(f"   → Join: '{main_subject} learning communities'")
            guidance.append(f"   → Follow: Top {main_subject} educators on YouTube")
        
        guidance.append("")
        guidance.append("🌟 **Remember:** Learning is a marathon, not a sprint. Consistency > Intensity.")
        
        return guidance
    
    def _detect_possible_subjects(self, video_title):
        """Try to detect subject for slightly personalized tips"""
        title_lower = video_title.lower()
        subjects = []
        
        # Common subjects (non-exhaustive)
        subject_keywords = {
            'programming': ['python', 'javascript', 'java', 'c++', 'coding', 'program'],
            'data': ['sql', 'excel', 'analysis', 'visualization', 'power bi'],
            'web': ['html', 'css', 'react', 'website', 'frontend'],
            'ai': ['machine learning', 'ai', 'neural', 'llm', 'langchain'],
            'design': ['photoshop', 'figma', 'ui', 'ux', 'design'],
            'business': ['excel', 'powerpoint', 'marketing', 'finance']
        }
        
        for subject, keywords in subject_keywords.items():
            for keyword in keywords:
                if keyword in title_lower:
                    subjects.append(subject)
                    break
        
        return list(set(subjects))