#!/usr/bin/env python3
"""
Simple Mock Data Creator for PawHub API
This script creates mock data for testing purposes.
Run this from the project root directory.
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

import random

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile

from animals.models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
)
from organisations.models import Organisation

# Import models
from users.models import CustomUser

# Try to import Vultr storage utility
try:
    from utils.vultr_storage import upload_to_vultr

    VULTR_AVAILABLE = True
except ImportError:
    VULTR_AVAILABLE = False
    print("Warning: Vultr storage utility not available. Using placeholder URLs.")


class MockDataCreator:
    def __init__(self, images_folder=None):
        self.images_folder = images_folder
        self.image_files = []

        if images_folder and os.path.exists(images_folder):
            supported_formats = [".jpg", ".jpeg", ".png", ".webp"]
            for file in os.listdir(images_folder):
                if any(file.lower().endswith(fmt) for fmt in supported_formats):
                    self.image_files.append(os.path.join(images_folder, file))

        print(f"Found {len(self.image_files)} images")

    def upload_image_to_vultr(self, image_path):
        """Upload image to Vultr storage and return URL"""
        if not VULTR_AVAILABLE:
            return f"/static/mock_images/{os.path.basename(image_path)}"

        try:
            with open(image_path, "rb") as image_file:
                uploaded_file = SimpleUploadedFile(
                    name=os.path.basename(image_path),
                    content=image_file.read(),
                    content_type="image/jpeg",
                )
                image_url = upload_to_vultr(uploaded_file)
                return image_url
        except Exception as e:
            print(f"Warning: Failed to upload {image_path} to Vultr: {e}")
            return f"/static/mock_images/{os.path.basename(image_path)}"

    def create_animal_media(self, animal=None):
        """Create AnimalMedia object with random image and optional ML processing"""
        if not self.image_files:
            # Create placeholder media
            return AnimalMedia.objects.create(
                image_url="https://via.placeholder.com/400x300/grey/white?text=Animal+Photo",
                animal=animal,
            ), None

        image_path = random.choice(self.image_files)

        # Try ML processing first
        try:
            from animals.utils import upload_and_process_image

            # Create uploaded file object
            with open(image_path, "rb") as f:
                uploaded_file = SimpleUploadedFile(
                    name=os.path.basename(image_path),
                    content=f.read(),
                    content_type="image/jpeg",
                )

            # Process with ML APIs
            image_url, species_data, embedding = upload_and_process_image(uploaded_file)

            if image_url:
                media = AnimalMedia.objects.create(
                    image_url=image_url, animal=animal, embedding=embedding
                )
                return media, species_data

        except Exception as e:
            print(f"Warning: ML processing failed for {image_path}: {e}")

        # Fallback to basic upload
        image_url = self.upload_image_to_vultr(image_path)
        return AnimalMedia.objects.create(image_url=image_url, animal=animal), None

    def get_random_location(self):
        """Generate random coordinates around major cities"""
        city_centers = [
            (-74.0060, 40.7128),  # New York
            (-118.2437, 34.0522),  # Los Angeles
            (-87.6298, 41.8781),  # Chicago
            (-95.3698, 29.7604),  # Houston
            (-75.1652, 39.9526),  # Philadelphia
        ]

        center = random.choice(city_centers)
        lat_offset = random.uniform(-0.05, 0.05)  # ~5km radius
        lng_offset = random.uniform(-0.05, 0.05)

        return Point(center[0] + lng_offset, center[1] + lat_offset)

    def get_random_breed_analysis(self):
        """Generate random breed analysis data"""
        features = [
            "Short-haired coat",
            "Long-haired coat",
            "Pointed ears",
            "Floppy ears",
            "Large eyes",
            "Small eyes",
            "Long tail",
            "Short tail",
            "Muscular build",
            "Spotted pattern",
            "Striped pattern",
            "Solid color",
            "Large size",
            "Medium size",
        ]
        return random.sample(features, random.randint(2, 4))

    def create_mock_users(self):
        """Create mock users for testing"""
        mock_users_data = [
            {
                "email": "john.doe@example.com",
                "username": "johndoe",
                "name": "John Doe",
            },
            {
                "email": "jane.smith@example.com",
                "username": "janesmith",
                "name": "Jane Smith",
            },
            {
                "email": "mike.johnson@example.com",
                "username": "mikejohnson",
                "name": "Mike Johnson",
            },
            {
                "email": "sarah.wilson@example.com",
                "username": "sarahwilson",
                "name": "Sarah Wilson",
            },
            {
                "email": "animal.lover@example.com",
                "username": "animallover",
                "name": "Animal Lover",
            },
        ]

        created_users = []
        for user_data in mock_users_data:
            user, created = CustomUser.objects.get_or_create(
                email=user_data["email"],
                defaults={
                    "username": user_data["username"],
                    "name": user_data["name"],
                    "is_active": True,
                },
            )
            if created:
                user.set_password("testpassword123")
                user.save()
                print(f"Created user: {user.email}")
            created_users.append(user)

        return created_users

    def create_mock_organizations(self):
        """Create mock organizations for testing"""
        mock_orgs_data = [
            {
                "name": "City Animal Rescue",
                "email": "info@cityrescue.org",
                "address": "123 Rescue Street, Animal City, AC 12345",
                "location": Point(-74.0060, 40.7128),
            },
            {
                "name": "Stray Care Foundation",
                "email": "contact@straycare.org",
                "address": "456 Care Avenue, Pet Town, PT 67890",
                "location": Point(-118.2437, 34.0522),
            },
        ]

        created_orgs = []
        for org_data in mock_orgs_data:
            org, created = Organisation.objects.get_or_create(
                email=org_data["email"], defaults=org_data
            )
            if created:
                print(f"Created organization: {org.name}")
            created_orgs.append(org)

        return created_orgs

    def create_stray_animals(self, count=20):
        """Create stray animal profiles using ML workflow when possible"""
        # Fallback data for when ML fails
        fallback_species = ["Dog", "Cat", "Rabbit", "Bird"]
        fallback_breeds = {
            "Dog": ["Labrador", "German Shepherd", "Golden Retriever", "Mixed Breed"],
            "Cat": ["Persian", "Siamese", "Maine Coon", "Mixed Breed"],
            "Rabbit": ["Holland Lop", "Netherland Dwarf", "Mixed Breed"],
            "Bird": ["Parakeet", "Canary", "Mixed Species"],
        }

        stray_names = [
            "Buddy",
            "Max",
            "Bella",
            "Charlie",
            "Lucy",
            "Cooper",
            "Luna",
            "Rocky",
            "Shadow",
            "Bandit",
            "Storm",
            "Star",
            "Hope",
            "Lucky",
            "Angel",
            "Spirit",
        ]

        created_animals = []
        for i in range(count):
            name = random.choice(stray_names)

            # Create first image with ML processing to get species/breed
            media, species_data = self.create_animal_media()

            # Extract species and breed from ML data
            if species_data:
                # Use ML detected species and breed
                species = species_data.get("species", random.choice(fallback_species))
                breed = species_data.get("breed", "Unknown")
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )

                print(f"ML detected: {species} - {breed} for {name} #{i+1}")
            else:
                # Fallback to random data
                species = random.choice(fallback_species)
                breed = random.choice(fallback_breeds[species])
                breed_analysis = self.get_random_breed_analysis()

                print(f"Using fallback data: {species} - {breed} for {name} #{i+1}")

            animal = AnimalProfileModel.objects.create(
                name=f"{name} #{i+1}",
                type="stray",
                species=species,
                breed=breed,
                breed_analysis=breed_analysis,
                location=self.get_random_location(),
                is_sterilized=random.choice([True, False]),
                owner=None,
            )

            # Link the first media to the animal
            media.animal = animal
            media.save()
            animal.images.add(media)

            # Add 1-2 additional images
            for _ in range(random.randint(0, 1)):
                additional_media, _ = self.create_animal_media(animal)
                animal.images.add(additional_media)

            created_animals.append(animal)
            print(f"Created stray animal: {animal.name}")

        return created_animals

    def create_sightings(self, animals, users, count=30):
        """Create animal sightings with ML processing"""
        for i in range(count):
            animal = random.choice(animals) if random.choice([True, False]) else None
            reporter = random.choice(users)

            # Create sighting image with ML processing
            sighting_image, species_data = self.create_animal_media()

            # Extract breed analysis from ML data if available
            if species_data:
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )
                print(f"Sighting #{i+1}: ML detected {len(breed_analysis)} features")
            else:
                breed_analysis = self.get_random_breed_analysis()
                print(f"Sighting #{i+1}: Using fallback breed analysis")

            AnimalSighting.objects.create(
                animal=animal,
                location=self.get_random_location(),
                image=sighting_image,
                reporter=reporter,
                breed_analysis=breed_analysis,
            )
            print(f"Created sighting #{i+1}")

    def create_emergencies(self, animals, users, count=10):
        """Create emergency reports with ML processing"""
        emergency_types = ["injury", "rescue_needed", "aggressive_behavior"]
        descriptions = [
            "Animal appears to be injured and needs immediate help",
            "Stray animal is trapped and requires rescue assistance",
            "Animal showing aggressive behavior towards people",
            "Animal found in distress near busy road",
        ]

        for i in range(count):
            emergency_type = random.choice(emergency_types)
            reporter = random.choice(users)
            animal = random.choice(animals) if random.choice([True, False]) else None

            # Create emergency image with ML processing
            emergency_image, species_data = self.create_animal_media()

            # Log ML processing results
            if species_data:
                detected_species = species_data.get("species", "Unknown")
                print(f"Emergency #{i+1}: ML detected {detected_species}")
            else:
                print(f"Emergency #{i+1}: ML processing unavailable")

            Emergency.objects.create(
                emergency_type=emergency_type,
                reporter=reporter,
                location=self.get_random_location(),
                image=emergency_image,
                animal=animal,
                description=random.choice(descriptions),
                status=random.choice(["active", "resolved"]),
            )
            print(f"Created emergency #{i+1}")

    def create_adoptions(self, organizations, count=15):
        """Create adoption listings with ML processing"""
        # Fallback data for when ML fails
        fallback_species = ["Dog", "Cat", "Rabbit"]
        fallback_breeds = {
            "Dog": ["Labrador", "German Shepherd", "Mixed Breed"],
            "Cat": ["Persian", "Siamese", "Mixed Breed"],
            "Rabbit": ["Holland Lop", "Mixed Breed"],
        }

        adoption_names = ["Hope", "Lucky", "Angel", "Miracle", "Sunshine", "Star"]
        descriptions = [
            "Loving and friendly animal looking for a forever home",
            "Great with children and other pets",
            "Very active and loves to play",
            "Sweet temperament, good for first-time owners",
        ]

        for i in range(count):
            name = random.choice(adoption_names)
            organization = random.choice(organizations)

            # Create first image with ML processing to get species/breed
            media, species_data = self.create_animal_media()

            # Extract species and breed from ML data
            if species_data:
                # Use ML detected species and breed
                species = species_data.get("species", random.choice(fallback_species))
                breed = species_data.get("breed", "Unknown")
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )

                print(f"Adoption {name} #{i+1}: ML detected {species} - {breed}")
            else:
                # Fallback to random data
                species = random.choice(fallback_species)
                breed = random.choice(fallback_breeds[species])
                breed_analysis = self.get_random_breed_analysis()

                print(f"Adoption {name} #{i+1}: Using fallback {species} - {breed}")

            animal = AnimalProfileModel.objects.create(
                name=f"{name} #{i+1}",
                type="stray",
                species=species,
                breed=breed,
                breed_analysis=breed_analysis,
                location=organization.location
                if organization.location
                else self.get_random_location(),
                is_sterilized=random.choice([True, False]),
                owner=None,
            )

            # Link the first media to the animal
            media.animal = animal
            media.save()
            animal.images.add(media)

            # Add 2-3 additional images
            for _ in range(random.randint(1, 2)):
                additional_media, _ = self.create_animal_media(animal)
                animal.images.add(additional_media)

            Adoption.objects.create(
                profile=animal,
                posted_by=organization,
                description=random.choice(descriptions),
                status=random.choice(["available", "adopted"]),
            )
            print(f"Created adoption listing: {animal.name}")


def main():
    """Main function to create all mock data"""
    print("PawHub API Mock Data Creator")
    print("=" * 40)

    # Get images folder from command line argument or use default
    images_folder = None
    if len(sys.argv) > 1:
        images_folder = sys.argv[1]
        if not os.path.exists(images_folder):
            print(f"Warning: Images folder '{images_folder}' does not exist")
            images_folder = None
    else:
        print("Usage: python create_mock_data_simple.py [images_folder_path]")
        print("No images folder provided, using placeholder images")

    # Create mock data creator
    creator = MockDataCreator(images_folder)

    # Create base data
    print("\n1. Creating mock users...")
    users = creator.create_mock_users()

    print("\n2. Creating mock organizations...")
    organizations = creator.create_mock_organizations()

    print("\n3. Creating stray animals...")
    animals = creator.create_stray_animals(20)

    print("\n4. Creating animal sightings...")
    creator.create_sightings(animals, users, 30)

    print("\n5. Creating emergency reports...")
    creator.create_emergencies(animals, users, 10)

    print("\n6. Creating adoption listings...")
    creator.create_adoptions(organizations, 15)

    print("\n" + "=" * 40)
    print("Mock data creation completed successfully!")
    print("Created:")
    print(f"- {len(users)} users")
    print(f"- {len(organizations)} organizations")
    print(f"- {len(animals)} stray animals")
    print("- 30 sightings")
    print("- 10 emergencies")
    print("- 15 adoptions")


if __name__ == "__main__":
    main()
