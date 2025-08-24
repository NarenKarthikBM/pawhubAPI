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

from .models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
    Lost,
)
from .serializers import (
    AdoptionSerializer,
    AnimalProfileModelSerializer,
    EmergencySerializer,
)


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
            emergency_type=data["emergency_type"],  # Required field - no default
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


def mark_pet_as_lost(data, user):
    """Mark a pet as lost and create both a lost report and emergency post

    Args:
        data (dict): Validated data containing pet_id, description, location, and time
        user (CustomUser): The pet owner

    Returns:
        dict: Lost report details and emergency post details or error response
    """
    from datetime import datetime

    from .serializers import LostSerializer

    try:
        # Get the pet and verify ownership
        pet = AnimalProfileModel.objects.filter(
            id=data["pet_id"], owner=user, type="pet"
        ).first()

        if not pet:
            return {
                "error": "Pet not found or you don't have permission to mark it as lost"
            }

        # Check if pet is already marked as lost
        existing_lost_report = Lost.objects.filter(pet=pet, status="active").first()

        if existing_lost_report:
            return {"error": "Pet is already marked as lost"}

        # Parse last seen time
        last_seen_time = datetime.now()
        if data.get("last_seen_time"):
            try:
                last_seen_time = datetime.fromisoformat(
                    data["last_seen_time"].replace("Z", "+00:00")
                )
            except ValueError:
                pass  # Use current time if parsing fails

        # Create lost report
        lost_report = Lost.objects.create(
            pet=pet,
            description=data["description"],
            last_seen_time=last_seen_time,
            status="active",
        )

        # Set last seen location if provided
        if data.get("last_seen_longitude") and data.get("last_seen_latitude"):
            lost_report.set_last_seen_location(
                data["last_seen_longitude"], data["last_seen_latitude"]
            )
            lost_report.save()

        # Get the last uploaded image for the pet
        last_image = pet.media_files.order_by("-uploaded_at").first()

        # Create emergency post automatically
        emergency_location = Point(
            data.get("last_seen_longitude", pet.longitude or 0.0),
            data.get("last_seen_latitude", pet.latitude or 0.0),
            srid=4326,
        )

        emergency = Emergency.objects.create(
            emergency_type="missing_lost_pet",
            reporter=user,
            location=emergency_location,
            image=last_image,
            animal=pet,
            description=f"LOST PET: {pet.name} - {data['description']}",
            status="active",
        )

        return {
            "lost_report": LostSerializer(lost_report).details_serializer(),
            "emergency_post": EmergencySerializer(emergency).details_serializer(),
            "message": f"{pet.name} has been marked as lost and an emergency post has been created",
        }

    except Exception as e:
        return {"error": f"Failed to mark pet as lost: {str(e)}"}


