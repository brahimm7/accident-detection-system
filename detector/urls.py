from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('upload/', views.upload_video, name='upload_video'),
    path('video/<int:video_id>/', views.video_detail, name='video_detail'),
    path('video/<int:video_id>/status/', views.video_status, name='video_status'),
    path('video/<int:video_id>/frame/', views.get_processing_frame, name='get_processing_frame'),
    path('video/<int:video_id>/delete/', views.delete_video, name='delete_video'),
    path('history/', views.history, name='history'),
    
    # Real-time webcam routes
    path('realtime/', views.realtime, name='realtime'),
    path('realtime/start/', views.start_webcam, name='start_webcam'),
    path('realtime/stop/', views.stop_webcam, name='stop_webcam'),
    path('realtime/feed/', views.webcam_feed, name='webcam_feed'),
]
