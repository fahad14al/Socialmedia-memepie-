from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Follow, Meme
from .views import get_smart_suggestions
from django.core.files.uploadedfile import SimpleUploadedFile

class SmartSuggestionsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.user3 = User.objects.create_user(username='user3', password='password')
        self.user4 = User.objects.create_user(username='user4', password='password')
        
    def test_mutual_follows(self):
        # User1 follows User2, User2 follows User3. User3 should be suggested to User1.
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.create(follower=self.user2, following=self.user3)
        
        suggestions = get_smart_suggestions(self.user1)
        self.assertIn(self.user3, suggestions)
        self.assertNotIn(self.user2, suggestions)
        self.assertNotIn(self.user1, suggestions)

    def test_shared_interests(self):
        # User1 and User4 like the same meme. User4 should be suggested to User1.
        image = SimpleUploadedFile('test.gif', b'\x47\x49\x46\x20\x01', content_type='image/gif')
        meme = Meme.objects.create(author=self.user2, image=image, caption="Shared Meme")
        
        meme.faa_likes.add(self.user1)
        meme.faa_likes.add(self.user4)
        
        suggestions = get_smart_suggestions(self.user1)
        self.assertIn(self.user4, suggestions)
        self.assertNotIn(self.user1, suggestions)
