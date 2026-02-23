from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Meme, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

class CommentExtendedTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client.login(username='user1', password='password')
        
        image_content = b'\x47\x49\x46\x20\x01'
        image = SimpleUploadedFile('test.gif', image_content, content_type='image/gif')
        self.meme = Meme.objects.create(author=self.user, image=image, caption="Test Meme")

    def test_add_comment_top_level(self):
        url = reverse('add_comment', args=[self.meme.id])
        response = self.client.post(url, {'content': 'Top level comment'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(data['is_reply'])
        self.assertEqual(Comment.objects.count(), 1)

    def test_add_reply(self):
        parent = Comment.objects.create(meme=self.meme, author=self.user, content="Parent")
        url = reverse('add_comment', args=[self.meme.id])
        response = self.client.post(url, {'content': 'Reply', 'parent_id': parent.id}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(data['is_reply'])
        self.assertEqual(data['parent_id'], parent.id)
        
        reply = Comment.objects.get(id=data['comment_id'])
        self.assertEqual(reply.parent, parent)

    def test_like_comment(self):
        comment = Comment.objects.create(meme=self.meme, author=self.user, content="Comment to like")
        url = reverse('like_comment', args=[comment.id])
        
        # Like
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertTrue(data['liked'])
        self.assertEqual(data['total_likes'], 1)
        self.assertEqual(comment.likes.count(), 1)
        
        # Unlike
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertFalse(data['liked'])
        self.assertEqual(data['total_likes'], 0)
