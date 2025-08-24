"""
Test script for the Nearby Sightings and Emergencies API for Organizations

This script tests the new API endpoint that allows organizations to get
both sightings and emergencies within a custom radius.
"""

import json

import requests


def test_nearby_sightings_emergencies_api():
    """Test the nearby sightings and emergencies API for organizations"""

    base_url = "http://localhost:8000"  # Adjust based on your setup
    endpoint = f"{base_url}/api/organisations/sightings-emergencies/nearby/"

    # Test parameters
    test_cases = [
        {
            "name": "Valid request with 10km radius",
            "params": {"latitude": 40.7128, "longitude": -74.0060, "radius": 10},
            "expected_status": 200,
        },
        {
            "name": "Valid request with large radius (100km)",
            "params": {"latitude": 40.7128, "longitude": -74.0060, "radius": 100},
            "expected_status": 200,
        },
        {
            "name": "Invalid request - missing latitude",
            "params": {"longitude": -74.0060, "radius": 10},
            "expected_status": 400,
        },
        {
            "name": "Invalid request - missing longitude",
            "params": {"latitude": 40.7128, "radius": 10},
            "expected_status": 400,
        },
        {
            "name": "Invalid request - missing radius",
            "params": {"latitude": 40.7128, "longitude": -74.0060},
            "expected_status": 400,
        },
        {
            "name": "Invalid request - negative radius",
            "params": {"latitude": 40.7128, "longitude": -74.0060, "radius": -5},
            "expected_status": 400,
        },
        {
            "name": "Invalid request - zero radius",
            "params": {"latitude": 40.7128, "longitude": -74.0060, "radius": 0},
            "expected_status": 400,
        },
        {
            "name": "Invalid request - non-numeric latitude",
            "params": {"latitude": "invalid", "longitude": -74.0060, "radius": 10},
            "expected_status": 400,
        },
    ]

    print("Testing Nearby Sightings and Emergencies API for Organizations")
    print("=" * 70)

    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case['name']}")
        print(f"Parameters: {test_case['params']}")

        try:
            response = requests.get(endpoint, params=test_case["params"])
            status_code = response.status_code

            print(f"Status Code: {status_code}")
            print(f"Expected: {test_case['expected_status']}")

            if status_code == test_case["expected_status"]:
                print("✅ PASS")

                if status_code == 200:
                    data = response.json()
                    print(f"Sightings count: {len(data.get('sightings', []))}")
                    print(f"Emergencies count: {len(data.get('emergencies', []))}")

                    # Validate response structure
                    if "sightings" in data and "emergencies" in data:
                        print("✅ Response structure is correct")
                    else:
                        print("❌ Response structure is incorrect")

                elif status_code == 400:
                    error_data = response.json()
                    print(
                        f"Error message: {error_data.get('error', 'No error message')}"
                    )

            else:
                print("❌ FAIL")
                print(f"Response: {response.text}")

        except requests.exceptions.ConnectionError:
            print("❌ FAIL - Connection Error")
            print("Make sure the Django server is running on localhost:8000")
        except Exception as e:
            print(f"❌ FAIL - Unexpected error: {str(e)}")

    print("\n" + "=" * 70)
    print("Testing completed!")


def test_response_structure():
    """Test the structure of a successful response"""

    print("\nTesting Response Structure...")
    print("-" * 30)

    # Mock response structure for documentation
    expected_structure = {
        "sightings": [
            {
                "id": "integer",
                "animal": {
                    "id": "integer",
                    "name": "string",
                    "species": "string",
                    "breed": "string",
                    "type": "string",
                },
                "location": {"latitude": "number", "longitude": "number"},
                "image": {"id": "integer", "image_url": "string"},
                "reporter": {"id": "integer", "username": "string", "name": "string"},
                "breed_analysis": "array",
                "created_at": "string (ISO datetime)",
            }
        ],
        "emergencies": [
            {
                "id": "integer",
                "emergency_type": "string",
                "reporter": {"id": "integer", "username": "string", "name": "string"},
                "location": {"latitude": "number", "longitude": "number"},
                "image": {"id": "integer", "image_url": "string"},
                "animal": {
                    "id": "integer",
                    "name": "string",
                    "species": "string",
                    "breed": "string",
                    "type": "string",
                },
                "description": "string",
                "status": "string",
                "created_at": "string (ISO datetime)",
            }
        ],
    }

    print("Expected response structure:")
    print(json.dumps(expected_structure, indent=2))


if __name__ == "__main__":
    test_nearby_sightings_emergencies_api()
    test_response_structure()
