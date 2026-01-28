from django.shortcuts import render
import os
import re
from googleapiclient.discovery import build
from .utils.error_handler import ErrorHandler
from .services.rag_service import RAGService
from .services.qa_service import QAService
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.conf import settings
from urllib.parse import urlparse, parse_qs

# ======================
# UTILITY FUNCTIONS
# ======================

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

# ======================
# HOME PAGE (Landing Page)
# ======================
def home(request):
    """Render the landing page"""
    return render(request, 'analyzer/home.html')

# ======================
# ABOUT PAGE
# ======================
def about(request):
    return render(request, 'analyzer/about.html')

# ======================
# AUTHENTICATION VIEWS
# ======================

def login_view(request):
    """Handle user login"""
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    # Check for success message from signup
    signup_success = False
    for message in messages.get_messages(request):
        if 'success' in message.tags and 'Account created successfully' in message.message:
            signup_success = True
            break
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember_me = request.POST.get('remember')
        
        # Try to get user by email (username field in Django)
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            username = email  # Fallback to email as username
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Login the user
            login(request, user)
            
            # Handle "remember me" option
            if not remember_me:
                # Set session to expire when browser closes
                request.session.set_expiry(0)
            
            # ✅ FIXED: Get the 'next' parameter properly
            next_url = request.GET.get('next')
            if next_url:
                # If there's a 'next' parameter, redirect to that URL
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect(next_url)
            else:
                # If no 'next' parameter, go to dashboard
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')
                return redirect('dashboard')
        else:
            messages.error(request, 'Invalid email or password. Please try again.')
    
    # Pass signup_success flag to template
    return render(request, 'analyzer/login.html', {
        'signup_success': signup_success
    })

def signup_view(request):
    """Handle user registration"""
    # If user is already logged in, redirect to dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        terms = request.POST.get('terms')
        
        # Validation
        errors = []
        
        # Check if passwords match
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check password strength
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long.')
        
        # Check if email already exists
        if User.objects.filter(email=email).exists():
            errors.append('An account with this email already exists.')
        
        # Check if username (email) already exists
        if User.objects.filter(username=email).exists():
            errors.append('An account with this email already exists.')
        
        # Check terms agreement
        if not terms:
            errors.append('You must agree to the Terms of Service.')
        
        # If no errors, create user
        if not errors:
            try:
                # Create user with email as username
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password
                )
                
                # Set first and last name if provided
                if full_name:
                    name_parts = full_name.split(' ', 1)
                    user.first_name = name_parts[0]
                    if len(name_parts) > 1:
                        user.last_name = name_parts[1]
                
                user.save()
                
                # ✅ CHANGE: DON'T auto-login. Instead show success message and redirect to login
                messages.success(request, f'Account created successfully! Welcome to GuideTube, {full_name or email}. Please log in to continue.')
                
                # ✅ CHANGE: Redirect to login page instead of dashboard
                return redirect('login')
                
            except Exception as e:
                errors.append(f'Error creating account: {str(e)}')
        
        # If there are errors, show them
        for error in errors:
            messages.error(request, error)
    
    # Render signup page
    return render(request, 'analyzer/signup.html')

@login_required
def dashboard_view(request):
    """Show user dashboard after login"""
    # Get user's recent activity or other data if needed
    user_data = {
        'name': request.user.first_name or request.user.username,
        'email': request.user.email,
        'join_date': request.user.date_joined.strftime('%B %d, %Y') if request.user.date_joined else 'Recently'
    }
    
    return render(request, 'analyzer/dashboard.html', {
        'user': request.user,
        'user_data': user_data
    })

# ======================
# VIDEO ANALYSIS & Q&A
# ======================
def _parse_duration(duration_iso):
    """Convert YouTube duration (PT1H15M30S) to minutes"""
    # PT1H15M30S -> 75.5 minutes
    hours = re.search(r'(\d+)H', duration_iso)
    minutes = re.search(r'(\d+)M', duration_iso)
    seconds = re.search(r'(\d+)S', duration_iso)
    
    total_minutes = 0
    
    if hours:
        total_minutes += int(hours.group(1)) * 60
    if minutes:
        total_minutes += int(minutes.group(1))
    if seconds:
        total_minutes += int(seconds.group(1)) / 60
    
    return round(total_minutes, 1)

