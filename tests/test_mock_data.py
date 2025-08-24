#!/usr/bin/env python3
"""
Test script to verify mock data creation
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

from animals.models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
)
from organisations.models import Organisation
from users.models import CustomUser


def test_data_counts():
    """Test the current counts of mock data"""
    print("Current Data Counts:")
    print("=" * 30)

    users_count = CustomUser.objects.count()
    orgs_count = Organisation.objects.count()
    animals_count = AnimalProfileModel.objects.count()
    media_count = AnimalMedia.objects.count()
    sightings_count = AnimalSighting.objects.count()
    emergencies_count = Emergency.objects.count()
    adoptions_count = Adoption.objects.count()

    print(f"Users: {users_count}")
    print(f"Organizations: {orgs_count}")
    print(f"Animals: {animals_count}")
    print(f"Animal Media: {media_count}")
    print(f"Sightings: {sightings_count}")
    print(f"Emergencies: {emergencies_count}")
    print(f"Adoptions: {adoptions_count}")

    # Show some sample data
    print("\nSample Data:")
    print("-" * 15)

    if animals_count > 0:
        sample_animal = AnimalProfileModel.objects.first()
        print(f"Sample Animal: {sample_animal.name} ({sample_animal.species})")
        print(f"  Type: {sample_animal.type}")
        print(f"  Breed: {sample_animal.breed}")
        print(f"  Location: {sample_animal.location}")
        print(f"  Images: {sample_animal.images.count()}")

    if sightings_count > 0:
        sample_sighting = AnimalSighting.objects.first()
        print(f"Sample Sighting: Reported by {sample_sighting.reporter.name}")
        if sample_sighting.animal:
            print(f"  Animal: {sample_sighting.animal.name}")
        print(f"  Location: {sample_sighting.location}")

    return {
        "users": users_count,
        "organizations": orgs_count,
        "animals": animals_count,
        "media": media_count,
        "sightings": sightings_count,
        "emergencies": emergencies_count,
        "adoptions": adoptions_count,
    }


def clear_all_mock_data():
    """Clear all mock data (use with caution!)"""
    print("Clearing all mock data...")

    # Delete in reverse dependency order
    Emergency.objects.all().delete()
    AnimalSighting.objects.all().delete()
    Adoption.objects.all().delete()
    AnimalMedia.objects.all().delete()
    AnimalProfileModel.objects.all().delete()

    # Delete test organizations and users
    Organisation.objects.filter(email__contains="@example.org").delete()
    Organisation.objects.filter(email__contains="@cityrescue.org").delete()
    Organisation.objects.filter(email__contains="@straycare.org").delete()

    CustomUser.objects.filter(email__contains="@example.com").delete()

    print("Mock data cleared!")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--clear":
        clear_all_mock_data()

    counts = test_data_counts()

    if all(count == 0 for count in counts.values()):
        print("\nNo mock data found. Run the mock data creation script:")
        print("python create_mock_data_simple.py [images_folder]")
    else:
        print(f"\nTotal records: {sum(counts.values())}")
