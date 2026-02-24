from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, StreamingHttpResponse
from django.conf import settings
from django.core.files.base import ContentFile
from .models import VideoUpload
from .detector_utils import YOLOv8AccidentDetector
import os
import threading
from django.utils import timezone
import cv2
import time
import base64

def index(request):
    """Homepage with upload form"""
    videos = VideoUpload.objects.all()[:10]  # Last 10 videos
    return render(request, 'index.html', {'videos': videos})

def upload_video(request):
    """Handle video upload"""
    if request.method == 'POST' and request.FILES.get('video'):
        video_file = request.FILES['video']
        confidence = float(request.POST.get('confidence', 0.5))
        smoothing = int(request.POST.get('smoothing', 15))
        
        # Create database entry
        video_upload = VideoUpload.objects.create(
            video_file=video_file,
            confidence_threshold=confidence,
            smoothing_frames=smoothing,
            status='pending'
        )
        
        # Start processing in background thread
        thread = threading.Thread(
            target=process_video_background,
            args=(video_upload.id,)
        )
        thread.daemon = True
        thread.start()
        
        return redirect('video_detail', video_id=video_upload.id)
    
    return redirect('index')


# Global dictionaries to store processing state
processing_frames = {}  # video_id -> current frame image
processing_stats = {}   # video_id -> stats dict

def process_video_background(video_id):
    """Process video in background with live updates"""
    try:
        video_upload = VideoUpload.objects.get(id=video_id)
        video_upload.status = 'processing'
        video_upload.save()
        
        # Initialize processing state
        processing_stats[video_id] = {
            'current_frame': 0,
            'total_frames': 0,
            'accident_frames': 0,
            'fps': 0,
            'status': 'processing'
        }
        
        # Initialize detector
        model_path = settings.MODEL_PATH
        if not os.path.exists(model_path):
            raise Exception(f"Model not found at {model_path}")
        
        detector = YOLOv8AccidentDetector(
            model_path=str(model_path),
            conf_threshold=video_upload.confidence_threshold
        )
        
        # Process video with live updates
        input_path = video_upload.video_file.path
        output_filename = f"output_{os.path.basename(input_path)}"
        output_path = os.path.join(settings.MEDIA_ROOT, 'outputs', output_filename)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Process with live frame callback
        result = detector.detect_from_video_live(
            video_path=input_path,
            output_path=output_path,
            smoothing_frames=video_upload.smoothing_frames,
            frame_callback=lambda frame, stats: update_processing_state(video_id, frame, stats)
        )
        
        # Update database with results
        if result:
            output_video_path, accident_frames, detections = result
            
            video_upload.output_video.name = f"outputs/{output_filename}"
            video_upload.accident_frames = len(accident_frames)
            video_upload.total_frames = detector.last_frame_count
            video_upload.detection_rate = (len(accident_frames) / detector.last_frame_count * 100) if detector.last_frame_count > 0 else 0
            video_upload.processing_time = detector.last_processing_time
            video_upload.status = 'completed'
            video_upload.processed_at = timezone.now()
        else:
            raise Exception("Processing returned no result")
        
        # Mark as completed
        processing_stats[video_id]['status'] = 'completed'
        
    except Exception as e:
        video_upload.status = 'failed'
        video_upload.error_message = str(e)
        if video_id in processing_stats:
            processing_stats[video_id]['status'] = 'failed'
    
    video_upload.save()

def update_processing_state(video_id, frame, stats):
    """Update global processing state with current frame"""
    # Encode frame to JPEG
    ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    # Update processing frame
    processing_frames[video_id] = frame_base64
    
    # Update stats
    processing_stats[video_id].update(stats)

def get_processing_frame(request, video_id):
    """Get current processing frame"""
    if video_id in processing_frames:
        return JsonResponse({
            'success': True,
            'frame': processing_frames[video_id],
            'stats': processing_stats.get(video_id, {})
        })
    else:
        return JsonResponse({
            'success': False,
            'stats': processing_stats.get(video_id, {})
        })

def video_detail(request, video_id):
    """Show video processing status and results"""
    video = get_object_or_404(VideoUpload, id=video_id)
    return render(request, 'video_detail.html', {'video': video})

def video_status(request, video_id):
    """API endpoint for checking video processing status"""
    video = get_object_or_404(VideoUpload, id=video_id)
    
    data = {
        'status': video.status,
        'total_frames': video.total_frames,
        'accident_frames': video.accident_frames,
        'detection_rate': video.detection_rate,
        'processing_time': video.processing_time,
        'error_message': video.error_message,
    }
    
    if video.status == 'completed' and video.output_video:
        data['output_url'] = video.output_video.url
    
    return JsonResponse(data)