@login_required
def video_analyse_QA(request):
    """Video analysis page - requires login"""
    video_info = None
    question_asked = False
    question = ""
    answer_lines = []
    
    if request.method == 'POST':
        # Check if it's a Q&A question
        if 'question_mode' in request.POST:
            question_asked = True
            question = request.POST.get('question', '')
            video_id = request.POST.get('video_id', '')
            video_title = request.POST.get('video_title', '')
            transcript_text = request.POST.get('transcript_text', '')
            duration_minutes = request.POST.get('duration_minutes', 60)
            
            # IMPORTANT: Reconstruct video_info from POST data
            video_info = {
                'title': video_title,
                'video_id': video_id,
                'has_transcript': True,
                'transcript_text': transcript_text,
                'duration_minutes': float(duration_minutes),
                # Add minimal info needed for display
                'channel': 'Previous Analysis',
                'description': 'Video previously analyzed',
                'word_count': len(transcript_text.split()),
                'analysis': {'level_score': 'N/A'},
                'skill_level': 'Beginner'
            }
            
            # ========== USE RAG SERVICE ==========
            try:
                rag_service = RAGService()
                
                # Process transcript first (store in vector DB)
                print("🔄 Processing transcript for RAG...")
                chunks_count = rag_service.process_transcript(
                    transcript_text, 
                    video_id, 
                    video_info.get('duration_minutes', 60)
                )
                print(f"✅ Processed {chunks_count} chunks")
                
                # Ask question using RAG
                print(f"🤔 Asking: {question[:50]}...")
                rag_result = rag_service.ask_question(
                    question, 
                    video_id, 
                    video_title,
                    video_info.get('duration_minutes', 60)
                )
                
                # Format answer for display
                answer_lines = rag_service.format_for_display(rag_result)
                print("✅ RAG answer generated")
                
            except Exception as e:
                print(f"❌ RAG Error: {e}")
                # Fallback to simple Q&A if RAG fails
                qa_service = QAService()
                qa_result = qa_service.find_answer_in_transcript(
                    question, 
                    transcript_text, 
                    video_title
                )
                answer_lines = qa_service.format_answer_for_display(qa_result)
            # ========== END RAG ==========
            
        # Original video analysis code
        elif 'video_url' in request.POST:
            video_url = request.POST['video_url']
            
            # Extract video ID using comprehensive parser
            video_id = extract_video_id(video_url)
            
            if not video_id:
                # Invalid URL format
                video_info = {
                    'error': 'Invalid YouTube URL. Please enter a valid YouTube video URL. Supported formats: youtube.com/watch?v=..., youtu.be/..., youtube.com/shorts/...'
                }
            else:
                # Get API key from settings
                API_KEY = settings.YOUTUBE_API_KEY
                
                if not API_KEY:
                    video_info = {
                        'error': 'YouTube API key is not configured. Please contact the administrator.'
                    }
                else:
                    # Fetch video info WITH DURATION
                    try:
                        youtube = build('youtube', 'v3', developerKey=API_KEY)
                        request_api = youtube.videos().list(
                            part="snippet,contentDetails",
                            id=video_id
                        )
                        response = request_api.execute()
                        
                        if response.get('items') and len(response['items']) > 0:
                            video = response['items'][0]
                            
                            # Get video duration
                            duration_iso = video['contentDetails']['duration']  # PT1H15M30S
                            duration_minutes = _parse_duration(duration_iso)
                            
                            video_info = {
                                'title': video['snippet']['title'],
                                'channel': video['snippet']['channelTitle'],
                                'description': video['snippet']['description'],
                                'video_id': video_id,
                                'duration_minutes': duration_minutes,
                                'has_transcript': False,
                                'word_count': 0,
                                'transcript_text': ''
                            }
                            
                            # Try to get transcript
                            try:
                                from youtube_transcript_api import YouTubeTranscriptApi
                                api = YouTubeTranscriptApi()
                                transcript_list = api.list(video_id)
                                
                                # Try English first, then Hindi, then any available transcript
                                try:
                                    transcript_obj = transcript_list.find_transcript(['en'])
                                except:
                                    try:
                                        transcript_obj = transcript_list.find_transcript(['hi'])  # Hindi
                                    except:
                                        # Get the first available transcript
                                        transcript_obj = transcript_list._manually_created_transcripts[0] if transcript_list._manually_created_transcripts else transcript_list._generated_transcripts[0]
                                
                                transcript_data = list(transcript_obj.fetch())
                                
                                video_info['has_transcript'] = True
                                video_info['word_count'] = sum(len(snippet.text.split()) for snippet in transcript_data)
                                video_info['transcript_sample'] = ' '.join([snippet.text for snippet in transcript_data[:5]])
                                video_info['transcript_full'] = ' '.join([snippet.text for snippet in transcript_data])
                                video_info['transcript_text'] = video_info['transcript_full']
                                
                                # Analyze the transcript
                                try:
                                    from .services.analysis_service import TranscriptAnalyzer
                                    analyzer = TranscriptAnalyzer()
                                    analysis_results = analyzer.analyze_transcript(video_info['transcript_full'], transcript_data)
                                    video_info['analysis'] = analysis_results
                                    video_info['skill_level'] = analysis_results['skill_level']
                                except Exception as e:
                                    video_info['analysis_error'] = str(e)
                                
                            except Exception as e:
                                video_info['transcript_error'] = str(e)
                        else:
                            # Video not found or private/deleted
                            video_info = {
                                'error': f'Video not found (ID: {video_id}). The video might be private, deleted, or unavailable in your region.'
                            }
                                
                    except Exception as e:
                        ErrorHandler.log_error(e, "YouTube API")
                        video_info = {'error': ErrorHandler.get_user_friendly_error(e)}
    
    return render(request, 'analyzer/video_analyse_QA.html', {
        'video_info': video_info,
        'question_asked': question_asked,
        'question': question,
        'answer_lines': answer_lines
    })

from django.contrib.auth import logout  # Make sure this import exists

def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')