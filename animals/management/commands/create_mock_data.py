import os
import random
from datetime import timedelta

from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from animals.models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
    Lost,
)
from organisations.models import Organisation
from users.models import CustomUser
from utils.vultr_storage import upload_to_vultr


class Command(BaseCommand):
    help = "Create mock data for stray animal profiles, sightings, and related models"

    def add_arguments(self, parser):
        parser.add_argument(
            "--images-folder",
            type=str,
            help="Path to folder containing animal images",
            default="/path/to/your/images",
        )
        parser.add_argument(
            "--num-animals",
            type=int,
            default=50,
            help="Number of stray animals to create (default: 50)",
        )
        parser.add_argument(
            "--num-sightings",
            type=int,
            default=100,
            help="Number of sightings to create (default: 100)",
        )
        parser.add_argument(
            "--num-emergencies",
            type=int,
            default=20,
            help="Number of emergencies to create (default: 20)",
        )
        parser.add_argument(
            "--num-lost",
            type=int,
            default=15,
            help="Number of lost pets to create (default: 15)",
        )
        parser.add_argument(
            "--num-adoptions",
            type=int,
            default=30,
            help="Number of adoption listings to create (default: 30)",
        )

    def handle(self, *args, **options):
        images_folder = options["images_folder"]
        num_animals = options["num_animals"]
        num_sightings = options["num_sightings"]
        num_emergencies = options["num_emergencies"]
        num_lost = options["num_lost"]
        num_adoptions = options["num_adoptions"]

        # Validate images folder
        if not os.path.exists(images_folder):
            raise CommandError(f'Images folder "{images_folder}" does not exist')

        # Get all image files from the folder
        image_files = []
        supported_formats = [".jpg", ".jpeg", ".png", ".webp"]
        for file in os.listdir(images_folder):
            if any(file.lower().endswith(fmt) for fmt in supported_formats):
                image_files.append(os.path.join(images_folder, file))

        if not image_files:
            raise CommandError(f'No supported image files found in "{images_folder}"')

        self.stdout.write(f"Found {len(image_files)} images in {images_folder}")

        # Create mock users if they don't exist
        self.create_mock_users()

        # Create mock organizations if they don't exist
        self.create_mock_organizations()

        # Create stray animals
        self.stdout.write("Creating stray animal profiles...")
        stray_animals = self.create_stray_animals(num_animals, image_files)

        # Create pet animals for lost pets
        self.stdout.write("Creating pet animals for lost pets...")
        pet_animals = self.create_pet_animals(num_lost, image_files)

        # Create sightings
        self.stdout.write("Creating animal sightings...")
        self.create_sightings(num_sightings, stray_animals, image_files)

        # Create emergencies
        self.stdout.write("Creating emergency reports...")
        self.create_emergencies(
            num_emergencies, stray_animals + pet_animals, image_files
        )

        # Create lost pet reports
        self.stdout.write("Creating lost pet reports...")
        self.create_lost_pets(pet_animals)

        # Create adoption listings
        self.stdout.write("Creating adoption listings...")
        self.create_adoptions(num_adoptions, image_files)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created mock data:\n"
                f"- {num_animals} stray animals\n"
                f"- {num_lost} pet animals\n"
                f"- {num_sightings} sightings\n"
                f"- {num_emergencies} emergencies\n"
                f"- {num_lost} lost pet reports\n"
                f"- {num_adoptions} adoption listings"
            )
        )

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
                "email": "david.brown@example.com",
                "username": "davidbrown",
                "name": "David Brown",
            },
            {
                "email": "lisa.davis@example.com",
                "username": "lisadavis",
                "name": "Lisa Davis",
            },
            {
                "email": "animal.lover@example.com",
                "username": "animallover",
                "name": "Animal Lover",
            },
            {
                "email": "rescue.helper@example.com",
                "username": "rescuehelper",
                "name": "Rescue Helper",
            },
        ]

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
                self.stdout.write(f"Created user: {user.email}")

    def create_mock_organizations(self):
        """Create mock organizations for testing"""
        mock_orgs_data = [
            {
                "name": "City Animal Rescue",
                "email": "info@cityrescue.org",
                "address": "123 Rescue Street, Animal City, AC 12345",
                "location": Point(-74.0060, 40.7128),  # New York coordinates
            },
            {
                "name": "Stray Care Foundation",
                "email": "contact@straycare.org",
                "address": "456 Care Avenue, Pet Town, PT 67890",
                "location": Point(-118.2437, 34.0522),  # Los Angeles coordinates
            },
            {
                "name": "Animal Welfare Society",
                "email": "help@animalwelfare.org",
                "address": "789 Welfare Road, Animal Haven, AH 11111",
                "location": Point(-87.6298, 41.8781),  # Chicago coordinates
            },
        ]

        for org_data in mock_orgs_data:
            org, created = Organisation.objects.get_or_create(
                email=org_data["email"], defaults=org_data
            )
            if created:
                self.stdout.write(f"Created organization: {org.name}")

    def upload_image_to_vultr(self, image_path):
        """Upload image to Vultr storage and return URL"""
        try:
            with open(image_path, "rb") as image_file:
                # Create a simple uploaded file object
                uploaded_file = SimpleUploadedFile(
                    name=os.path.basename(image_path),
                    content=image_file.read(),
                    content_type="image/jpeg",
                )

                # Upload to Vultr storage
                image_url = upload_to_vultr(uploaded_file)
                return image_url
        except Exception as e:
            # Fallback to local URL if Vultr upload fails
            self.stdout.write(f"Warning: Failed to upload {image_path} to Vultr: {e}")
            return f"/static/mock_images/{os.path.basename(image_path)}"

    def create_animal_media(self, image_files, animal=None):
        """Create AnimalMedia object with random image and ML processing"""
        image_path = random.choice(image_files)

        # Upload to Vultr and get ML data
        try:
            from django.core.files.uploadedfile import SimpleUploadedFile

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

            if not image_url:
                # Fallback to basic upload if ML processing fails
                image_url = self.upload_image_to_vultr(image_path)
                embedding = None

        except Exception as e:
            self.stdout.write(f"Warning: ML processing failed for {image_path}: {e}")
            image_url = self.upload_image_to_vultr(image_path)
            embedding = None
            species_data = None

        # Create media object with embedding
        media = AnimalMedia.objects.create(
            image_url=image_url, animal=animal, embedding=embedding
        )

        return media, species_data

    def get_random_location(self):
        """Generate random coordinates for testing (around major cities)"""
        # Random locations around major cities
        city_centers = [
            (-74.0060, 40.7128),  # New York
            (-118.2437, 34.0522),  # Los Angeles
            (-87.6298, 41.8781),  # Chicago
            (-95.3698, 29.7604),  # Houston
            (-75.1652, 39.9526),  # Philadelphia
            (-112.0740, 33.4484),  # Phoenix
            (-98.4936, 29.4241),  # San Antonio
            (-117.1611, 32.7157),  # San Diego
        ]

        center = random.choice(city_centers)
        # Add some random offset (within ~10km radius)
        lat_offset = random.uniform(-0.09, 0.09)  # ~10km
        lng_offset = random.uniform(-0.09, 0.09)  # ~10km

        return Point(center[0] + lng_offset, center[1] + lat_offset)

    def get_random_breed_analysis(self):
        """Generate random breed analysis data"""
        features = [
            "Short-haired coat",
            "Long-haired coat",
            "Curly fur",
            "Straight fur",
            "Pointed ears",
            "Floppy ears",
            "Large eyes",
            "Small eyes",
            "Long tail",
            "Short tail",
            "Muscular build",
            "Lean build",
            "Spotted pattern",
            "Striped pattern",
            "Solid color",
            "Mixed colors",
            "Large size",
            "Medium size",
            "Small size",
            "Compact build",
        ]

        return random.sample(features, random.randint(2, 5))

    def create_stray_animals(self, count, image_files):
        """Create stray animal profiles using ML workflow for species/breed detection"""
        # Fallback data for when ML fails
        fallback_species = ["Dog", "Cat", "Rabbit", "Bird", "Hamster"]
        fallback_breeds = {
            "Dog": [
                "Labrador",
                "German Shepherd",
                "Golden Retriever",
                "Bulldog",
                "Poodle",
                "Mixed Breed",
            ],
            "Cat": [
                "Persian",
                "Siamese",
                "Maine Coon",
                "British Shorthair",
                "Ragdoll",
                "Mixed Breed",
            ],
            "Rabbit": [
                "Holland Lop",
                "Netherland Dwarf",
                "Mini Rex",
                "Lionhead",
                "Mixed Breed",
            ],
            "Bird": ["Parakeet", "Canary", "Cockatiel", "Finch", "Mixed Species"],
            "Hamster": ["Syrian", "Dwarf", "Roborovski", "Chinese", "Mixed Breed"],
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
            "Daisy",
            "Bear",
            "Molly",
            "Tucker",
            "Sadie",
            "Jack",
            "Maggie",
            "Duke",
            "Sophie",
            "Zeus",
            "Chloe",
            "Toby",
            "Lily",
            "Oscar",
            "Zoe",
            "Leo",
            "Mia",
            "Rusty",
            "Ruby",
            "Finn",
            "Emma",
            "Diesel",
            "Coco",
            "Shadow",
            "Penny",
            "Hunter",
            "Princess",
            "Ace",
            "Stella",
            "Bandit",
            "Lola",
            "Storm",
        ]

        created_animals = []

        for i in range(count):
            name = random.choice(stray_names)

            # Create first image with ML processing to get species/breed
            media, species_data = self.create_animal_media(image_files)

            # Extract species and breed from ML data
            if species_data:
                # Use ML detected species and breed
                species = species_data.get("species", random.choice(fallback_species))
                breed = species_data.get("breed", "Unknown")
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )

                self.stdout.write(f"ML detected: {species} - {breed} for {name} #{i+1}")
            else:
                # Fallback to random data
                species = random.choice(fallback_species)
                breed = random.choice(fallback_breeds[species])
                breed_analysis = self.get_random_breed_analysis()

                self.stdout.write(
                    f"Using fallback data: {species} - {breed} for {name} #{i+1}"
                )

            # Create animal profile with ML data
            animal = AnimalProfileModel.objects.create(
                name=f"{name} #{i+1}",
                type="stray",
                species=species,
                breed=breed,
                breed_analysis=breed_analysis,
                location=self.get_random_location(),
                is_sterilized=random.choice([True, False]),
                owner=None,  # Stray animals don't have owners
            )

            # Link the first media to the animal
            media.animal = animal
            media.save()
            animal.images.add(media)

            # Add 1-2 additional images without ML processing (for variety)
            num_additional_images = random.randint(0, 2)
            for _ in range(num_additional_images):
                additional_media, _ = self.create_animal_media(image_files, animal)
                animal.images.add(additional_media)

            created_animals.append(animal)
            self.stdout.write(f"Created stray animal: {animal.name} ({animal.species})")

        return created_animals

    def create_pet_animals(self, count, image_files):
        """Create pet animal profiles for lost pets"""
        species_choices = ["Dog", "Cat", "Rabbit", "Bird"]
        breed_choices = {
            "Dog": [
                "Labrador",
                "German Shepherd",
                "Golden Retriever",
                "Bulldog",
                "Poodle",
            ],
            "Cat": ["Persian", "Siamese", "Maine Coon", "British Shorthair", "Ragdoll"],
            "Rabbit": ["Holland Lop", "Netherland Dwarf", "Mini Rex", "Lionhead"],
            "Bird": ["Parakeet", "Canary", "Cockatiel", "Finch"],
        }

        pet_names = [
            "Fluffy",
            "Whiskers",
            "Mittens",
            "Patches",
            "Snowball",
            "Ginger",
            "Tiger",
            "Smokey",
            "Oreo",
            "Peanut",
            "Honey",
            "Cinnamon",
        ]

        created_animals = []
        users = list(CustomUser.objects.all())

        for i in range(count):
            species = random.choice(species_choices)
            breed = random.choice(breed_choices[species])
            name = random.choice(pet_names)
            owner = random.choice(users)

            # Create pet animal profile
            animal = AnimalProfileModel.objects.create(
                name=f"{name} #{i+1}",
                type="pet",
                species=species,
                breed=breed,
                breed_analysis=self.get_random_breed_analysis(),
                location=self.get_random_location(),
                is_sterilized=random.choice([True, False]),
                owner=owner,
            )

            # Add 1-2 images to each pet
            num_images = random.randint(1, 2)
            for _ in range(num_images):
                media, _ = self.create_animal_media(image_files, animal)
                animal.images.add(media)

            created_animals.append(animal)

        return created_animals

    def create_sightings(self, count, animals, image_files):
        """Create animal sightings using ML workflow"""
        users = list(CustomUser.objects.all())

        for i in range(count):
            # 50% chance to link to existing animal, 50% unlinked sighting
            animal = random.choice(animals) if random.choice([True, False]) else None
            reporter = random.choice(users)

            # Create sighting image with ML processing
            sighting_image, species_data = self.create_animal_media(image_files)

            # Extract breed analysis from ML data if available
            if species_data:
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )
                self.stdout.write(
                    f"Sighting #{i+1}: ML detected features: {len(breed_analysis)} traits"
                )
            else:
                breed_analysis = self.get_random_breed_analysis()
                self.stdout.write(f"Sighting #{i+1}: Using fallback breed analysis")

            # Create sighting
            AnimalSighting.objects.create(
                animal=animal,
                location=self.get_random_location(),
                image=sighting_image,
                reporter=reporter,
                breed_analysis=breed_analysis,
            )

    def create_emergencies(self, count, animals, image_files):
        """Create emergency reports with ML-processed images"""
        users = list(CustomUser.objects.all())
        emergency_types = [
            "injury",
            "rescue_needed",
            "aggressive_behavior",
            "missing_lost_pet",
        ]
        descriptions = [
            "Animal appears to be injured and needs immediate help",
            "Stray animal is trapped and requires rescue assistance",
            "Animal showing aggressive behavior towards people",
            "Pet has been missing for several days",
            "Animal found in distress near busy road",
            "Sick animal needs veterinary attention",
            "Animal stuck in dangerous location",
            "Multiple animals in need of rescue",
        ]

        for i in range(count):
            emergency_type = random.choice(emergency_types)
            reporter = random.choice(users)
            animal = (
                random.choice(animals) if emergency_type == "missing_lost_pet" else None
            )

            # Create emergency image with ML processing
            emergency_image, species_data = self.create_animal_media(image_files)

            # Log ML processing results
            if species_data:
                detected_species = species_data.get("species", "Unknown")
                self.stdout.write(f"Emergency #{i+1}: ML detected {detected_species}")
            else:
                self.stdout.write(f"Emergency #{i+1}: ML processing unavailable")

            # Create emergency
            Emergency.objects.create(
                emergency_type=emergency_type,
                reporter=reporter,
                location=self.get_random_location(),
                image=emergency_image,
                animal=animal,
                description=random.choice(descriptions),
                status=random.choice(["active", "resolved"]),
            )

    def create_lost_pets(self, pet_animals):
        """Create lost pet reports"""
        descriptions = [
            "Lost while walking in the park, very friendly",
            "Escaped from backyard, may be scared",
            "Missing since yesterday evening",
            "Last seen near the shopping center",
            "Lost during fireworks, might be hiding",
            "Escaped through open gate",
            "Missing after thunderstorm",
            "Lost while visiting friends",
        ]

        for animal in pet_animals:
            # Create random last seen time (within last 30 days)
            last_seen_time = timezone.now() - timedelta(days=random.randint(1, 30))

            Lost.objects.create(
                pet=animal,
                last_seen_at=self.get_random_location(),
                last_seen_time=last_seen_time,
                description=random.choice(descriptions),
                status=random.choice(["active", "found"]),
            )

    def create_adoptions(self, count, image_files):
        """Create adoption listings with ML-processed animal profiles"""
        organizations = list(Organisation.objects.all())
        if not organizations:
            self.stdout.write("No organizations found, skipping adoption listings")
            return

        # Fallback data for when ML fails
        fallback_species = ["Dog", "Cat", "Rabbit", "Bird"]
        fallback_breeds = {
            "Dog": [
                "Labrador",
                "German Shepherd",
                "Golden Retriever",
                "Bulldog",
                "Poodle",
                "Mixed Breed",
            ],
            "Cat": [
                "Persian",
                "Siamese",
                "Maine Coon",
                "British Shorthair",
                "Ragdoll",
                "Mixed Breed",
            ],
            "Rabbit": [
                "Holland Lop",
                "Netherland Dwarf",
                "Mini Rex",
                "Lionhead",
                "Mixed Breed",
            ],
            "Bird": ["Parakeet", "Canary", "Cockatiel", "Finch", "Mixed Species"],
        }

        adoption_names = [
            "Hope",
            "Lucky",
            "Angel",
            "Miracle",
            "Sunshine",
            "Rainbow",
            "Star",
            "Joy",
            "Faith",
            "Grace",
            "Spirit",
            "Brave",
            "Hero",
            "Champion",
        ]

        descriptions = [
            "Loving and friendly animal looking for a forever home",
            "Great with children and other pets",
            "Needs a quiet home due to shy nature",
            "Very active and loves to play",
            "Senior animal looking for peaceful retirement home",
            "Rescued from difficult situation, now healthy and ready",
            "Perfect companion for active family",
            "Sweet temperament, good for first-time owners",
        ]

        for i in range(count):
            name = random.choice(adoption_names)
            organization = random.choice(organizations)

            # Create first image with ML processing to get species/breed
            media, species_data = self.create_animal_media(image_files)

            # Extract species and breed from ML data
            if species_data:
                # Use ML detected species and breed
                species = species_data.get("species", random.choice(fallback_species))
                breed = species_data.get("breed", "Unknown")
                breed_analysis = species_data.get(
                    "breed_analysis", self.get_random_breed_analysis()
                )

                self.stdout.write(
                    f"Adoption {name} #{i+1}: ML detected {species} - {breed}"
                )
            else:
                # Fallback to random data
                species = random.choice(fallback_species)
                breed = random.choice(fallback_breeds[species])
                breed_analysis = self.get_random_breed_analysis()

                self.stdout.write(
                    f"Adoption {name} #{i+1}: Using fallback {species} - {breed}"
                )

            # Create animal profile for adoption
            animal = AnimalProfileModel.objects.create(
                name=f"{name} #{i+1}",
                type="stray",  # Animals for adoption are typically strays
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

            # Add 2-3 additional images without ML processing (for variety)
            num_additional_images = random.randint(1, 3)
            for _ in range(num_additional_images):
                additional_media, _ = self.create_animal_media(image_files, animal)
                animal.images.add(additional_media)

            # Create adoption listing
            Adoption.objects.create(
                profile=animal,
                posted_by=organization,
                description=random.choice(descriptions),
                status=random.choice(["available", "adopted"]),
            )
