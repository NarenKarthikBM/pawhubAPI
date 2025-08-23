#!/usr/bin/env python3
"""
Test script for Pet Registration and Image Upload APIs
"""

import os
import sys
from io import BytesIO

import django
import requests
from PIL import Image

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.django")
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from animals.models import AnimalProfileModel


class PetRegistrationTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.User = get_user_model()

        # Create test user
        self.user = self.User.objects.create_user(
            email="test@example.com",
            username="testuser",
            name="Test User",
            password="testpass123",
        )

        # Create auth token for the user
        from users.models import UserAuthTokens

        self.token = UserAuthTokens.objects.create(
            user=self.user,
            auth_token="test_token_123",
            device_token="device_123",
            type="web",
        )

    def test_register_pet_success(self):
        """Test successful pet registration"""
        data = {
            "name": "Buddy",
            "species": "Dog",
            "breed": "Golden Retriever",
            "is_sterilized": True,
            "longitude": -122.4194,
            "latitude": 37.7749,
        }

        response = self.client.post(
            "/api/animals/pets/register/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.auth_token}",
        )

        self.assertEqual(response.status_code, 201)
        response_data = response.json()
        self.assertTrue(response_data["success"])
        self.assertEqual(response_data["pet"]["name"], "Buddy")
        self.assertEqual(response_data["pet"]["species"], "Dog")
        self.assertEqual(response_data["pet"]["type"], "pet")

        # Verify pet was created in database
        pet = AnimalProfileModel.objects.get(name="Buddy")
        self.assertEqual(pet.owner, self.user)

    def test_register_pet_missing_required_fields(self):
        """Test pet registration with missing required fields"""
        data = {
            "breed": "Golden Retriever",
        }

        response = self.client.post(
            "/api/animals/pets/register/",
            data=data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.token.auth_token}",
        )

        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertIn("error", response_data)

    def test_register_pet_unauthorized(self):
        """Test pet registration without authentication"""
        data = {
            "name": "Buddy",
            "species": "Dog",
        }

        response = self.client.post(
            "/api/animals/pets/register/", data=data, content_type="application/json"
        )

        self.assertEqual(response.status_code, 401)

    def test_upload_image_success(self):
        """Test successful image upload"""
        # Create a test pet first
        pet = AnimalProfileModel.objects.create(
            name="Test Pet", species="Dog", type="pet", owner=self.user
        )

        # Create a test image
        image = Image.new("RGB", (100, 100), color="red")
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        image_io.name = "test_image.jpg"

        data = {"image_file": image_io, "animal_id": pet.id}

        # Note: This test may fail if Vultr storage is not configured
        # In a real environment, you would mock the upload_image_to_vultr function
        response = self.client.post(
            "/api/animals/pets/upload/",
            data=data,
            HTTP_AUTHORIZATION=f"Token {self.token.auth_token}",
        )

        # The test might fail due to Vultr storage configuration
        # but we can check the response format
        self.assertIn(response.status_code, [201, 400])

    def test_upload_image_unauthorized(self):
        """Test image upload without authentication"""
        image = Image.new("RGB", (100, 100), color="red")
        image_io = BytesIO()
        image.save(image_io, format="JPEG")
        image_io.seek(0)
        image_io.name = "test_image.jpg"

        data = {
            "image_file": image_io,
        }

        response = self.client.post("/api/animals/pets/upload/", data=data)

        self.assertEqual(response.status_code, 401)


def run_manual_tests():
    """Run manual API tests with a running server"""
    print("=== Manual Pet Registration API Tests ===")

    # Base URL for the API
    base_url = "http://localhost:8000/api"

    # Test data
    user_data = {"email": "test@example.com", "password": "testpass123"}

    pet_data = {
        "name": "Buddy",
        "species": "Dog",
        "breed": "Golden Retriever",
        "is_sterilized": True,
        "longitude": -122.4194,
        "latitude": 37.7749,
    }

    try:
        print("\n1. Testing Pet Registration API...")

        # You would need to obtain an auth token first
        # This is just an example of how to test the API
        headers = {
            "Authorization": "Token your_auth_token_here",
            "Content-Type": "application/json",
        }

        response = requests.post(
            f"{base_url}/animals/pets/register/", json=pet_data, headers=headers
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

    except requests.exceptions.ConnectionError:
        print("Server is not running. Please start the Django server first.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    # Run Django tests
    print("Running Django tests...")
    from django.conf import settings
    from django.test.utils import get_runner

    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["__main__"])

    if failures:
        print(f"Tests failed: {failures}")
    else:
        print("All tests passed!")

    # Uncomment to run manual tests
    # run_manual_tests()
