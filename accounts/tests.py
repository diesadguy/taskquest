from django.test import TestCase
from django.contrib.auth.models import User

from .models import Profile


class AccountsTests(TestCase):
    def test_profile_created_after_user_creation(self):
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123'
        )

        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_register_view_creates_user(self):
        response = self.client.post('/accounts/register/', {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'StrongPassword123',
            'password2': 'StrongPassword123',
        })

        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())
        self.assertTrue(Profile.objects.filter(user__username='newuser').exists())