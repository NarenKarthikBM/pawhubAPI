#!/usr/bin/env python
"""
Test script to verify breed analysis functionality
"""

import os
import sys

import django

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.django")
django.setup()

from animals.utils import calculate_breed_similarity, identify_animal_species


def test_breed_similarity():
    """Test the breed similarity calculation"""
    print("Testing breed similarity calculation...")

    # Test case 1: Same features
    breed1 = ["fluffy_coat", "pointed_ears", "long_tail"]
    breed2 = ["fluffy_coat", "pointed_ears", "long_tail"]
    similarity = calculate_breed_similarity(breed1, breed2)
    print(f"Same features: {similarity} (expected: 1.0)")

    # Test case 2: Partially overlapping features
    breed1 = ["fluffy_coat", "pointed_ears", "long_tail"]
    breed2 = ["fluffy_coat", "pointed_ears", "short_tail"]
    similarity = calculate_breed_similarity(breed1, breed2)
    print(f"Partial overlap: {similarity} (expected: 0.5)")

    # Test case 3: No overlapping features
    breed1 = ["fluffy_coat", "pointed_ears"]
    breed2 = ["smooth_coat", "floppy_ears"]
    similarity = calculate_breed_similarity(breed1, breed2)
    print(f"No overlap: {similarity} (expected: 0.0)")

    # Test case 4: Empty arrays
    breed1 = []
    breed2 = ["fluffy_coat"]
    similarity = calculate_breed_similarity(breed1, breed2)
    print(f"One empty: {similarity} (expected: 0.0)")


def test_api_endpoint():
    """Test the identify-species API endpoint"""
    print("\nTesting identify-species API endpoint...")

    # Test with a dummy URL (this will likely fail without a real ML API)
    test_url = "https://example.com/test_image.jpg"
    result = identify_animal_species(test_url)

    if result:
        print(f"API Response: {result}")
        if "breed_analysis" in result:
            print(f"Breed analysis found: {result['breed_analysis']}")
        else:
            print("No breed_analysis in response")
    else:
        print("API call failed (expected with dummy URL)")


if __name__ == "__main__":
    print("Starting breed analysis tests...\n")
    test_breed_similarity()
    test_api_endpoint()
    print("\nTests completed!")
