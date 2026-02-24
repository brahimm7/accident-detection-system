from ultralytics import YOLO
import cv2
import numpy as np
import time

class YOLOv8AccidentDetector:
    def __init__(self, model_path, conf_threshold=0.5):
        """
        Initialize YOLOv8 accident detector
        
        Args:
            model_path: Path to YOLOv8 .pt model file
            conf_threshold: Confidence threshold (0-1)
        """
        self.model = YOLO(model_path)
        self.conf_threshold = conf_threshold
        self.last_frame_count = 0
        self.last_processing_time = 0.0
        
    def detect_from_video_live(self, video_path, output_path='output.mp4', 
                               smoothing_frames=15, iou_threshold=0.3, frame_callback=None):
        """
        Detect accidents in video file with live frame updates
        
        Args:
            video_path: Path to input video
            output_path: Path to save output video
            smoothing_frames: Number of frames to keep detection active
            iou_threshold: IoU threshold for matching boxes across frames
            frame_callback: Callback function(frame, stats) called for each processed frame
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return None
        
        # Get video properties
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Setup video writer
        fourcc = cv2.VideoWriter_fourcc(*'avc1')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        accident_frames = []
        accident_detections = []
        active_boxes = []
        
        start_time = time.time()
        fps_start = time.time()
        processing_fps = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Calculate processing FPS
            if frame_count % 10 == 0:
                processing_fps = 10 / (time.time() - fps_start)
                fps_start = time.time()
            
            # Run YOLOv8 detection
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            detections = results[0].boxes
            
            # Update active boxes
            for box_info in active_boxes:
                box_info['frames_remaining'] -= 1
            active_boxes = [b for b in active_boxes if b['frames_remaining'] > 0]
            
            # Process new detections
            for box in detections:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                class_name = self.model.names[cls]
                
                new_box = [x1, y1, x2, y2]
                
                # Check if overlaps with existing box
                matched = False
                for active_box in active_boxes:
                    if self._calculate_iou(new_box, active_box['box']) > iou_threshold:
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
            
            accident_detected = len(active_boxes) > 0
            
            if accident_detected:
                accident_frames.append(frame_count)
                for box_info in active_boxes:
                    accident_detections.append({
                        'frame': frame_count,
                        'confidence': box_info['confidence'],
                        'class': box_info['class']
                    })
            
            # Draw detections
            annotated_frame = frame.copy()
            
            for box_info in active_boxes:
                x1, y1, x2, y2 = box_info['box']
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                
                conf = box_info['confidence']
                class_name = box_info['class']
                
                color = (0, 0, 255)  # RED
                label = f"ACCIDENT: {class_name} {conf:.2f}"
                
                cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
                
                label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
                cv2.rectangle(annotated_frame, (x1, y1 - label_size[1] - 10), 
                              (x1 + label_size[0], y1), color, -1)
                
                cv2.putText(annotated_frame, label, (x1, y1 - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Add status overlay
            status_color = (0, 0, 255) if accident_detected else (0, 255, 0)
            status_text = "⚠️ ACCIDENT DETECTED" if accident_detected else "✓ Normal"
            
            overlay = annotated_frame.copy()
            cv2.rectangle(overlay, (5, 5), (450, 120), (0, 0, 0), -1)
            annotated_frame = cv2.addWeighted(overlay, 0.3, annotated_frame, 0.7, 0)
            
            cv2.putText(annotated_frame, f"Frame: {frame_count}/{total_frames}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(annotated_frame, status_text, 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, status_color, 2)
            cv2.putText(annotated_frame, f"FPS: {processing_fps:.1f}", 
                       (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Write frame
            out.write(annotated_frame)
            
            # Call frame callback for live updates
            if frame_callback and frame_count % 2 == 0:  # Update every 2 frames to reduce load
                stats = {
                    'current_frame': frame_count,
                    'total_frames': total_frames,
                    'accident_frames': len(accident_frames),
                    'fps': processing_fps,
                    'status': 'processing',
                    'progress': (frame_count / total_frames) * 100
                }
                frame_callback(annotated_frame, stats)
        
        cap.release()
        out.release()
        
        self.last_frame_count = frame_count
        self.last_processing_time = time.time() - start_time
        
        return output_path, accident_frames, accident_detections
    
    def detect_from_video(self, video_path, output_path='output.mp4', 
                         show_progress=False, smoothing_frames=15, iou_threshold=0.3):
        """
        Detect accidents in video file with temporal smoothing (backward compatibility)
        """
        return self.detect_from_video_live(video_path, output_path, smoothing_frames, iou_threshold)
    
    def _calculate_iou(self, box1, box2):
        """Calculate Intersection over Union (IoU) between two boxes"""
        x1_min, y1_min, x1_max, y1_max = box1
        x2_min, y2_min, x2_max, y2_max = box2
        
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return 0.0
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        box1_area = (x1_max - x1_min) * (y1_max - y1_min)
        box2_area = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = box1_area + box2_area - inter_area
        
        return inter_area / union_area if union_area > 0 else 0.0
