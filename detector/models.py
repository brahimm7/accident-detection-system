from django.db import models
from django.utils import timezone

class VideoUpload(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    video_file = models.FileField(upload_to='uploads/')
    output_video = models.FileField(upload_to='outputs/', null=True, blank=True)
    uploaded_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Detection results
    total_frames = models.IntegerField(default=0)
    accident_frames = models.IntegerField(default=0)
    detection_rate = models.FloatField(default=0.0)
    processing_time = models.FloatField(default=0.0)
    
    # Settings used
    confidence_threshold = models.FloatField(default=0.5)
    smoothing_frames = models.IntegerField(default=15)
    
    # Error message if failed
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Video {self.id} - {self.status}"
    
    @property
    def detection_percentage(self):
        if self.total_frames > 0:
            return (self.accident_frames / self.total_frames) * 100
        return 0.0