# ML API Configuration
ML_API_BASE_URL = "http://139.84.137.195:8001"
ML_API_TIMEOUT = 30
ML_API_KEY = "supersecrettoken123"


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
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ML_API_KEY}",
            "X-API-Token": ML_API_KEY,
        }

        response = requests.post(
            url,
            json=data,
            timeout=ML_API_TIMEOUT,
            headers=headers,
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
        pets = (
            AnimalProfileModel.objects.filter(owner=user, type="pet")
            .prefetch_related("images")
            .order_by("-created_at")
        )

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


def find_similar_pets(
    query_pet: AnimalProfileModel, limit: int = 10
) -> List[AnimalProfileModel]:
    """
    Finds the most similar pets by combining image similarity (80%)
    and location proximity (20%) into a weighted score.

    Args:
        query_pet: The AnimalProfileModel instance we want to find matches for.
        limit: The maximum number of similar pets to return.

    Returns:
        A list of the most similar AnimalProfileModel objects.
    """
    from django.contrib.gis.db.models.functions import Distance
    from django.db.models import ExpressionWrapper, F, FloatField, Min
    from pgvector.django import CosineDistance

    if not query_pet.location:
        return []

    # Get the best embedding from query pet's media files
    query_embedding = None
    best_media = query_pet.media_files.filter(embedding__isnull=False).first()
    if best_media:
        query_embedding = best_media.embedding

    if not query_embedding:
        return []

    # Distance from query pet's location (in meters, converted to km)
    location_distance = Distance("location", query_pet.location)
    location_km = ExpressionWrapper(
        location_distance / 1000.0, output_field=FloatField()
    )

    # Query pets with weighted similarity score
    similar_pets = (
        AnimalProfileModel.objects.filter(
            location__isnull=False,  # Must have location
            media_files__embedding__isnull=False,  # Must have embeddings
        )
        .exclude(id=query_pet.id)  # Exclude the query pet itself
        .annotate(
            # Get minimum cosine distance across all media files
            min_image_distance=Min(
                CosineDistance("media_files__embedding", query_embedding)
            ),
            # Calculate location distance in km
            location_km=location_km,
            # Weighted score: 80% image similarity + 20% location proximity
            # Lower score is better (cosine distance and geographic distance)
            weighted_score=ExpressionWrapper(
                0.8 * F("min_image_distance") + 0.2 * F("location_km"),
                output_field=FloatField(),
            ),
        )
        .distinct()  # Remove duplicates from joins
        .order_by("weighted_score")[:limit]
    )

    return list(similar_pets)


def find_similar_pets_with_details(
    query_pet: AnimalProfileModel, limit: int = 10
) -> List[Dict]:
    """
    Finds the most similar pets with detailed similarity breakdown.
    Uses the same formula as find_similar_pets but returns more information.

    Args:
        query_pet: The AnimalProfileModel instance we want to find matches for.
        limit: The maximum number of similar pets to return.

    Returns:
        A list of dictionaries containing pet data and similarity metrics.
    """
    from django.contrib.gis.db.models.functions import Distance
    from django.db.models import ExpressionWrapper, F, FloatField, Min
    from pgvector.django import CosineDistance

    if not query_pet.location:
        return []

    # Get the best embedding from query pet's media files
    query_embedding = None
    best_media = query_pet.media_files.filter(embedding__isnull=False).first()
    if best_media:
        query_embedding = best_media.embedding

    if not query_embedding:
        return []

    # Distance from query pet's location (in meters, converted to km)
    location_distance = Distance("location", query_pet.location)
    location_km = ExpressionWrapper(
        location_distance / 1000.0, output_field=FloatField()
    )

    # Query pets with weighted similarity score
    similar_pets = (
        AnimalProfileModel.objects.filter(
            location__isnull=False,  # Must have location
            media_files__embedding__isnull=False,  # Must have embeddings
        )
        .exclude(id=query_pet.id)  # Exclude the query pet itself
        .annotate(
            # Get minimum cosine distance across all media files
            min_image_distance=Min(
                CosineDistance("media_files__embedding", query_embedding)
            ),
            # Calculate location distance in km
            location_km=location_km,
            # Weighted score: 80% image similarity + 20% location proximity
            # Lower score is better (cosine distance and geographic distance)
            weighted_score=ExpressionWrapper(
                0.8 * F("min_image_distance") + 0.2 * F("location_km"),
                output_field=FloatField(),
            ),
        )
        .distinct()  # Remove duplicates from joins
        .order_by("weighted_score")[:limit]
    )

    # Build detailed results
    detailed_results = []
    for pet in similar_pets:
        # Calculate image similarity score (1 - cosine_distance)
        image_similarity = 1.0 - pet.min_image_distance

        detailed_results.append(
            {
                "pet": AnimalProfileModelSerializer(pet).details_serializer(),
                "similarity_metrics": {
                    "weighted_score": float(pet.weighted_score),
                    "image_similarity": float(
                        image_similarity
                    ),  # 0-1, higher is better
                    "image_distance": float(
                        pet.min_image_distance
                    ),  # 0-1, lower is better
                    "location_distance_km": float(pet.location_km),
                    "weights": {"image_weight": 0.8, "location_weight": 0.2},
                },
            }
        )

    return detailed_results


def get_nearby_adoptions(latitude, longitude, radius_km=20):
    """Get available adoption listings from organizations within specified radius

    Args:
        latitude (float): User's latitude coordinate
        longitude (float): User's longitude coordinate
        radius_km (int): Search radius in kilometers (default: 20km)

    Returns:
        dict: Success response with adoption listings or error message
    """
    try:
        # Create location point from user coordinates
        user_location = Point(longitude, latitude, srid=4326)

        # Get available adoptions from organizations within radius
        nearby_adoptions = (
            Adoption.objects.filter(
                status="available",  # Only show available adoptions
                posted_by__location__distance_lte=(user_location, D(km=radius_km)),
                posted_by__is_verified=True,  # Only verified organizations
            )
            .select_related("profile", "posted_by")
            .prefetch_related("profile__images")
            .order_by("-created_at")
        )

        # Serialize adoption data with enhanced organization location details
        adoptions_data = []
        for adoption in nearby_adoptions:
            adoption_data = AdoptionSerializer(adoption).details_serializer()

            # Add distance and organization location details
            if adoption.posted_by.location:
                org_location = adoption.posted_by.location
                distance = user_location.distance(org_location) * 111  # Convert to km

                adoption_data["posted_by"]["location"] = {
                    "latitude": org_location.y,
                    "longitude": org_location.x,
                }
                adoption_data["distance_km"] = round(distance, 2)

                # Add organization address if available
                if adoption.posted_by.address:
                    adoption_data["posted_by"]["address"] = adoption.posted_by.address

            adoptions_data.append(adoption_data)

        return {
            "success": True,
            "adoptions": adoptions_data,
            "count": len(adoptions_data),
            "search_radius_km": radius_km,
            "user_location": {
                "latitude": latitude,
                "longitude": longitude,
            },
        }

    except Exception as e:
        return {"error": f"Failed to retrieve nearby adoptions: {str(e)}"}


def get_organisation_adoptions(organisation):
    """Get all adoption listings posted by an organization

    Args:
        organisation (Organisation): The organization to get adoptions for

    Returns:
        dict: List of adoption listings or error response
    """
    try:
        # Get all adoptions posted by this organization
        adoptions = (
            Adoption.objects.filter(posted_by=organisation)
            .select_related("profile", "posted_by")
            .prefetch_related("profile__images")
        )

        # Serialize adoption data
        adoptions_data = [
            AdoptionSerializer(adoption).details_serializer() for adoption in adoptions
        ]

        return {
            "success": True,
            "adoptions": adoptions_data,
            "count": len(adoptions_data),
            "organisation": {
                "id": organisation.id,
                "name": organisation.name,
                "email": organisation.email,
                "is_verified": organisation.is_verified,
            },
        }

    except Exception as e:
        return {"error": f"Failed to retrieve organization adoptions: {str(e)}"}


def mark_adoption_as_adopted(adoption_id, organisation):
    """Mark an adoption listing as adopted

    Args:
        adoption_id (int): ID of the adoption to mark as adopted
        organisation (Organisation): The organization that posted the adoption

    Returns:
        dict: Updated adoption details or error response
    """
    try:
        # Get the adoption listing
        adoption = (
            Adoption.objects.filter(id=adoption_id, posted_by=organisation)
            .select_related("profile", "posted_by")
            .prefetch_related("profile__images")
            .first()
        )

        if not adoption:
            return {
                "error": "Adoption listing not found or you don't have permission to modify it"
            }

        # Check if already adopted
        if adoption.status == "adopted":
            return {"error": "This adoption listing is already marked as adopted"}

        # Update status to adopted
        adoption.status = "adopted"
        adoption.save()

        return {
            "success": True,
            "message": "Adoption listing marked as adopted successfully",
            "adoption": AdoptionSerializer(adoption).details_serializer(),
        }

    except Exception as e:
        return {"error": f"Failed to mark adoption as adopted: {str(e)}"}
