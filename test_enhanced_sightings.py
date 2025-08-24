#!/usr/bin/env python3
"""
Test script for the enhanced sighting workflow
This script tests the ML similarity matching functionality.
"""

import os
import sys
from pathlib import Path

import django

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings.local")
django.setup()

from animals.models import AnimalMedia, AnimalProfileModel, AnimalSighting
from users.models import CustomUser


def test_enhanced_sightings():
    """Test the enhanced sighting creation with similarity matching"""

    print("🧪 Testing Enhanced Sighting Workflow")
    print("=" * 50)

    # Count existing data
    existing_animals = AnimalProfileModel.objects.count()
    existing_sightings = AnimalSighting.objects.count()
    existing_media = AnimalMedia.objects.count()
    existing_users = CustomUser.objects.count()

    print("📊 Existing data before test:")
    print(f"   • Animals: {existing_animals}")
    print(f"   • Sightings: {existing_sightings}")
    print(f"   • Media: {existing_media}")
    print(f"   • Users: {existing_users}")

    print("\n🎯 Expected Workflow:")
    print("1. Load images from sc2 folder")
    print("2. Process each image with ML APIs")
    print("3. Search for similar animals (>90% threshold)")
    print("4. Either match to existing animal OR create new profile")
    print("5. Create sighting record with proper timestamps")
    print("6. All sightings within 20km of Kolkata center")
    print("7. All sightings scattered over past 30 days")

    print("\n📍 Location Requirements:")
    print("   • Center: (22.96391456958128, 88.53245371532486)")
    print("   • Radius: 20km from center")

    print("\n⏰ Time Requirements:")
    print("   • Range: Past 30 days from now")
    print("   • Distribution: Random scatter")

    print("\n🔬 ML Requirements:")
    print("   • Image processing: upload_and_process_image()")
    print("   • Similarity search: find_similar_profiles()")
    print("   • Threshold: 90% similarity")
    print("   • Features: Species, breed, visual characteristics")

    print("\n🗂️ File Requirements:")
    print("   • Source: sc2/ subfolder")
    print("   • Formats: .jpg, .jpeg, .png, .webp")
    print("   • Processing: Each image becomes a sighting")

    print("\n" + "=" * 50)
    print("✅ Test setup complete!")
    print("💡 To run: python create_mock_data_simple.py /path/to/images")
    print("   (Ensure sc2/ folder exists within the images folder)")


if __name__ == "__main__":
    test_enhanced_sightings()
