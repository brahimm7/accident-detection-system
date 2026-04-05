# Accident Detection System

A Django-based web application that uses YOLOv8 to detect car accidents in videos with real-time processing capabilities and live webcam detection.

## Features

- **Video Upload & Processing** - Upload videos and get accident detection results
- **Real-Time Detection** - Live webcam accident detection
- **Live Processing Preview** - Watch videos being processed in real-time
- **Detection History** - View all previously processed videos
- **Adjustable Settings** - Configure detection sensitivity and smoothing
- **Temporal Smoothing** - Stable detections without flickering
- **Clean UI** - Simple, professional interface

## Screenshots

<!-- Add screenshots here after deployment -->

## Tech Stack

- **Backend:** Django 4.2+
- **ML Model:** YOLOv8 (Ultralytics)
- **Computer Vision:** OpenCV
- **Frontend:** Bootstrap 5, HTML5, CSS3, JavaScript
- **Database:** SQLite (development) / PostgreSQL (production ready)

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Webcam (optional, for real-time detection)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/accident-detection-system.git
cd accident-detection-system
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Add Your Model

Place your trained YOLOv8 model file in the `models/` directory:

```bash
mkdir models
# Copy your best.pt file to models/
```

### 5. Setup Database

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User (Optional)

```bash
python manage.py createsuperuser
```

### 7. Run the Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

## Usage

### Upload Video for Detection

1. Navigate to the home page
2. Drag and drop a video or click "Choose File"
3. Adjust detection settings (optional)
4. Click "Start Detection"
5. Watch the live processing preview
6. View results and download the processed video

### Real-Time Webcam Detection

1. Click "Real-Time" in the navigation
2. Adjust settings as needed
3. Click "Start Webcam"
4. Point camera at traffic or test scenarios
5. Red boxes will appear around detected accidents

## Project Structure

```
accident-detection-system/
├── accident_detector/          # Django project settings
├── detector/                   # Main application
├── templates/                  # HTML templates
├── media/                      # Uploaded and processed videos
├── models/                     # YOLOv8 model files
├── manage.py
├── requirements.txt
└── README.md
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


Made for road safety
