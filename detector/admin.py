from django.contrib import admin
from .models import VideoUpload

@admin.register(VideoUpload)
class VideoUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'status', 'uploaded_at', 'total_frames', 'accident_frames', 'detection_rate']
    list_filter = ['status', 'uploaded_at']
    search_fields = ['id']
    readonly_fields = ['uploaded_at', 'processed_at']
