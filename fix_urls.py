import os

# Define the path to the detector app
app_name = 'detector'
file_name = 'urls.py'
folder_path = os.path.join(os.getcwd(), app_name)
file_path = os.path.join(folder_path, file_name)

# The content to write
content = """from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
]
"""

# Check if the app folder exists
if not os.path.exists(folder_path):
    print(f"ERROR: The folder '{app_name}' does not exist next to manage.py.")
    print("Please verify the name of your app folder.")
else:
    # Create the urls.py file
    with open(file_path, 'w') as f:
        f.write(content)
    print(f"SUCCESS: Created {file_path}")
    print("You can now run 'python manage.py migrate'")