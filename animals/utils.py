import concurrent.futures
import secrets
from typing import Dict, List, Optional, Tuple

import requests
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D

from users.models import (
    CustomUser,
    UserAuthTokens,
)
from users.serializers import UserSerializer
from utils.vultr_storage import upload_image_to_vultr

from .models import AnimalMedia, AnimalProfileModel, AnimalSighting, Emergency
from .serializers import AnimalProfileModelSerializer, EmergencySerializer


def generate_tokens():
    return {
        "auth_token": secrets.token_urlsafe(120),
        "device_token": secrets.token_urlsafe(16),
    }


def generate_otp():
    generateSecrets = secrets.SystemRandom()
    return generateSecrets.randint(100000, 999999)


def authorize_user(data):
    user = CustomUser.objects.filter(email=data["email"]).first()

    if not user:
        return None

    if not user.check_password(data["password"]):
        return {"error": "Invalid Password"}

    tokens = generate_tokens()

    UserAuthTokens(
        user=user,
        auth_token=tokens["auth_token"],
        device_token=tokens["device_token"],
        type="web",
    ).save()

    return {
        "tokens": tokens,
        "user_details": UserSerializer(user).details_serializer(),
    }


def revoke_tokens(auth_token, device_token):
    UserAuthTokens.objects.filter(
        auth_token=auth_token, device_token=device_token
    ).delete()


def create_user(email, name, password):
    user = CustomUser(
        email=email,
        name=name,
    ).save()
    user.set_password(password)
    user.save()

    return user


def create_emergency(data, user):
    """Create a new emergency report

    Args:
        data (dict): Validated emergency data containing longitude, latitude, description, and optional image_url
        user (CustomUser): The user reporting the emergency

    Returns:
        dict: Emergency details or error response
    """
    try:
        # Create location point from coordinates
        location = Point(data["longitude"], data["latitude"], srid=4326)

        # Create AnimalMedia object if image_url is provided
        image_media = None
        if data.get("image_url"):
            image_media = AnimalMedia.objects.create(image_url=data["image_url"])

        # Create emergency report
        emergency = Emergency.objects.create(
            reporter=user,
            location=location,
            image=image_media,
            description=data["description"],
            status="active",
        )

        return {
            "emergency": EmergencySerializer(emergency).details_serializer(),
            "message": "Emergency reported successfully",
        }

    except Exception as e:
        return {"error": f"Failed to create emergency: {str(e)}"}


# ML API Configuration
ML_API_BASE_URL = "http://139.84.137.195:8001"
ML_API_TIMEOUT = 30


