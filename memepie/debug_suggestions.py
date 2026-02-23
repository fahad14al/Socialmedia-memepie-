import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'memepie.settings')
django.setup()

from django.contrib.auth.models import User
from memes.models import Follow, Meme
from memes.views import get_smart_suggestions
from django.core.files.uploadedfile import SimpleUploadedFile

def debug_suggestions():
    try:
        User.objects.all().delete()
        user1 = User.objects.create_user(username='u1', password='p')
        user2 = User.objects.create_user(username='u2', password='p')
        user3 = User.objects.create_user(username='u3', password='p')
        
        Follow.objects.create(follower=user1, following=user2)
        Follow.objects.create(follower=user2, following=user3)
        
        print("Testing mutual follows...")
        suggestions = get_smart_suggestions(user1)
        print(f"Suggestions for u1: {[u.username for u in suggestions]}")
        
        print("Success!")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_suggestions()