def delete_video(request, video_id):
    """Delete a video and its output"""
    video = get_object_or_404(VideoUpload, id=video_id)
    
    # Delete files safely
    try:
        if video.video_file:
            video_file_path = video.video_file.path
            if os.path.exists(video_file_path):
                os.remove(video_file_path)
    except Exception as e:
        print(f"Error deleting video file: {e}")
    
    try:
        if video.output_video:
            output_file_path = video.output_video.path
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
    except Exception as e:
        print(f"Error deleting output file: {e}")
    
    # Clean up processing state
    if video.id in processing_frames:
        del processing_frames[video.id]
    if video.id in processing_stats:
        del processing_stats[video.id]
    
    # Delete database entry
    video.delete()
    
    # Redirect to index
    return redirect('index')

def history(request):
    """Show all processed videos"""
    videos = VideoUpload.objects.all()
    return render(request, 'history.html', {'videos': videos})


# ============= REAL-TIME WEBCAM DETECTION =============

# Global webcam detector instance
webcam_detector = None
webcam_active = False

def realtime(request):
    """Real-time webcam detection page"""
    return render(request, 'realtime.html')

def start_webcam(request):
    """Start webcam detection"""
    global webcam_detector, webcam_active
    
    try:
        confidence = float(request.GET.get('confidence', 0.5))
        smoothing = int(request.GET.get('smoothing', 15))
        
        # Initialize detector if not already running
        if webcam_detector is None:
            model_path = settings.MODEL_PATH
            if not os.path.exists(model_path):
                return JsonResponse({'success': False, 'error': 'Model not found'})
            
            webcam_detector = YOLOv8AccidentDetector(
                model_path=str(model_path),
                conf_threshold=confidence
            )
            webcam_detector.smoothing_frames = smoothing
        
        webcam_active = True
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

def stop_webcam(request):
    """Stop webcam detection"""
    global webcam_active
    webcam_active = False
    return JsonResponse({'success': True})

def webcam_feed(request):
    """Video streaming generator function"""
    return StreamingHttpResponse(
        generate_frames(),
        content_type='multipart/x-mixed-replace; boundary=frame'
    )

def generate_frames():
    """Generate frames from webcam with accident detection"""
    global webcam_detector, webcam_active
    
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Set camera resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    
    active_boxes = []
    frame_count = 0
    fps_start_time = time.time()
    fps = 0
    
    try:
        while webcam_active:
            success, frame = cap.read()
            
            if not success:
                break
            
            frame_count += 1
            
            # Calculate FPS
            if frame_count % 10 == 0:
                fps = 10 / (time.time() - fps_start_time)
                fps_start_time = time.time()
            
            if webcam_detector is not None:
                # Run detection
                results = webcam_detector.model(frame, conf=webcam_detector.conf_threshold, verbose=False)
                detections = results[0].boxes
                
                # Update active boxes
                for box_info in active_boxes:
                    box_info['frames_remaining'] -= 1
                active_boxes = [b for b in active_boxes if b['frames_remaining'] > 0]
                
                # Process new detections
                smoothing_frames = getattr(webcam_detector, 'smoothing_frames', 15)
                for box in detections:
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    conf = float(box.conf[0])
                    cls = int(box.cls[0])
                    class_name = webcam_detector.model.names[cls]
                    
                    new_box = [x1, y1, x2, y2]
                    
                    # Check if overlaps with existing box
                    matched = False
                    for active_box in active_boxes:
                        if webcam_detector._calculate_iou(new_box, active_box['box']) > 0.3:
                            active_box['frames_remaining'] = smoothing_frames
                            active_box['confidence'] = max(active_box['confidence'], conf)
                            active_box['box'] = new_box
                            matched = True
                            break
                    
                    if not matched:
                        active_boxes.append({
                            'box': new_box,
                            'frames_remaining': smoothing_frames,
                            'confidence': conf,
                            'class': class_name
                        })
                
                # Draw detections
                accident_detected = len(active_boxes) > 0
                
                for box_info in active_boxes:
                    x1, y1, x2, y2 = box_info['box']
                    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                    
                    conf = box_info['confidence']
                    class_name = box_info['class']
                    
                    # RED for accidents
                    color = (0, 0, 255)
                    label = f"ACCIDENT: {conf:.2f}"
                    
                    # Draw rectangle
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 3)
                    
                    # Draw label
                    label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                    cv2.rectangle(frame, (x1, y1 - label_size[1] - 10), 
                                  (x1 + label_size[0], y1), color, -1)
                    cv2.putText(frame, label, (x1, y1 - 5), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                # Add status overlay
                status_color = (0, 0, 255) if accident_detected else (0, 255, 0)
                status_text = "ACCIDENT DETECTED!" if accident_detected else "Normal"
                
                # Semi-transparent background
                overlay = frame.copy()
                cv2.rectangle(overlay, (5, 5), (400, 80), (0, 0, 0), -1)
                frame = cv2.addWeighted(overlay, 0.3, frame, 0.7, 0)
                
                # Add text
                cv2.putText(frame, status_text, (10, 40), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
                cv2.putText(frame, f"FPS: {fps:.1f}", (10, 70), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Encode frame to JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # Yield frame in byte format
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    finally:
        cap.release()
