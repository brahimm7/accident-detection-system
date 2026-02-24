import os

# Define the path to the detector app
app_name = 'detector'
file_name = 'views.py'
folder_path = os.path.join(os.getcwd(), app_name)
file_path = os.path.join(folder_path, file_name)

# The content to write
content = """from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    return HttpResponse("Success! The Detector App is working.")
"""

# Check if the app folder exists
if not os.path.exists(folder_path):
    print(f"ERROR: The folder '{app_name}' does not exist.")
else:
    # Create the views.py file
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"SUCCESS: Created {file_path}")
    print("You can now run 'python manage.py makemigrations'")