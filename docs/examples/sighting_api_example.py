#!/usr/bin/env python3
"""
Example usage of the Create Sighting API workflow
This demonstrates how a client application would interact with the API
"""

import json

import requests

# API Configuration
API_BASE_URL = "http://localhost:8000/api"  # Update with your Django server URL
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer YOUR_TOKEN_HERE",  # Update with actual token
}


def example_sighting_workflow():
    """
    Demonstrates the complete sighting workflow
    """
    print("=" * 60)
    print("SIGHTING API WORKFLOW EXAMPLE")
    print("=" * 60)

    # Step 1: Create a new sighting
    print("\n1. Creating new sighting...")

    sighting_data = {
        "image_url": "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500",
        "longitude": -122.4194,
        "latitude": 37.7749,
    }

    print(f"Sending sighting data: {json.dumps(sighting_data, indent=2)}")

    try:
        response = requests.post(
            f"{API_BASE_URL}/animals/sightings/create/",
            headers=HEADERS,
            json=sighting_data,
            timeout=60,  # ML processing can take time
        )

        if response.status_code == 201:
            sighting_result = response.json()
            print("✅ Sighting created successfully!")

            # Display ML results
            if sighting_result.get("ml_species_identification"):
                ml_data = sighting_result["ml_species_identification"]
                print(f"🧠 ML Identification: {ml_data}")

            # Display matching profiles
            matches = sighting_result.get("matching_profiles", [])
            print(f"🔍 Found {len(matches)} matching profiles:")

            for i, match in enumerate(matches, 1):
                print(
                    f"  {i}. {match['animal_name']} ({match['species']}) - "
                    f"Similarity: {match['similarity_score']}, "
                    f"Distance: {match['distance_km']}km"
                )

            # Step 2: Select a profile or create new one
            sighting_id = sighting_result["sighting"]["id"]

            if matches:
                # Example: Select the first matching profile
                print("\n2. Selecting matching profile...")

                selection_data = {
                    "sighting_id": sighting_id,
                    "action": "select_existing",
                    "profile_id": matches[0]["profile_id"],
                }

                link_response = requests.post(
                    f"{API_BASE_URL}/animals/sightings/select-profile/",
                    headers=HEADERS,
                    json=selection_data,
                )

                if link_response.status_code == 200:
                    link_result = link_response.json()
                    print("✅ Sighting linked to existing profile!")
                    print(f"📝 {link_result['message']}")
                else:
                    print(f"❌ Failed to link sighting: {link_response.text}")

            else:
                # Example: Create new stray profile
                print("\n2. Creating new stray profile...")

                new_profile_data = {
                    "sighting_id": sighting_id,
                    "action": "create_new",
                    "new_profile_data": {
                        "name": "Stray Dog from Marina",
                        "species": "Dog",
                        "breed": "Unknown",
                    },
                }

                link_response = requests.post(
                    f"{API_BASE_URL}/animals/sightings/select-profile/",
                    headers=HEADERS,
                    json=new_profile_data,
                )

                if link_response.status_code == 200:
                    link_result = link_response.json()
                    print("✅ New stray profile created and linked!")
                    print(f"📝 {link_result['message']}")
                else:
                    print(f"❌ Failed to create profile: {link_response.text}")

        else:
            print(f"❌ Failed to create sighting: {response.status_code}")
            print(f"Error: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {str(e)}")

    print("\n" + "=" * 60)
    print("WORKFLOW COMPLETED")
    print("=" * 60)


def test_ml_apis_directly():
    """
    Test the ML APIs directly (useful for debugging)
    """
    print("\n" + "=" * 60)
    print("TESTING ML APIS DIRECTLY")
    print("=" * 60)

    ml_api_base = "http://139.84.137.195:8001"
    test_image = "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500"

    # Test species identification
    print("\n1. Testing species identification...")
    try:
        response = requests.post(
            f"{ml_api_base}/identify-pet/", json={"url": test_image}, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            print(f"✅ Species identification successful: {result}")
        else:
            print(f"❌ Species identification failed: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Species identification request failed: {str(e)}")

    # Test embedding generation
    print("\n2. Testing embedding generation...")
    try:
        response = requests.post(
            f"{ml_api_base}/generate-embedding/", json={"url": test_image}, timeout=30
        )

        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            print("✅ Embedding generation successful!")
            print(f"Embedding length: {len(embedding)}")
            print(f"First 5 values: {embedding[:5] if embedding else 'None'}")
        else:
            print(f"❌ Embedding generation failed: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Embedding generation request failed: {str(e)}")


def main():
    """
    Main function - run the example
    """
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "test-ml":
        test_ml_apis_directly()
    else:
        print("🚀 Starting Sighting API Workflow Example")
        print("\n⚠️  IMPORTANT: Make sure to:")
        print("   1. Start your Django server: python manage.py runserver")
        print("   2. Update the API_BASE_URL and Authorization token in this script")
        print("   3. Ensure you have valid user authentication")

        print("\nCurrent configuration:")
        print(f"  API Base URL: {API_BASE_URL}")
        print(f"  Headers: {HEADERS}")

        proceed = input("\nProceed with the example? (y/N): ")

        if proceed.lower() == "y":
            example_sighting_workflow()
        else:
            print(
                "Example cancelled. You can also run 'python example_api_usage.py test-ml' to test ML APIs directly."
            )


if __name__ == "__main__":
    main()
