#!/usr/bin/env python3
"""
Simple Mock Data Creator for PawHub API
This script creates mock data for testing purposes with ML-enhanced sighting workflow.
Run this from the project root directory.
"""

import os
import random
import sys
import time
import math
from datetime import timedelta
from pathlib import Path

import django

# Add the project root to Python path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pawhubAPI.settings")
# Disable logging to avoid file permission issues
os.environ.setdefault("DJANGO_LOG_LEVEL", "ERROR")

# Configure minimal logging before Django setup
import logging

logging.basicConfig(level=logging.ERROR)

django.setup()

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from animals.models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
)

# Import ML utilities for similarity matching
from animals.utils import find_similar_animal_profiles, upload_and_process_image
from organisations.models import OrganisationModel
from users.models import CustomUser


class MockDataCreator:
    """Creates mock data for testing purposes with ML integration"""

    def __init__(self):
        """Initialize the mock data creator"""
        self.similarity_threshold = 0.8  # 90% similarity threshold

    def create_users(self, count=15):
        """Create mock users"""
        print(f"Creating {count} mock users...")
        
        first_names = [
            "Arjun", "Priya", "Rahul", "Anita", "Vikram", "Sneha", "Amit", "Kavya",
            "Ravi", "Meera", "Sanjay", "Pooja", "Kiran", "Deepika", "Suresh"
        ]
        
        last_names = [
            "Sharma", "Patel", "Kumar", "Singh", "Gupta", "Verma", "Agarwal", "Jain",
            "Reddy", "Nair", "Iyer", "Chopra", "Malhotra", "Banerjee", "Das"
        ]
        
        created_users = []
        
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            
            user = CustomUser.objects.create_user(
                username=f"{first_name.lower()}{last_name.lower()}{i}",
                email=f"{first_name.lower()}.{last_name.lower()}{i}@example.com",
                password="testpass123",
                name=f"{first_name} {last_name}",
            )
            created_users.append(user)
        
        print(f"✅ Created {len(created_users)} users")
        return created_users

    def create_organisations(self, count=5):
        """Create mock organisations"""
        print(f"Creating {count} mock organisations...")
        
        org_names = [
            "Kolkata Animal Welfare Society",
            "Bengal Stray Animal Care",
            "Howrah Pet Rescue Foundation",
            "West Bengal Animal Protection Trust",
            "Calcutta Street Dog Shelter"
        ]
        
        created_orgs = []
        
        for i, name in enumerate(org_names[:count]):
            # Generate random location within Kolkata area
            lat = 22.9641 + random.uniform(-0.1, 0.1)
            lng = 88.5324 + random.uniform(-0.1, 0.1)
            
            org = OrganisationModel.objects.create(
                name=name,
                email=f"contact@{name.lower().replace(' ', '').replace('_', '')}org.com",
                phone=f"+91{random.randint(7000000000, 9999999999)}",
                type="shelter",
                verification_status="verified",
                location=Point(lng, lat),
            )
            created_orgs.append(org)
        
        print(f"✅ Created {len(created_orgs)} organisations")
        return created_orgs

    def get_random_location_in_radius(self, center_lat=22.96391456958128, center_lng=88.53245371532486, radius_km=20):
        """Generate random location within specified radius of center point"""
        # Convert radius from km to degrees (rough approximation)
        # 1 degree ≈ 111 km at equator
        lat_per_km = 1 / 111.0
        lng_per_km = 1 / (111.0 * math.cos(math.radians(center_lat)))

        # Generate random distance (0 to radius_km) and angle
        distance = random.uniform(0, radius_km)
        angle = random.uniform(0, 2 * math.pi)

        # Calculate random radius (for uniform distribution within circle)
        radius_km = distance * math.sqrt(random.random())

        # Convert to lat/lng offsets
        lat_offset = radius_km * lat_per_km * math.sin(angle)
        lng_offset = radius_km * lng_per_km * math.cos(angle)

        # Apply offsets to center coordinates
        lat = center_lat + lat_offset
        lng = center_lng + lng_offset

        return Point(lng, lat)  # Note: Point(longitude, latitude)

    def get_random_past_datetime(self):
        """Generate random datetime within the past month"""
        now = timezone.now()
        one_month_ago = now - timedelta(days=30)

        # Generate random number of seconds between one month ago and now
        time_diff = now - one_month_ago
        random_seconds = random.randint(0, int(time_diff.total_seconds()))

        return one_month_ago + timedelta(seconds=random_seconds)

    def create_enhanced_sightings(self, users, organisations):
        """Create sightings from sc2 folder images with ML similarity matching"""
        
        # Path to sc2 folder
        image_folder = Path(__file__).parent / "sc2"
        
        if not image_folder.exists():
            print(f"❌ Error: {image_folder} directory not found!")
            return []
        
        # Get all image files from sc2 folder
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        image_files = [
            f for f in image_folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ]
        
        if not image_files:
            print(f"❌ No image files found in {image_folder}")
            return []

        # Geographic parameters for Kolkata area
        center_lat = 22.96391456958128
        center_lng = 88.53245371532486
        
        total_images = len(image_files)
        total_time = total_images * 20 / 60  # Total time in minutes
        print(f"\n🚀 Starting enhanced sightings creation...")
        print(f"📁 Processing {total_images} images from {image_folder}")
        print(f"⏱️  Estimated total time: {total_time:.1f} minutes at 3 sightings/minute")
        print(f"📍 Geographic center: {center_lat}, {center_lng}")
        print(f"🎯 Similarity threshold: 90%")
        print(f"📅 Time range: Past 30 days")
        print("=" * 60)

        created_sightings = []

        for i, image_path in enumerate(image_files):
            try:
                print(f"\n🔄 Processing image {i+1}/{total_images}: {image_path.name}")

                # Upload and process image with ML
                print("🤖 Calling ML API for species identification and embedding...")
                result = upload_and_process_image(image_path)
                
                if not result:
                    print(f"⚠️  Failed to process image {image_path.name}, skipping...")
                    continue

                species_data = result.get('species')
                embedding = result.get('embedding')

                # Fix embedding dimensions if needed (database expects 384, but API might return 512)
                if embedding:
                    if len(embedding) == 512:
                        embedding = embedding[:384]  # Truncate to 384 dimensions
                        print("🔧 Adjusted embedding from 512 to 384 dimensions")
                    elif len(embedding) < 384:
                        # Pad with zeros if too short
                        embedding = embedding + [0.0] * (384 - len(embedding))
                        print(f"🔧 Padded embedding from {len(embedding)} to 384 dimensions")

                if not embedding or not species_data:
                    print(f"⚠️  ML processing failed for {image_path.name}, skipping...")
                    continue

                print(f"🔍 Detected species: {species_data.get('species', 'Unknown')} (confidence: {species_data.get('confidence', 0):.2f})")

                # Find similar animals based on embedding
                print("🔍 Searching for similar animal profiles...")
                similar_animals = find_similar_animal_profiles(embedding, threshold=self.similarity_threshold)

                matched_animal = None
                if similar_animals:
                    # Get the most similar animal
                    most_similar = similar_animals[0]
                    similarity_score = most_similar['similarity']
                    matched_animal = most_similar['animal']
                    print(f"✅ Found similar animal: {matched_animal.name} (similarity: {similarity_score:.2f})")
                else:
                    print("❌ No similar animals found, creating new animal profile...")
                    
                    # Create new animal profile
                    reporter = random.choice(users + organisations) if users and organisations else None
                    
                    # Create media first
                    with open(image_path, 'rb') as img_file:
                        uploaded_file = SimpleUploadedFile(
                            name=image_path.name,
                            content=img_file.read(),
                            content_type=f"image/{image_path.suffix[1:]}"
                        )
                    
                    animal_media = AnimalMedia.objects.create(
                        media_type="image",
                        media_url=f"https://mock-storage.vultr.com/{image_path.name}",
                        uploaded_by=reporter if hasattr(reporter, 'email') else None,
                        embedding=embedding,
                    )
                    
                    # Create new animal
                    matched_animal = AnimalProfileModel.objects.create(
                        name=f"Stray {species_data.get('species', 'Animal')} {random.randint(1000, 9999)}",
                        type=species_data.get('species', 'dog').lower(),
                        breed=species_data.get('breed', 'Mixed'),
                        color=random.choice(['Brown', 'Black', 'White', 'Golden', 'Gray', 'Mixed']),
                        gender=random.choice(['male', 'female']),
                        size=random.choice(['small', 'medium', 'large']),
                        status='stray',
                        health_status=random.choice(['healthy', 'minor_injury', 'sick']),
                        location=self.get_random_location_in_radius(center_lat, center_lng),
                        reporter=reporter,
                    )
                    
                    # Add media to animal
                    matched_animal.media.add(animal_media)
                    print(f"🆕 Created new animal profile: {matched_animal.name}")

                # Generate sighting data
                location = self.get_random_location_in_radius(center_lat, center_lng)
                sighting_time = self.get_random_past_datetime()
                
                reporter = random.choice(users + organisations) if users and organisations else None
                
                # Create media for sighting (using the same image)
                with open(image_path, 'rb') as img_file:
                    uploaded_file = SimpleUploadedFile(
                        name=f"sighting_{image_path.name}",
                        content=img_file.read(),
                        content_type=f"image/{image_path.suffix[1:]}"
                    )
                
                sighting_media = AnimalMedia.objects.create(
                    media_type="image",
                    media_url=f"https://mock-storage.vultr.com/sighting_{image_path.name}",
                    uploaded_by=reporter if hasattr(reporter, 'email') else None,
                    embedding=embedding,
                )

                # Create sighting
                sighting = AnimalSighting.objects.create(
                    animal=matched_animal,
                    reporter=reporter,
                    location=location,
                    description=f"Sighting of {matched_animal.name} in Kolkata area",
                    status='verified',
                    image=sighting_media,  # Reference the media we just created
                    created_at=sighting_time,
                )

                created_sightings.append(sighting)

                # Calculate progress
                progress = (i + 1) / total_images * 100
                remaining_time = (total_images - (i + 1)) * 20 / 60  # in minutes

                print(f"✅ Created sighting #{i+1}/{total_images} for {matched_animal.name}")
                print(f"   📍 Location: ({location.y:.6f}, {location.x:.6f})")
                print(f"   📅 Date: {sighting_time.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"   📊 Progress: {progress:.1f}% complete")
                
                # Rate limiting: 3 sightings per minute = 20 seconds between each
                if i + 1 < total_images:  # Don't sleep after the last image
                    print(f"   ⏳ Waiting 20 seconds before processing next sighting... (Est. {remaining_time:.1f} min remaining)")
                    time.sleep(20)

            except Exception as e:
                print(f"❌ Error processing sighting #{i+1}: {str(e)}")
                continue

        print(f"\n🎉 Created {len(created_sightings)} enhanced sightings successfully!")
        return created_sightings

    def create_emergencies(self, animals, users, count=10):
        """Create mock emergency reports"""
        print(f"Creating {count} mock emergency reports...")
        
        emergency_types = [
            'injured', 'sick', 'trapped', 'aggressive', 'lost', 'abandoned',
            'hit_by_vehicle', 'poisoning', 'abuse', 'other'
        ]
        
        severity_levels = ['low', 'medium', 'high', 'critical']
        statuses = ['reported', 'in_progress', 'resolved', 'false_alarm']
        
        created_emergencies = []
        
        for i in range(count):
            animal = random.choice(animals) if animals else None
            reporter = random.choice(users) if users else None
            
            # Generate random location within Kolkata area
            location = self.get_random_location_in_radius()
            
            emergency = Emergency.objects.create(
                animal=animal,
                reporter=reporter,
                emergency_type=random.choice(emergency_types),
                severity=random.choice(severity_levels),
                location=location,
                description=f"Emergency report #{i+1} - {random.choice(emergency_types)} situation",
                status=random.choice(statuses),
                created_at=self.get_random_past_datetime(),
            )
            created_emergencies.append(emergency)
        
        print(f"✅ Created {len(created_emergencies)} emergency reports")
        return created_emergencies

    def create_adoptions(self, animals, users, organisations, count=8):
        """Create mock adoption records"""
        print(f"Creating {count} mock adoption records...")
        
        statuses = ['pending', 'approved', 'rejected', 'completed']
        
        created_adoptions = []
        
        for i in range(count):
            animal = random.choice(animals) if animals else None
            adopter = random.choice(users) if users else None
            organisation = random.choice(organisations) if organisations else None
            
            adoption = Adoption.objects.create(
                animal=animal,
                adopter=adopter,
                organisation=organisation,
                status=random.choice(statuses),
                application_date=self.get_random_past_datetime(),
                notes=f"Adoption application #{i+1} for {animal.name if animal else 'unknown animal'}",
            )
            created_adoptions.append(adoption)
        
        print(f"✅ Created {len(created_adoptions)} adoption records")
        return created_adoptions

    def run(self):
        """Run the complete mock data creation process"""
        print("🚀 Starting enhanced mock data creation with ML integration...")
        print("=" * 60)
        
        try:
            # Create base data
            users = self.create_users(15)
            organisations = self.create_organisations(5)
            
            # Create ML-enhanced sightings (this will also create animals)
            sightings = self.create_enhanced_sightings(users, organisations)
            
            # Get all animals created
            animals = list(AnimalProfileModel.objects.all())
            print(f"\n📊 Total animals in database: {len(animals)}")
            
            # Create emergencies and adoptions
            emergencies = self.create_emergencies(animals, users, 10)
            adoptions = self.create_adoptions(animals, users, organisations, 8)
            
            print("\n" + "=" * 60)
            print("🎉 Mock data creation completed successfully!")
            print(f"👥 Users: {len(users)}")
            print(f"🏢 Organisations: {len(organisations)}")
            print(f"🐕 Animals: {len(animals)}")
            print(f"👁️  Sightings: {len(sightings)}")
            print(f"🚨 Emergencies: {len(emergencies)}")
            print(f"🏠 Adoptions: {len(adoptions)}")
            
        except Exception as e:
            print(f"❌ Error during mock data creation: {str(e)}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    creator = MockDataCreator()
    creator.run()
