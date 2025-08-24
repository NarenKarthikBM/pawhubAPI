#!/usr/bin/env python3
"""
Test script for the Create Sighting API workflow
This tests the core functionality without requiring a running Django server.
"""

import os
import sys

import django

# Add the parent directory to the Python path
sys.path.append("/Volumes/Files/Coding/StatusCode2/pawhubAPI")

# Configure Django settings
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.django")
django.setup()


def test_ml_api_calls():
    """Test ML API calls with a test image"""
    from animals.utils import (
        generate_image_embedding,
        identify_pet_species,
        process_image_ml_data,
    )

    # Test with a sample dog image URL
    test_image_url = "https://images.unsplash.com/photo-1552053831-71594a27632d?w=500"

    print("Testing ML API calls...")
    print(f"Test image URL: {test_image_url}")

    # Test species identification
    print("\n1. Testing species identification...")
    species_data = identify_pet_species(test_image_url)
    if species_data:
        print(f"Species identification successful: {species_data}")
    else:
        print("Species identification failed")

    # Test embedding generation
    print("\n2. Testing embedding generation...")
    embedding = generate_image_embedding(test_image_url)
    if embedding:
        print(f"Embedding generated successfully. Length: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
    else:
        print("Embedding generation failed")

    # Test concurrent processing
    print("\n3. Testing concurrent ML processing...")
    species_data, embedding = process_image_ml_data(test_image_url)

    if species_data and embedding:
        print("Concurrent processing successful!")
        print(f"Species data: {species_data}")
        print(f"Embedding length: {len(embedding)}")
    else:
        print("Concurrent processing failed")
        print(f"Species data: {species_data}")
        print(f"Embedding: {embedding is not None}")


def test_workflow_validation():
    """Test input validation for the sighting workflow"""
    from animals.validator import (
        CreateSightingInputValidator,
        SightingSelectProfileInputValidator,
    )

    print("\nTesting input validation...")

    # Test CreateSightingInputValidator
    print("\n1. Testing CreateSightingInputValidator...")
    valid_data = {
        "image_url": "https://example.com/image.jpg",
        "longitude": -122.4194,
        "latitude": 37.7749,
    }

    try:
        validator = CreateSightingInputValidator(valid_data)
        validated = validator.serialized_data()
        print(f"Valid data passed: {validated}")
    except Exception as e:
        print(f"Validation failed: {e}")

    # Test SightingSelectProfileInputValidator
    print("\n2. Testing SightingSelectProfileInputValidator...")
    select_existing_data = {
        "sighting_id": 1,
        "action": "select_existing",
        "profile_id": 123,
    }

    try:
        validator = SightingSelectProfileInputValidator(select_existing_data)
        validated = validator.serialized_data()
        print(f"Select existing profile validation passed: {validated}")
    except Exception as e:
        print(f"Validation failed: {e}")

    create_new_data = {
        "sighting_id": 1,
        "action": "create_new",
        "new_profile_data": {"name": "Stray Dog", "species": "Dog", "breed": "Mixed"},
    }

    try:
        validator = SightingSelectProfileInputValidator(create_new_data)
        validated = validator.serialized_data()
        print(f"Create new profile validation passed: {validated}")
    except Exception as e:
        print(f"Validation failed: {e}")


def test_serializers():
    """Test serializer functionality"""
    from animals.serializers import SightingMatchSerializer

    print("\nTesting serializers...")

    # Test SightingMatchSerializer
    mock_matching_profiles = [
        {
            "profile": {
                "id": 1,
                "name": "Buddy",
                "species": "Dog",
                "breed": "Golden Retriever",
                "type": "stray",
                "location": {"latitude": 37.7749, "longitude": -122.4194},
            },
            "similarity_score": 0.85,
            "distance_km": 2.5,
            "matching_image_url": "https://example.com/buddy.jpg",
        }
    ]

    formatted = SightingMatchSerializer.format_matching_profiles(mock_matching_profiles)
    print(f"Formatted matching profiles: {formatted}")


def main():
    """Run all tests"""
    print("=" * 60)
    print("SIGHTING API WORKFLOW TEST")
    print("=" * 60)

    try:
        test_workflow_validation()
        test_serializers()

        # Only test ML APIs if we can connect
        print("\nAttempting to test ML API connectivity...")
        test_ml_api_calls()

    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback

        traceback.print_exc()

    print("\n" + "=" * 60)
    print("TEST COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    main()
