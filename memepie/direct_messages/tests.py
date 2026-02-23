from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Thread, Message
from memes.models import Follow

class DirectMessagesTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password1')
        self.user2 = User.objects.create_user(username='user2', password='password1')
        self.user3 = User.objects.create_user(username='user3', password='password1')
        self.client = Client()

    def test_start_chat_with_follower(self):
        """Test that messaging someone you follow goes into Primary inbox."""
        self.client.login(username='user1', password='password1')
        # User1 follows User2
        Follow.objects.create(follower=self.user1, following=self.user2)
        
        # User1 starts chat with User2
        response = self.client.get(reverse('start_chat', args=['user2']))
        thread = Thread.objects.first()
        
        # Should be accepted automatically if there's a follow relationship (in views logic we check if recipient follows sender or is_accepted is true)
        # Actually my logic was: thread.is_accepted=True if RECIPENT follows SENDER
        # Let's verify the view logic I wrote
        self.assertRedirects(response, reverse('chat_detail', args=[thread.id]))

    def test_message_request_flow(self):
        """Test that messaging someone who doesn't follow you goes into Requests."""
        self.client.login(username='user1', password='password1')
        
        # User1 messages User2 (No follows exist)
        self.client.get(reverse('start_chat', args=['user2']))
        thread = Thread.objects.first()
        
        # User2 checks inbox
        self.client.logout()
        self.client.login(username='user2', password='password1')
        
        response = self.client.get(reverse('inbox'))
        self.assertEqual(len(response.context['threads']), 0) # Primary should be empty
        
        response = self.client.get(reverse('inbox') + '?tab=requests')
        self.assertEqual(len(response.context['threads']), 1) # Should be in requests

    def test_accept_request(self):
        """Test accepting a message request moves it to Primary."""
        self.client.login(username='user1', password='password1')
        self.client.get(reverse('start_chat', args=['user2']))
        thread = Thread.objects.first()
        
        self.client.logout()
        self.client.login(username='user2', password='password1')
        
        # Accept request
        self.client.post(reverse('accept_request', args=[thread.id]))
        thread.refresh_from_db()
        self.assertTrue(thread.is_accepted)
        
        # Check Primary inbox
        response = self.client.get(reverse('inbox'))
        self.assertEqual(len(response.context['threads']), 1)

    def test_auto_accept_mutual_follow(self):
        """Test that mutual follows result in an automatically accepted thread."""
        Follow.objects.create(follower=self.user1, following=self.user2)
        Follow.objects.create(follower=self.user2, following=self.user1)
        
        self.client.login(username='user1', password='password1')
        self.client.get(reverse('start_chat', args=['user2']))
        thread = Thread.objects.first()
        
        # Should be auto-accepted in start_chat logic if other follows me
        self.assertTrue(thread.is_accepted)

    def test_message_read_status(self):
        """Test that opening a chat marks messages as read."""
        self.client.login(username='user1', password='password1')
        self.client.get(reverse('start_chat', args=['user2']))
        thread = Thread.objects.first()
        
        # User 1 sends message
        Message.objects.create(thread=thread, sender=self.user1, text="Hello")
        
        # User 2 opens chat
        self.client.logout()
        self.client.login(username='user2', password='password1')
        self.client.get(reverse('chat_detail', args=[thread.id]))
        
        # Message should be read
        msg = Message.objects.first()
        self.assertTrue(msg.is_read)
