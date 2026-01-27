from .topic_detector import TopicDetector
from .chapter_extractor import ChapterExtractor

class ExplanationService:
    def generate_why_this_video(self, video, target_level):
        """Generate detailed explanation of why this video is recommended"""
        
        level = video['skill_level']
        readability = video['analysis']['readability'].get('flesch_score', 0)
        jargon = video['analysis']['jargon'].get('percentage', 0)
        pacing = video['analysis']['pacing'].get('words_per_minute', 0)
        comments = video['analysis'].get('comments', {})
        
        # Get the recommendation score (8/8 from your table)
        score = video.get('recommendation_score', 0)
        score_percentage = min(int((score / 100) * 8), 8)  # Convert to 8/8 scale
        
        explanations = []
        
        # 1. Score-based explanation
        if score_percentage >= 7:
            explanations.append(f"🏆 **Top-rated choice** - Scored {score_percentage}/8, highest among compared videos")
        elif score_percentage >= 5:
            explanations.append(f"✅ **Solid pick** - Scored {score_percentage}/8 based on multiple factors")
        else:
            explanations.append(f"⚖️ **Balanced option** - Scored {score_percentage}/8, best available match")
                    # 2. Level match explanation
        if level.lower() == target_level:
            explanations.append("🎯 **Perfect level match** - This video is exactly at your selected skill level")
        else:
            level_distance = self._get_level_distance(level.lower(), target_level)
            if level_distance == 1:
                explanations.append(f"🎯 **Good fit** - This {level} video is close to your requested {target_level} level")
            else:
                explanations.append(f"🎯 **Alternative option** - While you requested {target_level}, this {level} video is the closest match available")
        
        # 3. Readability explanation
        if readability != 'N/A':
            if readability > 70:
                explanations.append("📚 **Easy to understand** - Uses simple language and clear explanations")
            elif readability > 50:
                explanations.append("📚 **Moderate difficulty** - Balanced language suitable for learning")
            else:
                explanations.append("📚 **Challenging content** - Uses complex language, best for focused learners")
        
        # 4. Jargon explanation
        if jargon < 5:
            explanations.append("🔤 **Beginner-friendly terminology** - Minimal technical jargon, easy to follow")
        elif jargon < 15:
            explanations.append("🔤 **Moderate technical terms** - Introduces concepts with appropriate terminology")
        else:
            explanations.append("🔤 **Technical focus** - Uses specialized terms for in-depth learning")
        
        # 5. Pacing explanation
        if pacing < 140:
            explanations.append("⏱️ **Comfortable pace** - Speaks slowly enough for beginners to follow")
        elif pacing < 180:
            explanations.append("⏱️ **Balanced speed** - Good pace for most learners")
        else:
            explanations.append("⏱️ **Fast-paced** - Quick delivery, best for experienced learners")
        
        # 6. Comments explanation
        if comments.get('total_comments', 0) > 0:
            if comments.get('sentiment') == 'Positive':
                understanding = comments.get('understanding_score', 0)
                if understanding > 20:
                    explanations.append(f"💬 **Highly praised** - {understanding}% of viewers found it clear and helpful")
                else:
                    explanations.append("💬 **Positive feedback** - Viewers generally found it useful")
            elif comments.get('sentiment') == 'Confusing':
                confusion = comments.get('confusion_score', 0)
                explanations.append(f"💬 **Some confusion** - {confusion}% of viewers found parts difficult")
        
        # 7. Length explanation
        word_count = video.get('word_count', 0)
        if word_count > 30000:
            explanations.append("📏 **Comprehensive coverage** - Detailed, in-depth tutorial")
        elif word_count > 10000:
            explanations.append("📏 **Moderate length** - Balanced coverage of topics")
        else:
            explanations.append("📏 **Concise tutorial** - Quick overview of concepts")
        
        return explanations
    
    def _get_level_distance(self, video_level, target_level):
        """Calculate distance between levels"""
        levels = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
        return abs(levels.get(video_level, 1) - levels.get(target_level, 1))
    
    def _get_domain_specific_tips(self, domain):
        """Get domain-specific learning tips"""
        tips = {
            'programming': [
                "💻 **Code along** - Type the code yourself as you watch",
                "🐛 **Debug actively** - Don't just copy, understand why things work",
                "🔁 **Practice variations** - Modify the code to try different approaches"
            ],
            'data_science': [
                "📊 **Use your own data** - Apply techniques to datasets you care about",
                "📈 **Visualize everything** - Create charts to understand patterns",
                "🔍 **Ask questions** - Formulate hypotheses before analyzing"
            ],
            'web_dev': [
                "🌐 **Build alongside** - Create a real project as you learn",
                "🛠️ **Inspect elements** - Use browser dev tools to see how things work",
                "📱 **Test responsiveness** - Check how sites work on different devices"
            ],
            'design': [
                "🎨 **Sketch first** - Plan your designs on paper before digital",
                "👁️ **Study references** - Analyze designs you admire to learn techniques",
                "🔄 **Iterate often** - Create multiple versions to find the best solution"
            ],
            'business': [
                "📈 **Apply immediately** - Use techniques on real business problems",
                "💼 **Case studies** - Analyze how successful companies use these methods",
                "📊 **Measure results** - Track the impact of what you implement"
            ]
        }
        
        return tips.get(domain, [
            "📝 **Take notes** - Write down key concepts and timestamps",
            "🔁 **Review regularly** - Revisit difficult sections multiple times",
            "💭 **Think critically** - Ask yourself why things work the way they do",
            "🔄 **Apply knowledge** - Use what you learn in practical situations"
        ])
    
    def generate_pre_watch_summary(self, video):
        """Generate what you'll learn from ACTUAL video chapters"""
        description = video.get('description', '')
        title = video['title']
        
        print(f"DEBUG: Title: {title}")
        print(f"DEBUG: Description length: {len(description)}")
        print(f"DEBUG: First 200 chars of description: {description[:200]}")
        
        # Initialize chapter extractor
        chapter_extractor = ChapterExtractor()
        
        # Extract actual chapters from description
        chapters = chapter_extractor.extract_chapters_from_description(description)
        
        print(f"DEBUG: Found {len(chapters)} chapters")
        for i, chapter in enumerate(chapters):
            print(f"DEBUG Chapter {i}: {chapter['time']} - {chapter['topic']}")
        
        # Generate summary from REAL chapters
        if chapters:
            return chapter_extractor.generate_learning_summary_from_chapters(chapters, title)
        else:
            # If no chapters, return simple, honest message
            return self._generate_honest_summary(video)
    
    def _generate_honest_summary(self, video):
        """Return honest summary when we can't extract chapters"""
        summary = []
        summary.append("📋 **What You'll Learn:**")
        
        # Just show what we actually know from the title
        title_lower = video['title'].lower()
        
        if any(term in title_lower for term in ['python', 'programming', 'code']):
            summary.append("💻 **Programming concepts and examples**")
        elif any(term in title_lower for term in ['data', 'analysis', 'visualization']):
            summary.append("📊 **Data-related techniques**")
        elif any(term in title_lower for term in ['web', 'html', 'css', 'javascript']):
            summary.append("🌐 **Web development topics**")
        elif any(term in title_lower for term in ['langchain', 'llm', 'ai', 'machine learning']):
            summary.append("🤖 **AI and language model concepts**")
        else:
            summary.append("📚 **Content based on the video title**")
        
        # Always be honest about what we're showing
        summary.append("ℹ️ **Note:** Based on video title analysis")
        summary.append("📝 **Watch the video to see actual content**")
        
        return summary
    