def call_ml_api(endpoint: str, data: Dict) -> Optional[Dict]:
    """Call ML API endpoint with error handling

    Args:
        endpoint (str): API endpoint path
        data (dict): Request data

    Returns:
        dict: API response or None if failed
    """
    try:
        url = f"{ML_API_BASE_URL}/{endpoint}/"
        response = requests.post(
            url,
            json=data,
            timeout=ML_API_TIMEOUT,
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            return response.json()
        else:
            print(f"ML API Error: {response.status_code} - {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"ML API Request failed: {str(e)}")
        return None


def identify_animal_species(image_url: str) -> Optional[Dict]:
    """Identify animal species and breed analysis from image URL

    Args:
        image_url (str): URL of the image

    Returns:
        dict: Species identification results with breed_analysis or None if failed
    """
    return call_ml_api("identify-pet", {"url": image_url})


def generate_image_embedding(image_url: str) -> Optional[List[float]]:
    """Generate embedding for image

    Args:
        image_url (str): URL of the image

    Returns:
        list: Embedding vector or None if failed
    """
    result = call_ml_api("generate-embedding", {"url": image_url})
    if result and "embedding" in result:
        return result["embedding"]
    return None


def upload_and_process_image(
    image_file,
) -> Tuple[Optional[str], Optional[Dict], Optional[List[float]]]:
    """Upload image to Vultr Object Storage and process with ML APIs

    Args:
        image_file: Django uploaded file object

    Returns:
        tuple: (image_url, species_data, embedding) or (None, None, None) if upload failed
    """
    # Upload image to Vultr Object Storage
    success, result = upload_image_to_vultr(image_file)

    if not success:
        # Return error message in place of image_url for error handling
        return result, None, None

    image_url = result

    # Process the uploaded image with ML APIs
    species_data, embedding = process_image_ml_data(image_url)

    return image_url, species_data, embedding


def process_image_ml_data(
    image_url: str,
) -> Tuple[Optional[Dict], Optional[List[float]]]:
    """Process image with both ML APIs concurrently

    Args:
        image_url (str): URL of the image

    Returns:
        tuple: (species_data, embedding) or (None, None) if both failed
    """
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both API calls concurrently
        species_future = executor.submit(identify_animal_species, image_url)
        embedding_future = executor.submit(generate_image_embedding, image_url)

        # Get results
        species_data = species_future.result()
        embedding = embedding_future.result()

    return species_data, embedding


def create_animal_media_with_embedding(
    image_url: str, embedding: List[float]
) -> AnimalMedia:
    """Create AnimalMedia object with embedding

    Args:
        image_url (str): URL of the image
        embedding (list): Vector embedding

    Returns:
        AnimalMedia: Created media object
    """
    return AnimalMedia.objects.create(image_url=image_url, embedding=embedding)


def calculate_breed_similarity(
    breed_analysis_1: List[str], breed_analysis_2: List[str]
) -> float:
    """Calculate similarity between two breed analysis arrays

    Args:
        breed_analysis_1 (list): First breed analysis features
        breed_analysis_2 (list): Second breed analysis features

    Returns:
        float: Similarity score between 0 and 1
    """
    if not breed_analysis_1 or not breed_analysis_2:
        return 0.0

    # Convert to sets for intersection calculation
    set1 = set(breed_analysis_1)
    set2 = set(breed_analysis_2)

    # Calculate Jaccard similarity (intersection over union)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    if union == 0:
        return 0.0

    return intersection / union


def find_similar_animal_profiles(
    location: Point,
    embedding: List[float],
    breed_analysis: Optional[List[str]] = None,
    radius_km: int = 10,
    similarity_threshold: float = 0.7,
    limit: int = 10,
) -> List[Dict]:
    """Find similar animal profiles within radius using vector similarity and breed analysis

    Args:
        location (Point): Sighting location
        embedding (list): Image embedding vector
        breed_analysis (list): Breed analysis features from ML model
        radius_km (int): Search radius in kilometers
        similarity_threshold (float): Minimum similarity score
        limit (int): Maximum number of results

    Returns:
        list: List of matching animal profiles with similarity scores
    """
    try:
        from pgvector.django import CosineDistance

        # Find profiles within geographic radius that have embeddings
        nearby_profiles = AnimalProfileModel.objects.filter(
            location__distance_lte=(location, D(km=radius_km)),
            media_files__embedding__isnull=False,
        ).distinct()

        # Calculate similarity scores for profiles with embeddings
        matching_profiles = []

        for profile in nearby_profiles:
            # Get the profile's media with embeddings
            media_with_embeddings = (
                profile.media_files.filter(embedding__isnull=False)
                .annotate(similarity=1 - CosineDistance("embedding", embedding))
                .order_by("-similarity")
            )

            if media_with_embeddings.exists():
                best_match = media_with_embeddings.first()
                image_similarity_score = float(best_match.similarity)

                # Calculate breed similarity if breed analysis is available
                breed_similarity_score = 0.0
                if breed_analysis and profile.breed_analysis:
                    breed_similarity_score = calculate_breed_similarity(
                        breed_analysis, profile.breed_analysis
                    )

                # Combine image similarity and breed similarity
                # Weight: 70% image similarity, 30% breed similarity
                combined_similarity = (
                    0.7 * image_similarity_score + 0.3 * breed_similarity_score
                )

                if combined_similarity >= similarity_threshold:
                    matching_profiles.append(
                        {
                            "profile": AnimalProfileModelSerializer(
                                profile
                            ).details_serializer(),
                            "similarity_score": combined_similarity,
                            "image_similarity": image_similarity_score,
                            "breed_similarity": breed_similarity_score,
                            "distance_km": float(
                                profile.location.distance(location).km
                            ),
                            "matching_image_url": best_match.image_url,
                        }
                    )

        # Sort by combined similarity score (descending) and limit results
        matching_profiles.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matching_profiles[:limit]

    except Exception as e:
        print(f"Error finding similar profiles: {str(e)}")
        return []


def create_sighting_record(
    data: Dict,
    user: CustomUser,
    animal_media: AnimalMedia,
    breed_analysis: Optional[List[str]] = None,
) -> AnimalSighting:
    """Create initial sighting record without animal profile link

    Args:
        data (dict): Validated sighting data
        user (CustomUser): Reporter user
        animal_media (AnimalMedia): Associated media object
        breed_analysis (list): Breed analysis features from ML model

    Returns:
        AnimalSighting: Created sighting object
    """
    location = Point(data["longitude"], data["latitude"], srid=4326)

    return AnimalSighting.objects.create(
        reporter=user,
        location=location,
        image=animal_media,
        animal=None,  # Will be linked later when user selects/creates profile
        breed_analysis=breed_analysis or [],
    )


def create_stray_animal_profile(
    data: Dict,
    location: Point,
    user: CustomUser,
    breed_analysis: Optional[List[str]] = None,
) -> AnimalProfileModel:
    """Create a new stray animal profile

    Args:
        data (dict): Animal profile data
        location (Point): Animal location
        user (CustomUser): User creating the profile
        breed_analysis (list): Breed analysis features from ML model

    Returns:
        AnimalProfileModel: Created animal profile
    """
    return AnimalProfileModel.objects.create(
        name=data["name"],
        species=data["species"],
        breed=data.get("breed", ""),
        type="stray",
        location=location,
        owner=None,  # Stray animals don't have owners
        breed_analysis=breed_analysis or [],
    )


def link_sighting_to_profile(
    sighting: AnimalSighting, profile: AnimalProfileModel
) -> None:
    """Link a sighting to an animal profile

    Args:
        sighting (AnimalSighting): The sighting to link
        profile (AnimalProfileModel): The animal profile to link to
    """
    sighting.animal = profile
    sighting.save()

    # Also link the media to the profile if not already linked
    if not sighting.image.animal:
        sighting.image.animal = profile
        sighting.image.save()


def register_pet(validated_data, user):
    """Register a new pet for the authenticated user

    Args:
        validated_data (dict): Validated pet registration data
        user (CustomUser): The authenticated user

    Returns:
        dict: Registration result with pet details or error
    """
    try:
        # Create the pet profile
        pet = AnimalProfileModel.objects.create(
            name=validated_data["name"],
            species=validated_data["species"],
            breed=validated_data.get("breed", ""),
            type="pet",  # Always set to pet for registered pets
            owner=user,
            is_sterilized=validated_data.get("is_sterilized", False),
        )

        # Set location if provided
        longitude = validated_data.get("longitude")
        latitude = validated_data.get("latitude")
        if longitude is not None and latitude is not None:
            pet.set_location(longitude, latitude)
            pet.save()

        return {
            "success": True,
            "pet": AnimalProfileModelSerializer(pet).details_serializer(),
        }

    except Exception as e:
        return {"error": f"Failed to register pet: {str(e)}"}


def upload_pet_image(validated_data, user):
    """Upload an image for a pet

    Args:
        validated_data (dict): Validated image upload data
        user (CustomUser): The authenticated user

    Returns:
        dict: Upload result with image details or error
    """
    try:
        image_file = validated_data["image_file"]
        animal_id = validated_data.get("animal_id")

        # Upload image to Vultr storage
        upload_result = upload_image_to_vultr(image_file)

        if not upload_result.get("success"):
            return {"error": "Failed to upload image to storage"}

        image_url = upload_result["url"]

        # Create AnimalMedia object
        animal_media = AnimalMedia.objects.create(
            image_url=image_url,
        )

        # If animal_id is provided, link the image to that animal
        if animal_id:
            try:
                animal = AnimalProfileModel.objects.get(
                    id=animal_id,
                    owner=user,  # Ensure user owns the animal
                )
                animal_media.animal = animal
                animal_media.save()

                # Add the media to the animal's images
                animal.images.add(animal_media)

            except AnimalProfileModel.DoesNotExist:
                # If animal doesn't exist or user doesn't own it,
                # still return the uploaded image but without linking
                pass

        return {
            "success": True,
            "image": {
                "id": animal_media.id,
                "image_url": animal_media.image_url,
                "animal_id": animal_media.animal.id if animal_media.animal else None,
                "uploaded_at": animal_media.uploaded_at.isoformat(),
            },
        }

    except Exception as e:
        return {"error": f"Failed to upload image: {str(e)}"}


def get_user_pets(user):
    """Get all pets owned by a specific user

    Args:
        user (CustomUser): The user whose pets to retrieve

    Returns:
        dict: User's pets with serialized data
    """
    try:
        # Get all pets owned by the user
        pets = AnimalProfileModel.objects.filter(
            owner=user, type="pet"
        ).prefetch_related("images").order_by("-created_at")

        # Serialize pets data
        pets_data = [
            AnimalProfileModelSerializer(pet).user_pets_serializer() for pet in pets
        ]

        return {
            "success": True,
            "pets": pets_data,
            "count": len(pets_data),
        }

    except Exception as e:
        return {"error": f"Failed to retrieve user pets: {str(e)}"}
