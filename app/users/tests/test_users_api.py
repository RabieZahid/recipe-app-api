"""
Tests for the users API.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('users:create')
CREATE_USER_TOKEN_URL = reverse('users:token')


def create_user(**params):
    """Create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUseApiTests(TestCase):
    """Test the public features of the API."""

    def setUp(self):
        self.client = APIClient()

    def test_create_user_success(self):
        """Test creating user is successful."""
        payload = {
            'email': "test@example.com",
            'password': 'Testpass123',
            'name': 'Test Name',
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_email_exists_error(self):
        """Test error return if user with email already exists"""
        payload = {
            'email': "test@example.com",
            'password': 'Testpass123',
            'name': 'Test Name',
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test an error is returned if password less than 5 chars."""
        payload = {
            'email': "test@example.com",
            'password': 'pwd',
            'name': 'Test Name',
        }
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test generates token for valid credentials."""
        user_details = {
            'email': "test@example.com",
            'password': 'Testpass123',
            'name': 'Test Name',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['email'],
            'password': user_details['password']
        }
        res = self.client.post(CREATE_USER_TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_bad_credentials(self):
        """Fails to login with invalid credentials."""
        user_details = {
            'email': "test@example.com",
            'password': 'Testpass123',
            'name': 'Test Name',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['email'],
            'password': 'BadPassword123'
        }
        res = self.client.post(CREATE_USER_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_blank_password(self):
        """Fails to login with empty password"""
        user_details = {
            'email': "test@example.com",
            'password': 'Testpass123',
            'name': 'Test Name',
        }
        create_user(**user_details)

        payload = {
            'username': user_details['email'],
            'password': ''
        }
        res = self.client.post(CREATE_USER_TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
