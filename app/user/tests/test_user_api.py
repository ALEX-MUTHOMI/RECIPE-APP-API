"""
Tests for the user API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model  # Fixed 'conrib'
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
TOKEN_URL = reverse("user:token")

def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicUserApiTests(TestCase):
    """Test the public features of the user API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test Creating User is Successful."""
        payload = {
            "email": "test@example.com",  # Fixed email format
            "password": "testpass123",    # Fixed missing colon & comma
            "name": "Test Name",          # Fixed missing colon
        }
        # ACT: Send the data
        res = self.client.post(CREATE_USER_URL, payload)

        # ASSERT: Check the result
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload["email"])
        self.assertTrue(user.check_password(payload["password"])) # Fixed missing dot
        self.assertNotIn("password", res.data)

    def test_user_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        payload = {
            "email": "test@example.com",
            "password": "testpass123",
            "name": "Test Name",
        }
        # Create the user ONCE directly in the DB
        create_user(**payload)

        # Try to create the SAME user again via API
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password is too short."""
        payload = {
            "email": "test@example.com",
            "password": "pw",  # Too short
            "name": "Test Name",
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload["email"]
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """
        Test generates token for valid credentials.
        """
        user_details = {
            "name": "Test Name",
            "email": "test@example.com",
            "password": "test-user-password123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],

        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

def test_create_token_bad_credentials(self):
        """
        Test returns error if credentials are invalid.
        """
        create_user(
            email="test@example.com",
            password="goodpass"
        )

        payload = {
            "email": "test@example.com",
            "password": "badpass",
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn("token", res.data)
        # FIX 1: Removed "token" from this line
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

def test_create_token_blank_password(self):
        """
        Test returns error if password is blank.
        """
        payload = {
            "email": "test@example.com",
            "password": "",
        }
        res = self.client.post(TOKEN_URL, payload)

        # FIX 2: Fixed indentation here
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)