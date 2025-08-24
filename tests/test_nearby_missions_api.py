#!/usr/bin/env python3
"""
Test script for the Nearby Missions API
"""

import requests

# Configuration
BASE_URL = "http://localhost:8000"
API_ENDPOINT = f"{BASE_URL}/api/organisations/missions/nearby/"

# Test coordinates (San Francisco area)
test_coordinates = {"latitude": 37.7749, "longitude": -122.4194}


def test_nearby_missions_api():
    """Test the nearby missions API"""

    print("Testing Nearby Missions API")
    print("=" * 50)

    # Test without authentication (should fail)
    print("\n1. Testing without authentication:")
    response = requests.get(API_ENDPOINT, params=test_coordinates)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # Test with missing coordinates
    print("\n2. Testing with missing coordinates:")
    response = requests.get(API_ENDPOINT)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # Test with invalid coordinates
    print("\n3. Testing with invalid coordinates:")
    invalid_coords = {"latitude": "invalid", "longitude": "invalid"}
    response = requests.get(API_ENDPOINT, params=invalid_coords)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    # Test with valid coordinates but no authentication
    print("\n4. Testing with valid coordinates but no authentication:")
    response = requests.get(API_ENDPOINT, params=test_coordinates)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")

    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nNOTE: To test with authentication, you need to:")
    print("1. Register/login a user to get an authentication token")
    print("2. Add the token to headers: {'Authorization': 'Token your_token_here'}")
    print("3. Create some OrganisationMissions with location data in the database")


if __name__ == "__main__":
    test_nearby_missions_api()
