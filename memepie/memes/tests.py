from django.test import TestCase
from django.contrib.auth.models import User
from .models import Meme, Comment
from django.core.files.uploadedfile import SimpleUploadedFile

class MemeModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.other_user = User.objects.create_user(username='otheruser', password='password')
        
        # Mock image
        image_content = b'\x47\x49\x46\x20\x01'  # Minimal GIF
        self.image = SimpleUploadedFile('test.gif', image_content, content_type='image/gif')

    def test_meme_creation(self):
        meme = Meme.objects.create(
            author=self.user,
            image=self.image,
            caption="Testing meme"
        )
        self.assertEqual(meme.author.username, 'testuser')
        self.assertEqual(meme.caption, "Testing meme")
        self.assertEqual(str(meme), "testuser - Testing meme")

    def test_meme_likes(self):
        meme = Meme.objects.create(
            author=self.user,
            image=self.image,
            caption="Testing likes"
        )
        meme.faa_likes.add(self.user)
        meme.faa_likes.add(self.other_user)
        self.assertEqual(meme.total_faa_likes, 2)

    def test_comment_creation(self):
        meme = Meme.objects.create(
            author=self.user,
            image=self.image,
            caption="Testing comments"
        )
        comment = Comment.objects.create(
            meme=meme,
            author=self.other_user,
            content="Great meme!"
        )
        self.assertEqual(comment.author.username, 'otheruser')
        self.assertEqual(comment.meme, meme)
        self.assertEqual(comment.content, "Great meme!")
        self.assertIn("Comment by otheruser", str(comment))
