 # Adjust the import based on your app structure
from django.conf import settings
import os
import django

import sys

# Now you can import models and use Django functionality
from .models import User
from django.core.files.base import ContentFile
import base64
from profiles.models import Profile



# # Assuming your script is in the same directory as manage.py
# project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# sys.path.append(project_root)

# settings.configure(
#     DEBUG=True,
#     # Other settings...
# )
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'helios.settings')
# django.setup()

# use absolute path to the file


# Replace with your base64-encoded test image string
test_image_base64 = "iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAQAAADZc7J/AAAAmUlEQVR42mN0rgIFL+UH4B2BaJWGbCo6Z1Z9UbDlsDdWCipOhUKxR7lpoRqAdg9JFZhgHEFFAFTzwGYxmDPhBUmKHTqJUmACOfBRIJqAJoHwK2OoPIBkA2eAdwA5UIsErQgMhRirVsBdAIhJ6GtAqEKRaoGxQLtFIJpCkGVGGUZlSAqkwCqCcA0gMgigCjA3l7aDDKVAIlACkL0geawK6dDRc3pAJsKdQAAAABJRU5ErkJggg=="
_, str_img = test_image_base64.split(';base64')
decoded_file = base64.b64decode(str_img)

# Get or create a user
user, created = User.objects.get_or_create(username='test_user')

# Create or get the user's profile
profile, created = Profile.objects.get_or_create(user=user)

# Save the test image to the profile's photo field
profile.photo.save('test_image.png', ContentFile(decoded_file), save=True)
