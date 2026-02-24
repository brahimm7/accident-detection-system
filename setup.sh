#!/bin/bash

echo "🚗 Car Accident Detection Web App Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create models directory
echo ""
echo "Creating models directory..."
mkdir -p models
echo "⚠️  IMPORTANT: Copy your YOLOv8 model file to: models/best.pt"

# Create media directories
echo ""
echo "Creating media directories..."
mkdir -p media/uploads
mkdir -p media/outputs

# Run migrations
echo ""
echo "Setting up database..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
echo "Do you want to create an admin user? (y/n)"
read -r create_admin

if [ "$create_admin" = "y" ]; then
    python manage.py createsuperuser
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your model file: cp /path/to/best.pt models/best.pt"
echo "2. Start the server: python manage.py runserver"
echo "3. Open browser: http://127.0.0.1:8000/"
echo ""
echo "🎉 Enjoy your accident detection app!"
