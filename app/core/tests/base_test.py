""" Base test for auth testing
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

User = get_user_model()


def create_user(**params):
    """Helper function to create a new user."""
    return get_user_model().objects.create_user(**params)


class BaseTestSetup(TestCase):
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        self.active_payload = {
            'email': 'active@example.com',
            'password': 'Complex135@',
            'name': 'Active User',
        }
        self.inactive_payload = {
            'email': 'inactive@example.com',
            'password': 'Complex135@',
            'name': 'Inactive User',
        }
        self.active_user = User.objects.create_user(
            email=self.active_payload['email'],
            password=self.active_payload['password'],
            name=self.active_payload['name'],
        )
        self.active_user.is_active = True
        self.active_user.save()
        self.active_user.refresh_from_db()
        self.inactive_user = User.objects.create_user(
            email=self.inactive_payload['email'],
            password=self.inactive_payload['password'],
            name=self.inactive_payload['name'],
            is_active=False
        )
