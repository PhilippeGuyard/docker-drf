"""
Tests for the models of the core app.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model


class ModelTests(TestCase):
    """Tests for the core app models."""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'test@example.com'
        password = 'testpass123'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_create_user(self):
        """Test creating a new user with email"""
        User = get_user_model()
        password = 'testpass123'
        user = User.objects.create_user(
            email='test@example.com',
            password=password
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password(password))
        self.assertFalse(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a new superuser with email"""
        User = get_user_model()
        admin_user = User.objects.create_superuser(
            email='superadmin@example.com',
            password='testpass123'
        )
        self.assertEqual(admin_user.email, 'superadmin@example.com')
        self.assertTrue(admin_user.is_active)
        self.assertTrue(admin_user.is_staff)
        self.assertTrue(admin_user.is_superuser)

    def test_email_normalized(self):
        """Test the email for a new user is normalized"""
        sample_emails = [
            ['test1@EXAMPLE.COM', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
        ]
        for email, expected in sample_emails:
            User = get_user_model()
            user = User.objects.create_user(
                email=email, password='testpass123')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        """Test creating user without email raises ValueError"""
        User = get_user_model()
        with self.assertRaises(ValueError):
            User.objects.create_user(email='', password='testpass123')
        with self.assertRaises(ValueError):
            User.objects.create_user(email=None, password='testpass123')
