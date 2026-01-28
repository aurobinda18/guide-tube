from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .services.analysis_service import TranscriptAnalyzer
from .services.comments_analyzer import CommentsAnalyzer
from .utils.error_handler import ErrorHandler
from .services.chapter_extractor import ChapterExtractor
from .services.explanation_service import ExplanationService
from .services.learning_path_service import LearningPathService
import os
from googleapiclient.discovery import build
from django.conf import settings
from urllib.parse import urlparse, parse_qs
import re

def extract_video_id(url):
    """
    Extract YouTube video ID from various URL formats.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/shorts/VIDEO_ID
    - https://m.youtube.com/watch?v=VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    - https://www.youtube.com/v/VIDEO_ID
    """
    if not url:
        return None
    
    # Remove whitespace
    url = url.strip()
    
    # Pattern 1: Standard watch URL with v parameter
    if 'v=' in url:
        try:
            parsed_url = urlparse(url)
            query_params = parse_qs(parsed_url.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                # Video IDs are 11 characters
                return video_id[:11] if len(video_id) >= 11 else video_id
        except:
            pass
    
    # Pattern 2: Short URL (youtu.be/VIDEO_ID)
    if 'youtu.be/' in url:
        try:
            video_id = url.split('youtu.be/')[1].split('?')[0].split('&')[0]
            return video_id[:11] if len(video_id) >= 11 else video_id
        except:
            pass
    
    # Pattern 3: Shorts URL
    if '/shorts/' in url:
        try:
            video_id = url.split('/shorts/')[1].split('?')[0].split('&')[0]
            return video_id[:11] if len(video_id) >= 11 else video_id
        except:
            pass
    
    # Pattern 4: Embed URL
    if '/embed/' in url:
        try:
            video_id = url.split('/embed/')[1].split('?')[0].split('&')[0]
            return video_id[:11] if len(video_id) >= 11 else video_id
        except:
            pass
    
    # Pattern 5: /v/ URL
    if '/v/' in url:
        try:
            video_id = url.split('/v/')[1].split('?')[0].split('&')[0]
            return video_id[:11] if len(video_id) >= 11 else video_id
        except:
            pass
    
    # Pattern 6: Just the video ID (11 characters, alphanumeric with - and _)
    # YouTube video IDs are exactly 11 characters: letters, numbers, hyphens, underscores
    if len(url) == 11:
        # Check if it's a valid video ID format
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_')
        if all(char in valid_chars for char in url):
            return url
    
    return None

def get_youtube_api():
    """Get YouTube API instance using Django settings"""
    API_KEY = settings.YOUTUBE_API_KEY
    
    if not API_KEY:
        raise ValueError('YouTube API key is not configured in settings')
    
    return build('youtube', 'v3', developerKey=API_KEY)

def calculate_recommendation_score(video, target_level):
    """Calculate how well this video matches target level"""
    level_values = {'beginner': 1, 'intermediate': 2, 'advanced': 3}

    video_level = video['skill_level'].lower()
    level_distance = abs(
        level_values.get(video_level, 2) -
        level_values.get(target_level, 2)
    )

    if level_distance == 0:
        level_match_score = 100
    elif level_distance == 1:
        level_match_score = 70
    else:
        level_match_score = 30

    # Safe access to readability with proper fallback
    try:
        readability = video['analysis']['readability'].get('normalized', 50)
        if readability == 'N/A':
            readability = 50
        readability = float(readability) if readability else 50
    except (KeyError, TypeError, ValueError):
        readability = 50

    # Safe access to jargon percentage
    try:
        jargon = video['analysis']['jargon'].get('percentage', 0)
        jargon = float(jargon) if jargon else 0
    except (KeyError, TypeError, ValueError):
        jargon = 0

    # Safe access to pacing
    try:
        pacing = video['analysis']['pacing'].get('words_per_minute', 150)
        pacing = float(pacing) if pacing else 150
    except (KeyError, TypeError, ValueError):
        pacing = 150

    if 120 <= pacing <= 160:
        pacing_score = 100
    elif pacing < 120:
        pacing_score = 80 - (120 - pacing)
    else:
        pacing_score = 80 - (pacing - 160)

    pacing_score = max(0, min(100, pacing_score))

    content_score = (
        readability * 0.5 +
        (100 - min(jargon * 10, 100)) * 0.3 +
        pacing_score * 0.2
    )

    overall_score = (level_match_score * 0.7) + (content_score * 0.3)

    return round(overall_score, 1)

@login_required
def compare_videos(request):
    """Multi-video comparison page - requires login"""
    comparison_results = None

    # If somehow user bypasses decorator, check again
    if not request.user.is_authenticated:
        messages.info(request, 'Please log in to compare videos.')
        return redirect(f'/login/?next=/compare/')
    
    if request.method == 'POST':
        video_urls = []
        for i in range(1, 5):
            url_key = f'video_url_{i}'
            if url_key in request.POST and request.POST[url_key].strip():
                video_urls.append(request.POST[url_key].strip())

        target_level = request.POST.get('target_level', 'beginner')

        if len(video_urls) >= 2:
            try:
                youtube = get_youtube_api()
                analyzer = TranscriptAnalyzer()
                videos_data = []
                failed_videos = []  # Track failed videos

                for url in video_urls:
                    video_id = extract_video_id(url)
                    
                    # ✅ CHECK IF VIDEO ID IS VALID
                    if not video_id:
                        failed_videos.append({
                            'url': url,
                            'error': 'Invalid YouTube URL format'
                        })
                        print(f"❌ Invalid URL format: {url}")
                        continue

                    request_api = youtube.videos().list(
                        part="snippet",
                        id=video_id
                    )
                    response = request_api.execute()

                    if not response['items']:
                        # Video not found
                        failed_videos.append({
                            'url': url,
                            'video_id': video_id,
                            'error': 'Video not found. It may be private, deleted, or unavailable.'
                        })
                        print(f"❌ Video not found: {video_id}")
                        continue

                    video = response['items'][0]

                    from youtube_transcript_api import YouTubeTranscriptApi
                    
                    try:
                        api = YouTubeTranscriptApi()
                        transcript_list = api.list(video_id)
                    except Exception as transcript_error:
                        print(f"⚠️ Transcript blocked for {video_id}: {str(transcript_error)[:150]}")
                        failed_videos.append({
                            'url': url,
                            'video_id': video_id,
                            'error': 'Transcript unavailable or blocked'
                        })
                        # Skip this video if transcript is blocked
                        continue

                    try:
                        transcript_obj = transcript_list.find_transcript(['en'])
                    except:
                        try:
                            transcript_obj = transcript_list.find_transcript(['hi'])
                        except:
                            transcript_obj = (
                                transcript_list._manually_created_transcripts[0]
                                if transcript_list._manually_created_transcripts
                                else transcript_list._generated_transcripts[0]
                            )

                    transcript_data = list(transcript_obj.fetch())
                    transcript_text = ' '.join(
                        [snippet.text for snippet in transcript_data]
                    )

                    analysis = analyzer.analyze_transcript(
                        transcript_text,
                        transcript_data
                    )

                    # Add comments analysis
                    try:
                        API_KEY = settings.YOUTUBE_API_KEY
                        comments_analyzer = CommentsAnalyzer(API_KEY)
                        comments_analysis = comments_analyzer.analyze_video_comments(
                            video_id,
                            max_comments=50
                        )
                        analysis['comments'] = comments_analysis
                    except Exception as e:
                        analysis['comments'] = {
                            'error': 'Could not analyze comments'
                        }

                    videos_data.append({
                        'url': url,
                        'video_id': video_id,
                        'title': video['snippet']['title'],
                        'description': video['snippet']['description'],  # ADD THIS LINE
                        'channel': video['snippet']['channelTitle'],
                        'analysis': analysis,
                        'skill_level': analysis['skill_level'],
                        'level_score': analysis['level_score'],
                        'word_count': sum(
                            len(snippet.text.split())
                            for snippet in transcript_data
                        ),
                        'transcript_text': transcript_text
                    })

                # ✅ CHECK IF ANY VIDEOS WERE SUCCESSFULLY PROCESSED
                if not videos_data:
                    # All videos failed
                    error_msg = "Unable to process any videos. "
                    if failed_videos:
                        error_msg += "Errors: " + "; ".join([f"{v.get('video_id', 'Unknown')}: {v['error']}" for v in failed_videos])
                    comparison_results = {
                        'error': error_msg,
                        'failed_videos': failed_videos
                    }
                    messages.error(request, error_msg)
                elif len(videos_data) < 2:
                    # Less than 2 videos succeeded
                    comparison_results = {
                        'error': f'Only {len(videos_data)} video(s) could be processed. Please provide at least 2 valid YouTube videos.',
                        'failed_videos': failed_videos,
                        'videos': videos_data
                    }
                    messages.warning(request, f'Only {len(videos_data)} video(s) could be processed. Need at least 2 for comparison.')
                else:
                    # Success - 2 or more videos processed
                    comparison_results = {
                        'videos': videos_data,
                        'target_level': target_level,
                        'recommended_video': None,
                        'comparison_metrics': {},
                        'failed_videos': failed_videos  # Show which ones failed
                    }

                    for video in videos_data:
                        try:
                            video['recommendation_score'] = calculate_recommendation_score(
                                video,
                                target_level
                            )
                        except Exception as score_error:
                            print(f"⚠️ Error calculating score for {video.get('title', 'Unknown')}: {score_error}")
                            video['recommendation_score'] = 50  # Default middle score

                    videos_data.sort(
                        key=lambda x: x['recommendation_score'],
                        reverse=True
                    )

                    comparison_results['recommended_video'] = videos_data[0]
                    comparison_results['videos'] = videos_data
                    
                    # Generate explanations for recommended video
                    try:
                        explanation_service = ExplanationService()
                        comparison_results['why_this_video'] = explanation_service.generate_why_this_video(
                            videos_data[0], 
                            target_level
                        )
                    except Exception as exp_error:
                        print(f"⚠️ Error generating explanation: {exp_error}")
                        comparison_results['why_this_video'] = "Unable to generate explanation"
                    
                    # Make sure we have transcript text in the video data
                    try:
                        comparison_results['pre_watch_summary'] = explanation_service.generate_pre_watch_summary(
                            videos_data[0]  # Now has transcript_text
                        )
                    except Exception as summary_error:
                        print(f"⚠️ Error generating summary: {summary_error}")
                        comparison_results['pre_watch_summary'] = "Unable to generate summary"
                    
                    # Add learning path suggestions
                    try:
                        learning_service = LearningPathService()

                        # Get chapters for the recommended video
                        chapter_extractor = ChapterExtractor()
                        description = videos_data[0].get('description', '')
                        chapters = chapter_extractor.extract_chapters_from_description(description)

                        comparison_results['learning_path'] = learning_service.generate_learning_path(
                            videos_data[0]['title'],
                            chapters,
                            videos_data[0]['skill_level'],
                            videos_data[0].get('word_count', 0)
                        )
                    except Exception as path_error:
                        print(f"⚠️ Error generating learning path: {path_error}")
                        comparison_results['learning_path'] = "Unable to generate learning path"
                    
                    def get_level_display_name(level):
                        return level.title()

                    level_videos = [
                        v for v in videos_data
                        if v['skill_level'].lower() == target_level
                    ]

                    if level_videos:
                        level_videos.sort(
                            key=lambda x: x['recommendation_score'],
                            reverse=True
                        )
                        comparison_results[f'best_for_{target_level}'] = level_videos[0]
                        comparison_results['best_for_level_display'] = get_level_display_name(
                            target_level
                        )
                    else:
                        level_values = {'beginner': 1, 'intermediate': 2, 'advanced': 3}
                        closest_video = min(
                            videos_data,
                            key=lambda v: abs(
                                level_values.get(v['skill_level'].lower(), 2) -
                                level_values.get(target_level, 2)
                            )
                        )
                        comparison_results[f'best_for_{target_level}'] = closest_video
                        comparison_results['best_for_level_display'] = get_level_display_name(
                            target_level
                        )
                    
                    # Show success message with any failed videos
                    if failed_videos:
                        messages.warning(request, f'{len(videos_data)} videos successfully compared. {len(failed_videos)} video(s) failed.')
                    else:
                        messages.success(request, f'Successfully compared {len(videos_data)} videos!')

            except Exception as e:
                ErrorHandler.log_error(e, "Video Comparison")
                comparison_results = {
                    'error': ErrorHandler.get_user_friendly_error(e)
                }

    return render(
        request,
        'analyzer/compare.html',
        {
            'comparison_results': comparison_results
        }
    )