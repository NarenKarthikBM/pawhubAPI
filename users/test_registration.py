"""
Test file for User Registration API

This test demonstrates the user registration functionality
without OTP verification as requested.

API Endpoint: POST /api/users/register/

Example Usage:
```python
import requests

# Registration data
data = {
    "email": "test@example.com",
    "password": "securepassword123",
    "username": "testuser",
    "name": "Test User"
}

# Make registration request
response = requests.post("http://localhost:8000/api/users/register/", json=data)

if response.status_code == 201:
    result = response.json()
    print("Registration successful!")
    print(f"Auth Token: {result['tokens']['auth_token']}")
    print(f"User Details: {result['user_details']}")
else:
    print(f"Registration failed: {response.json()}")
```

Expected Response (Success - 201):
{
    "tokens": {
        "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "device_token": "device_abc123"
    },
    "user_details": {
        "id": 1,
        "name": "Test User",
        "email": "test@example.com",
        "username": "testuser",
        "is_active": true,
        "is_staff": false,
        "is_superuser": false,
        "date_joined": "2025-08-23T10:30:00Z"
    }
}

Expected Response (Error - 400):
{
    "error": "User with this email already exists",
    "field": "email"
}

Validation Rules:
- Email: Must be valid email format with @ symbol
- Password: Minimum 8 characters, maximum 100 characters
- Username: 3-20 characters, must be unique
- Name: 1-50 characters, required
"""

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import CustomUser


class UserRegistrationAPITest(TestCase):
    """Test cases for User Registration API"""

    def setUp(self):
        self.client = APIClient()
        self.registration_url = reverse("user-registration")
        self.valid_data = {
            "email": "test@example.com",
            "password": "securepassword123",
            "username": "testuser",
            "name": "Test User",
        }

    def test_successful_registration(self):
        """Test successful user registration"""
        response = self.client.post(
            self.registration_url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("tokens", response.data)
        self.assertIn("user_details", response.data)
        self.assertIn("auth_token", response.data["tokens"])
        self.assertIn("device_token", response.data["tokens"])

        # Verify user was created in database
        user = CustomUser.objects.get(email=self.valid_data["email"])
        self.assertEqual(user.username, self.valid_data["username"])
        self.assertEqual(user.name, self.valid_data["name"])

    def test_duplicate_email_registration(self):
        """Test registration with existing email"""
        # Create user first
        CustomUser.objects.create_user(
            email=self.valid_data["email"],
            username="different_username",
            name="Different User",
            password="password123",
        )

        response = self.client.post(
            self.registration_url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["field"], "email")

    def test_duplicate_username_registration(self):
        """Test registration with existing username"""
        # Create user first
        CustomUser.objects.create_user(
            email="different@example.com",
            username=self.valid_data["username"],
            name="Different User",
            password="password123",
        )

        response = self.client.post(
            self.registration_url, self.valid_data, format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("error", response.data)
        self.assertEqual(response.data["field"], "username")

    def test_invalid_email_validation(self):
        """Test registration with invalid email"""
        invalid_data = self.valid_data.copy()
        invalid_data["email"] = "invalid-email"

        response = self.client.post(self.registration_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_short_password_validation(self):
        """Test registration with short password"""
        invalid_data = self.valid_data.copy()
        invalid_data["password"] = "123"

        response = self.client.post(self.registration_url, invalid_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
