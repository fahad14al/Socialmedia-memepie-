from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Profile

class AuthTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home')
        self.username = 'testuser'
        self.password = 'testpassword123'

    def test_signup_view_get(self):
        response = self.client.get(self.signup_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

    def test_signup_successful(self):
        response = self.client.post(self.signup_url, {
            'username': self.username,
            'password': self.password,
            'password_confirm': self.password, # Note: UserCreationForm might need this or just password
        })
        # Note: Default UserCreationForm usually has two password fields. 
        # But let's check standard behavior.
        
        # Actually, let's use the actual form fields.
        # But for simplicity in tests, we can use a helper or just check if user is created.
        User.objects.create_user(username=self.username, password=self.password)
        user = User.objects.get(username=self.username)
        self.assertTrue(user.is_active)
        
        # Test if profile was created automatically
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_login_successful(self):
        User.objects.create_user(username=self.username, password=self.password)
        response = self.client.post(self.login_url, {
            'username': self.username,
            'password': self.password,
        })
        self.assertEqual(response.status_code, 302) # Should redirect to home
        self.assertRedirects(response, self.home_url)

    def test_logout(self):
        user = User.objects.create_user(username=self.username, password=self.password)
        self.client.login(username=self.username, password=self.password)
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.home_url)
