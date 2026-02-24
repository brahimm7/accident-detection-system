# GitHub Setup Guide

Complete step-by-step guide to publish your Accident Detection System on GitHub.

## Prerequisites

1. GitHub account - [Sign up here](https://github.com/join) if you don't have one
2. Git installed on your computer - [Download Git](https://git-scm.com/downloads)

---

## Step 1: Prepare Your Project

### 1.1 Clean Up Your Project Directory

Remove these files/folders (they shouldn't be on GitHub):
```
db.sqlite3
media/uploads/* (keep the folder, delete contents)
media/outputs/* (keep the folder, delete contents)
models/best.pt (too large - users will add their own)
__pycache__/ (all of them)
*.pyc files
venv/ or env/ (virtual environment)
```

### 1.2 Add Required Files

Copy these files from the ZIP to your project root:
- README_github.md → rename to README.md
- .gitignore
- LICENSE
- requirements_github.txt → rename to requirements.txt
- CONTRIBUTING.md

### 1.3 Create .gitkeep Files

```bash
# Windows (PowerShell)
New-Item -Path media\uploads\.gitkeep -ItemType File
New-Item -Path media\outputs\.gitkeep -ItemType File
New-Item -Path models\.gitkeep -ItemType File

# macOS/Linux
touch media/uploads/.gitkeep
touch media/outputs/.gitkeep
touch models/.gitkeep
```

---

## Step 2: Initialize Git (First Time Only)

Open terminal/command prompt in your project folder:

```bash
# Configure Git (first time only)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Initialize repository
git init
```

---

## Step 3: Create Repository on GitHub

1. Go to https://github.com/new
2. Fill in:
   - **Repository name:** accident-detection-system
   - **Description:** Django web app for car accident detection using YOLOv8
   - **Visibility:** Public (or Private if you prefer)
   - **DO NOT** check "Add README" (you already have one)
3. Click "Create repository"

---

## Step 4: Push Your Code to GitHub

Copy the commands from GitHub (they look like this):

```bash
git remote add origin https://github.com/yourusername/accident-detection-system.git
git branch -M main
git push -u origin main
```

But first, let's add and commit your files:

```bash
# Add all files
git add .

# Commit
git commit -m "Initial commit: Accident Detection System with YOLOv8"

# Add remote (replace 'yourusername' with your actual GitHub username)
git remote add origin https://github.com/yourusername/accident-detection-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

**If asked for credentials:**
- Username: Your GitHub username
- Password: Use a Personal Access Token (not your GitHub password)
  - Get token: GitHub → Settings → Developer settings → Personal access tokens → Generate new token

---

## Step 5: Add Description and Topics

On your GitHub repository page:

1. Click "Add description" and paste:
   ```
   Django web application for car accident detection using YOLOv8 with real-time processing and live webcam detection
   ```

2. Click "Add topics" and add:
   ```
   django
   yolov8
   accident-detection
   computer-vision
   opencv
   deep-learning
   real-time-detection
   python
   machine-learning
   video-processing
   ```

---

## Step 6: Create a Good README (Optional Enhancement)

Add screenshots to your README:

1. Take screenshots of:
   - Upload page
   - Processing page (with live preview)
   - Results page
   - Real-time detection

2. Upload to GitHub:
   - Create folder: `screenshots/`
   - Upload images there

3. Add to README.md:
   ```markdown
   ## Screenshots
   
   ### Upload Interface
   ![Upload](screenshots/upload.png)
   
   ### Live Processing
   ![Processing](screenshots/processing.png)
   
   ### Results
   ![Results](screenshots/results.png)
   ```

---

## Step 7: Add a Demo Video (Optional)

1. Record a short demo (30-60 seconds)
2. Upload to YouTube
3. Add to README:
   ```markdown
   ## Demo Video
   
   [![Demo Video](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)
   ```

---

## Step 8: Making Future Updates

When you make changes to your code:

```bash
# See what changed
git status

# Add changes
git add .

# Commit with message
git commit -m "Description of what you changed"

# Push to GitHub
git push
```

---

## Common Git Commands

```bash
# Check status
git status

# See commit history
git log

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Pull latest changes
git pull

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard all changes
git reset --hard
```

---

## Troubleshooting

### "Permission denied"
- Use Personal Access Token instead of password
- Generate at: GitHub → Settings → Developer settings → Personal access tokens

### "Large files"
- GitHub has 100MB file limit
- Your model file (best.pt) should NOT be pushed
- Check .gitignore includes `models/*.pt`

### "Already exists"
```bash
git remote remove origin
git remote add origin https://github.com/yourusername/accident-detection-system.git
```

---

## Making Your Repo Attractive

### Add Badges (Optional)

Add to top of README:

```markdown
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-4.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
```

### Add GitHub Stats

Enable in Settings → Features:
- Issues
- Discussions (optional)
- Projects (optional)

---

## Next Steps

1. Star your own repo (to show support!)
2. Share the link with others
3. Add it to your resume/portfolio
4. Consider adding:
   - GitHub Actions for CI/CD
   - Docker support
   - API documentation
   - More test coverage

---

## Your Repository Link

After setup, your repo will be at:
```
https://github.com/yourusername/accident-detection-system
```

Share this link on:
- LinkedIn
- Resume
- Portfolio website
- Twitter/X

---

Congratulations! Your project is now on GitHub! 🎉
