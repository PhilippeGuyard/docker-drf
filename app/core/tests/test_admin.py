from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse


class AdminSiteTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            password='password123',
            name='Test user full name'
        )

    def test_users_listed(self):
        """Test that users are listed on user page."""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_user_change_page(self):
        """Test that the user edit page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        """Test that the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user(self):
        """Test creating a new user through admin site."""
        url = reverse('admin:core_user_add')
        payload = {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'name': 'New User',
        }
        self.client.post(url, payload)

        # Check if the new user is listed on user page
        user_list_url = reverse('admin:core_user_changelist')
        user_list_res = self.client.get(user_list_url)

        self.assertContains(user_list_res, 'newuser@example.com')
        self.assertContains(user_list_res, 'New User')
