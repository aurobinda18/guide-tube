from django.urls import path
from . import views
from . import views_comparison

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Protected pages (require login)
    path('analyze/', views.video_analyse_QA, name='video_analyse_QA'),
    path('compare/', views_comparison.compare_videos, name='compare'),
]