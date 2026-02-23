from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Follow, Notification
from django.urls import reverse

class FollowSystemTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1', password='password')
        self.user2 = User.objects.create_user(username='user2', password='password')
        self.client.login(username='user1', password='password')

    def test_follow_user(self):
        url = reverse('toggle_follow', args=[self.user2.username])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['action'], 'followed')
        self.assertEqual(data['followers_count'], 1)
        self.assertTrue(Follow.objects.filter(follower=self.user1, following=self.user2).exists())
        
        # Check notification
        notif = Notification.objects.filter(recipient=self.user2, notification_type='follow').first()
        self.assertIsNotNone(notif)
        self.assertEqual(notif.sender, self.user1)

    def test_unfollow_user(self):
        Follow.objects.create(follower=self.user1, following=self.user2)
        url = reverse('toggle_follow', args=[self.user2.username])
        response = self.client.get(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        data = response.json()
        self.assertEqual(data['action'], 'unfollowed')
        self.assertEqual(data['followers_count'], 0)
        self.assertFalse(Follow.objects.filter(follower=self.user1, following=self.user2).exists())

    def test_followers_list(self):
        Follow.objects.create(follower=self.user2, following=self.user1)
        url = reverse('get_followers', args=[self.user1.username])
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(len(data['users']), 1)
        self.assertEqual(data['users'][0]['username'], 'user2')

    def test_suggestions_not_following(self):
        user3 = User.objects.create_user(username='user3', password='password')
        # user1 follows user2, should suggest user3 but not user2
        Follow.objects.create(follower=self.user1, following=self.user2)
        
        url = reverse('home')
        response = self.client.get(url)
        suggested_users = response.context['suggested_users']
        
        self.assertIn(user3, suggested_users)
        self.assertNotIn(self.user2, suggested_users)
        self.assertNotIn(self.user1, suggested_users)
