"""Tests for the Auth API endpoints"""


from django.test import override_settings
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.core import mail
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime, timedelta
import base64

from .base_test import BaseTestSetup


User = get_user_model()

LOGIN_URL = reverse("jwt-create")
REFRESH_URL = reverse("jwt-refresh")
REGISTER_URL = reverse("auth:user-list")
CREATE_USER_URL = reverse("auth:user-list")
PROTECTED_URL = reverse("fake_protected")
ACTIVATE_USER_URL = reverse("auth:user-activation")
PASSWORD_RESET_URL = reverse("auth:user-reset-password")
PASSWORD_RESET_CONFIRM_URL = reverse("auth:user-reset-password-confirm")
PASSWORD_SET_URL = reverse("auth:user-set-password")
DELETE_URL = reverse("auth:user-detail", kwargs={"id": 1})


class JWTAuthenticationTestCase(BaseTestSetup):
    def get_email_content(self):
        # Get the last sent email from the outbox
        email = mail.outbox[-1]

        # Retrieve the email content
        email_content = email.body  # This will give you the email body

        return email_content

    def extract_activation_reset_url(self, email_content):
        # You may need to use regular expressions or custom logic
        # to find the activation URL in the email content
        # Here, we assume that it starts with "http://" or "https://"
        url_start = email_content.find("http://") or \
            email_content.find("https://")

        if url_start != -1:
            url_end = email_content.find("\n", url_start)
            activation_url = email_content[url_start:url_end].strip()
            return activation_url

    def extract_activation_reset_token(self, activation_url):
        # Split the activation URL by forward slashes and get the last part
        url_parts = activation_url.split("/")
        activation_token = url_parts[-1]

        return activation_token

    def test_token_generation(self):
        self.active_user.refresh_from_db()
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_token_validation(self):
        # First, obtain a token by logging in
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]

        # Use the token to access a protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get(PROTECTED_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_token_expiry(self):
        # Note - I have checked that it is the expiration time
        # that is being checked, not the validity of the token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        valid_token = response.data["access"]
        expired_token = AccessToken(valid_token)
        expired_token["exp"] = datetime.utcnow() - timedelta(days=1)
        expired_token = str(expired_token)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {expired_token}")
        response = self.client.get(PROTECTED_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_token_refresh(self):
        # Step 1: Login to get the initial access and refresh token pair
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        refresh_token = response.data["refresh"]

        # Step 2: Use the refresh token to obtain a new access token
        refresh_payload = {"refresh": refresh_token}
        response = self.client.post(
            REFRESH_URL, refresh_payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        new_access_token = response.data["access"]

        # Optional: Use the new access token to access a protected view
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {new_access_token}"
            )
        response = self.client.get(PROTECTED_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_token(self):
        # Use an invalid token
        invalid_token = "this_is_an_invalid_token"

        # Try to access a protected endpoint with the invalid token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {invalid_token}")
        response = self.client.get(PROTECTED_URL)

        # The request should be unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_authentication(self):
        # Step 1: Login to get an access token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        access_token = response.data["access"]

        # Step 2: Use the access token to access a protected endpoint
        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
            )
        response = self.client.get(PROTECTED_URL)

        # The request should be successful
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_registration_duplicate_email(self):
        # First registration
        self.client.post(
            REGISTER_URL, self.inactive_payload, format="json"
            )

        # Attempt second registration with the same email
        response = self.client.post(
            REGISTER_URL, self.inactive_payload, format="json"
            )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Replace with the actual error message
        self.assertEqual(
            response.data["email"][0], "user with this email already exists."
        )

    def test_user_registration_invalid_data(self):
        """Test that user registration with invalid data fails."""
        invalid_payload = {
            "username": "",  # Empty username
            "email": "notanemail",  # Invalid email
            "password": "pw",  # Short password
            "re_password": "pw1",  # Mismatched password
        }
        response = self.client.post(CREATE_USER_URL, invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @override_settings(
            EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend"
            )
    def test_user_activation(self):
        """Test that user activation is successful."""
        # need a new user to test activation email
        login_payload = {
            "email": "newuser@example.com",
            "password": "Complex135@",
        }
        # Create an initial user (usually inactive by default)
        response = self.client.post(
            CREATE_USER_URL, login_payload, format="json"
            )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=login_payload["email"])

        email_content = self.get_email_content()
        activation_url = self.extract_activation_reset_url(email_content)

        # Parse the activation URL to extract the activation token
        activation_token = self.extract_activation_reset_token(activation_url)

        # Now, you have the activation token for testing
        self.assertIsNotNone(activation_token)

        uid = base64.urlsafe_b64encode(str(user.id).encode()).decode()
        # Activate the user
        activation_payload = {"uid": uid, "token": activation_token}
        response = self.client.post(
            ACTIVATE_USER_URL, activation_payload, format="json"
        )
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Verify that the user is now active
        user = get_user_model().objects.get(email=login_payload["email"])
        self.assertTrue(user.is_active)

    def test_user_activation_invalid_token(self):
        user = User.objects.create_user(
            email="emailfortestinginvalidtoken@example.com",
            password="Complex135@"
        )
        invalid_token = "this_is_an_invalid_token"
        uid = base64.urlsafe_b64encode(str(user.id).encode()).decode()
        activation_payload = {"uid": uid, "token": invalid_token}
        response = self.client.post(
            ACTIVATE_USER_URL, activation_payload, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertFalse(user.is_active)

    def test_user_password_reset_request(self):
        payload = {"email": self.active_user.email}

        # Make a POST request to the password reset endpoint
        response = self.client.post(PASSWORD_RESET_URL, payload, format="json")

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Check that an email was sent
        self.assertEqual(len(mail.outbox), 1)

        # Check that the email was sent to the correct user
        self.assertEqual(mail.outbox[0].to, [self.active_user.email])

    def test_user_password_reset_invalid_email(self):
        invalid_payload = {"email": "invalid-email"}

        # Make a POST request to the password resetendpoint
        # with an invalid email
        response = self.client.post(
            PASSWORD_RESET_URL, invalid_payload, format="json"
            )

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Check that no email was sent
        self.assertEqual(len(mail.outbox), 0)

    def test_user_password_reset(self):
        # Simulate a password reset request to get the token
        self.client.post(
            PASSWORD_RESET_URL,
            {"email": self.active_user.email}, format="json"
        )

        # Extract the reset token from the email content
        email_content = self.get_email_content()
        reset_url = self.extract_activation_reset_url(email_content)
        reset_token = self.extract_activation_reset_token(reset_url)

        self.assertIsNotNone(reset_token)  # Ensure the token exists

        # Prepare payload for password reset
        new_password = "NewComplex135@"
        uid = base64.urlsafe_b64encode(
            str(self.active_user.id).encode()
            ).decode()
        payload = {
            "uid": uid,
            "token": reset_token,
            "new_password": new_password,
            "re_new_password": new_password,
        }

        # Make a POST request to the password reset confirmation endpoint
        PASSWORD_RESET_CONFIRM_URL = reverse(
            "auth:user-reset-password-confirm"
            )
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL, payload, format="json"
            )

        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Verify that the password has been changed
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password(new_password))

    def test_user_password_reset_invalid_token(self):
        # Simulate a password reset request to get a valid token
        # (not going to use it)
        self.client.post(
            PASSWORD_RESET_URL,
            {"email": self.active_user.email}, format="json"
        )

        # Prepare payload for password reset with an invalid token
        new_password = "NewComplex135@"
        uid = base64.urlsafe_b64encode(
            str(self.active_user.id).encode()
            ).decode()
        invalid_token = "invalid_token_here"
        payload = {
            "uid": uid,
            "token": invalid_token,
            "new_password": new_password,
            "re_new_password": new_password,
        }

        # Make a POST request to the password reset confirmation endpoint
        PASSWORD_RESET_CONFIRM_URL = reverse(
            "auth:user-reset-password-confirm"
            )
        response = self.client.post(
            PASSWORD_RESET_CONFIRM_URL, payload, format="json"
            )

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the password has NOT been changed
        self.active_user.refresh_from_db()
        self.assertFalse(self.active_user.check_password(new_password))

    def test_user_password_change(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Prepare payload for password change
        old_password = self.active_payload["password"]
        new_password = "NewComplex135@"
        payload = {
            "current_password": old_password,
            "new_password": new_password,
            "re_new_password": new_password,
        }

        # Make a POST request to the password change endpoint
        response = self.client.post(PASSWORD_SET_URL, payload, format="json")

        # Check that the response status is 200 OK or 204 No Content
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Verify that the password has been changed
        self.active_user.refresh_from_db()
        self.assertTrue(self.active_user.check_password(new_password))

    def test_user_password_change_invalid_old_password(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Prepare payload for password change with an invalid current password
        invalid_current_password = "InvalidOldPassword"
        new_password = "NewComplex135@"
        payload = {
            "current_password": invalid_current_password,
            "new_password": new_password,
            "re_new_password": new_password,
        }

        # Make a POST request to the password change endpoint
        response = self.client.post(PASSWORD_SET_URL, payload, format="json")

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the password has NOT been changed
        self.active_user.refresh_from_db()
        self.assertFalse(self.active_user.check_password(new_password))

    def test_user_details_retrieval(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Make a GET request to the user details endpoint
        USER_DETAILS_URL = reverse(
            "auth:user-detail", kwargs={"id": self.active_user.id}
        )
        response = self.client.get(USER_DETAILS_URL, format="json")

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the returned user details are correct
        self.assertEqual(response.data["email"], self.active_user.email)

    def test_user_details_update_email_not_changeable(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Prepare new user details
        new_email = "newemail@example.com"
        payload = {"email": new_email}

        # Make a PATCH request to the user details endpoint
        USER_DETAILS_URL = reverse(
            "auth:user-detail", kwargs={"id": self.active_user.id}
        )
        response = self.client.patch(USER_DETAILS_URL, payload, format="json")

        # Check that the response status is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify that the email has NOT been changed
        self.active_user.refresh_from_db()
        self.assertNotEqual(self.active_user.email, new_email)
        self.assertEqual(self.active_user.email, self.active_payload["email"])

    def test_user_details_update_name(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Prepare new user details
        new_name = "New Name"
        payload = {"name": new_name}

        # Make a PATCH request to the user details endpoint
        USER_DETAILS_URL = reverse(
            "auth:user-detail", kwargs={"id": self.active_user.id}
        )
        response = self.client.patch(USER_DETAILS_URL, payload, format="json")

        # Check that the response status is 200 OK or 204 No Content
        self.assertIn(
            response.status_code,
            [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        )

        # Verify that the name has been changed
        self.active_user.refresh_from_db()
        self.assertEqual(self.active_user.name, new_name)

    def test_user_details_update_invalid_data(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Store the original name for comparison
        original_name = self.active_user.name

        # Prepare invalid user details
        # Using a dictionary instead of a string
        invalid_name = {"invalid": "data"}
        payload = {"name": invalid_name}
        # note - using an int for ex won't work,
        # the serializer converts it to a string

        # Make a PATCH request to the user details endpoint
        USER_DETAILS_URL = reverse(
            "auth:user-detail", kwargs={"id": self.active_user.id}
        )
        response = self.client.patch(USER_DETAILS_URL, payload, format="json")

        # Check that the response status is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Verify that the name has NOT been changed
        self.active_user.refresh_from_db()
        self.assertEqual(self.active_user.name, original_name)

    def test_user_deletion(self):
        # Log in to get an authentication token
        response = self.client.post(
            LOGIN_URL, self.active_payload, format="json"
            )
        token = response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

        # Prepare the payload with the current password
        payload = {"current_password": self.active_payload["password"]}

        # Make a DELETE request to the user details endpoint
        DELETE_URL = reverse(
            "auth:user-detail", kwargs={"id": self.active_user.id}
            )
        response = self.client.delete(DELETE_URL, data=payload)

        # Check that the response status is 204 No Content or 200 OK
        self.assertIn(
            response.status_code,
            [status.HTTP_204_NO_CONTENT, status.HTTP_200_OK]
        )

        # Verify that the user has been deleted
        with self.assertRaises(User.DoesNotExist):
            self.active_user.refresh_from_db()

    def test_user_deletion_unauthenticated(self):
        response = self.client.delete(DELETE_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
