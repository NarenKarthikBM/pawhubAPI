from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from pawhubAPI.settings.custom_DRF_settings.parsers import OctetStreamParser
from rest_framework import status
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from pawhubAPI.settings.custom_DRF_settings.authentication import (
    OrganisationTokenAuthentication,
    UserTokenAuthentication,
)

from .models import (
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
)
from .serializers import (
    AnimalProfileModelSerializer,
    AnimalSightingSerializer,
    EmergencySerializer,
)
from .utils import (
    create_emergency,
    get_nearby_adoptions,
    get_organisation_adoptions,
    mark_adoption_as_adopted,
    mark_pet_as_lost,
)
from .validator import (
    CreateEmergencyInputValidator,
    MarkAdoptionAsAdoptedInputValidator,
    MarkPetAsLostInputValidator,
    NearbyAdoptionsInputValidator,
)


class AnimalProfileListAPI(APIView):
    """API view to list and create animal profiles

    Methods:
        GET, POST
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get list of all animal profiles",
        operation_summary="List Animal Profiles",
        tags=["Animal Profiles"],
        manual_parameters=[
            openapi.Parameter(
                "type",
                openapi.IN_QUERY,
                description="Filter by animal type (pet/stray)",
                type=openapi.TYPE_STRING,
                enum=["pet", "stray"],
            ),
            openapi.Parameter(
                "species",
                openapi.IN_QUERY,
                description="Filter by species",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved animal profiles",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "name": openapi.Schema(type=openapi.TYPE_STRING),
                            "species": openapi.Schema(type=openapi.TYPE_STRING),
                            "breed": openapi.Schema(type=openapi.TYPE_STRING),
                            "type": openapi.Schema(type=openapi.TYPE_STRING),
                            "is_sterilized": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "location": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "latitude": openapi.Schema(
                                        type=openapi.TYPE_NUMBER
                                    ),
                                    "longitude": openapi.Schema(
                                        type=openapi.TYPE_NUMBER
                                    ),
                                },
                            ),
                            "owner": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "username": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                            "images": openapi.Schema(
                                type=openapi.TYPE_ARRAY,
                                items=openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "image_url": openapi.Schema(
                                            type=openapi.TYPE_STRING
                                        ),
                                    },
                                ),
                            ),
                            "created_at": openapi.Schema(
                                type=openapi.TYPE_STRING, format="date-time"
                            ),
                        },
                    ),
                ),
            ),
        },
    )
    def get(self, request):
        """GET Method to retrieve all animal profiles"""

        profiles = AnimalProfileModel.objects.all()

        # Apply filters
        animal_type = request.query_params.get("type")
        if animal_type:
            profiles = profiles.filter(type=animal_type)

        species = request.query_params.get("species")
        if species:
            profiles = profiles.filter(species__icontains=species)

        profiles_data = [
            AnimalProfileModelSerializer(profile).details_serializer()
            for profile in profiles
        ]

        return Response(profiles_data, status=status.HTTP_200_OK)


class NearbySightingsAPI(APIView):
    """API view to get latest animal sightings within 20km of given coordinates

    Gets only one sighting per animal profile within the last week
    """

    @swagger_auto_schema(
        operation_description="Get latest animal sightings within 20km of given coordinates",
        operation_summary="Get Nearby Animal Sightings",
        tags=["Animal Sightings"],
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of nearby animal sightings",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "animal": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "location": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "image": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "reporter": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid coordinates"
            ),
        },
    )
    def get(self, request):
        """Get latest animal sightings within 20km of given coordinates

        Args:
            request: HTTP request with latitude and longitude parameters

        Returns:
            Response: List of nearby animal sightings (one per animal profile)
        """
        # Get latitude and longitude from query parameters
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Both latitude and longitude are required and must be valid numbers"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a point from the coordinates
        user_location = Point(longitude, latitude, srid=4326)

        # Calculate date one week ago
        one_week_ago = timezone.now() - timezone.timedelta(days=7)

        # Get sightings within 20km and within the last week
        nearby_sightings = (
            AnimalSighting.objects.filter(
                location__distance_lte=(user_location, D(km=20)),
                created_at__gte=one_week_ago,
                animal__isnull=False,  # Only include sightings with associated animals
            )
            .select_related("animal", "image", "reporter")
            .order_by("animal", "-created_at")
        )

        # Get only the latest sighting per animal profile
        seen_animals = set()
        unique_sightings = []

        for sighting in nearby_sightings:
            if sighting.animal.id not in seen_animals:
                seen_animals.add(sighting.animal.id)
                unique_sightings.append(sighting)

        # Serialize the data
        sightings_data = [
            AnimalSightingSerializer(sighting).details_serializer()
            for sighting in unique_sightings
        ]

        return Response(sightings_data, status=status.HTTP_200_OK)


class NearbyEmergenciesAPI(APIView):
    """API view to get active animal emergencies within 20km of given coordinates

    Gets only active emergencies within the last week
    """

    @swagger_auto_schema(
        operation_description="Get active animal emergencies within 20km of given coordinates",
        operation_summary="Get Nearby Animal Emergencies",
        tags=["Animal Emergencies"],
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of nearby animal emergencies",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "reporter": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "location": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "image": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                            "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid coordinates"
            ),
        },
    )
    def get(self, request):
        """Get active animal emergencies within 20km of given coordinates

        Args:
            request: HTTP request with latitude and longitude parameters

        Returns:
            Response: List of nearby active emergencies
        """
        # Get latitude and longitude from query parameters
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Both latitude and longitude are required and must be valid numbers"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a point from the coordinates
        user_location = Point(longitude, latitude, srid=4326)

        # Calculate date one week ago
        one_week_ago = timezone.now() - timezone.timedelta(days=7)

        # Get active emergencies within 20km and within the last week
        nearby_emergencies = (
            Emergency.objects.filter(
                location__distance_lte=(user_location, D(km=20)),
                created_at__gte=one_week_ago,
                status="active",  # Only include active emergencies
            )
            .select_related("reporter", "image")
            .order_by("-created_at")
        )

        # Serialize the data
        emergencies_data = [
            EmergencySerializer(emergency).details_serializer()
            for emergency in nearby_emergencies
        ]

        return Response(emergencies_data, status=status.HTTP_200_OK)


class EmergencyCreateAPI(APIView):
    """API view to create emergency reports

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Create a new emergency report",
        operation_summary="Create Emergency Report",
        tags=["Emergencies"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "longitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Emergency location longitude coordinate",
                ),
                "latitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Emergency location latitude coordinate",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the emergency (minimum 10 characters)",
                    min_length=10,
                ),
                "emergency_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Type of emergency",
                    enum=["injury", "rescue_needed", "aggressive_behavior", "missing_lost_pet"],
                ),
                "image_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Optional URL of emergency image",
                    nullable=True,
                ),
            },
            required=["longitude", "latitude", "description", "emergency_type"],
        ),
        responses={
            201: openapi.Response(
                description="Emergency created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "emergency": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(description="Bad Request - Invalid input data"),
            401: openapi.Response(description="Unauthorized - Authentication required"),
        },
    )
    def post(self, request):
        """Create a new emergency report

        Args:
            request: HTTP request with emergency data

        Returns:
            Response: Created emergency details or error
        """
        try:
            # Validate input data
            validated_data = CreateEmergencyInputValidator(
                request.data
            ).serialized_data()

            # Create emergency using utility function
            result = create_emergency(validated_data, request.user)

            # Check if emergency creation was successful
            if "error" in result:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception:
            return Response(
                {"error": "Failed to create emergency report"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class CreateSightingAPI(APIView):
    """API view to create a new animal sighting

    This is the main endpoint for the sighting workflow:
    1. Upload image file + location
    2. Upload image to Vultr Object Storage
    3. Process with ML APIs (species identification + embedding)
    4. Find matching animal profiles within 10km
    5. Return matches for user selection

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]
    parser_classes = [OctetStreamParser]

    @swagger_auto_schema(
        operation_description="Create a new animal sighting with raw image upload and coordinates in query params",
        operation_summary="Create Animal Sighting (Octet-Stream)",
        tags=["Animal Sightings"],
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="Latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="Longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
        ],
        consumes=["application/octet-stream"],
        responses={
            201: openapi.Response(
                description="Sighting created successfully with matching profiles"
            ),
            400: openapi.Response(description="Invalid input data or file upload error"),
        },
    )
    def post(self, request):
        try:
            # Import utilities here to avoid circular imports
            from .serializers import SightingMatchSerializer, SightingSerializer
            from .utils import (
                create_animal_media_with_embedding,
                create_sighting_record,
                find_similar_animal_profiles,
                upload_and_process_image,
            )
            from .validator import CreateSightingInputValidator

            lat = request.query_params.get('latitude')
            lon = request.query_params.get('longitude')
            if not lat or not lon:
                return Response(
                    {"error": "latitude and longitude query parameters are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            
            validated_data = {"longitude": lon, "latitude": lat}

            # Get uploaded file from parser
            image_file = request.data.get('image_file')
            if not image_file:
                return Response(
                    {"error": "No image file uploaded"},
                    status=status.HTTP_400_BAD_REQUEST,
                )


            # Upload image to Vultr Object Storage and process with ML APIs
            image_url, species_data, embedding = upload_and_process_image(
                image_file
            )

            # Handle upload or ML API failures
            if not image_url:
                return Response(
                    {"error": "Image upload failed. Please try again."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if not embedding:
                return Response(
                    {
                        "error": "Failed to process image. Please ensure the image is a valid animal photo."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create animal media object with embedding
            animal_media = create_animal_media_with_embedding(image_url, embedding)

            # Extract breed analysis from species data
            breed_analysis = (
                species_data.get("breed_analysis", []) if species_data else []
            )

            # Create sighting record with breed analysis
            sighting = create_sighting_record(
                validated_data, request.user, animal_media, breed_analysis
            )

            # Find similar animal profiles within 30km using breed analysis
            matching_profiles = find_similar_animal_profiles(
                sighting.location, embedding, breed_analysis, radius_km=30, similarity_threshold=0.5
            )

            # Format matching profiles
            formatted_matches = SightingMatchSerializer.format_matching_profiles(
                matching_profiles
            )

            # Serialize response
            serializer = SightingSerializer(sighting)
            response_data = serializer.sighting_with_matches_serializer(
                formatted_matches, species_data
            )

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to create sighting: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class SightingSelectProfileAPI(APIView):
    """API view to link a sighting to an animal profile

    This endpoint handles the final step of the sighting workflow:
    - User selects an existing matching profile, OR
    - User creates a new stray animal profile
    - Sighting gets linked to the selected/created profile

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Link sighting to existing profile or create new stray profile",
        operation_summary="Select/Create Profile for Sighting",
        tags=["Animal Sightings"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["sighting_id", "action"],
            properties={
                "sighting_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the sighting to link",
                ),
                "action": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["select_existing", "create_new"],
                    description="Action to take: select existing profile or create new",
                ),
                "profile_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of existing profile (required if action=select_existing)",
                ),
                "new_profile_data": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    description="New profile data (required if action=create_new)",
                    properties={
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "species": openapi.Schema(type=openapi.TYPE_STRING),
                        "breed": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Sighting linked successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "sighting": openapi.Schema(type=openapi.TYPE_OBJECT),
                        "animal_profile": openapi.Schema(type=openapi.TYPE_OBJECT),
                    },
                ),
            ),
            400: openapi.Response(description="Invalid input data"),
            404: openapi.Response(description="Sighting or profile not found"),
        },
    )
    def post(self, request):
        try:
            # Import utilities here to avoid circular imports
            from .utils import create_stray_animal_profile, link_sighting_to_profile
            from .validator import SightingSelectProfileInputValidator

            # Validate input data
            validated_data = SightingSelectProfileInputValidator(
                request.data
            ).serialized_data()

            # Get sighting object
            try:
                sighting = AnimalSighting.objects.get(
                    id=validated_data["sighting_id"], reporter=request.user
                )
            except AnimalSighting.DoesNotExist:
                return Response(
                    {
                        "error": "Sighting not found or you don't have permission to modify it"
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Check if sighting is already linked
            if sighting.animal:
                return Response(
                    {"error": "Sighting is already linked to an animal profile"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Handle action: select existing or create new
            if validated_data["action"] == "select_existing":
                # Link to existing profile
                try:
                    profile = AnimalProfileModel.objects.get(
                        id=validated_data["profile_id"]
                    )
                except AnimalProfileModel.DoesNotExist:
                    return Response(
                        {"error": "Animal profile not found"},
                        status=status.HTTP_404_NOT_FOUND,
                    )

                link_sighting_to_profile(sighting, profile)
                message = f"Sighting linked to existing profile '{profile.name}'"

            elif validated_data["action"] == "create_new":
                # Create new stray profile with breed analysis from sighting
                profile_data = validated_data["new_profile_data"]
                profile = create_stray_animal_profile(
                    profile_data,
                    sighting.location,
                    request.user,
                    sighting.breed_analysis,
                )
                link_sighting_to_profile(sighting, profile)
                message = (
                    f"New stray animal profile '{profile.name}' created and linked"
                )

            # Serialize response
            response_data = {
                "message": message,
                "sighting": AnimalSightingSerializer(sighting).details_serializer(),
                "animal_profile": AnimalProfileModelSerializer(
                    profile
                ).details_serializer(),
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to link sighting: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class RegisterPetAPI(APIView):
    """API view to register a new pet for the authenticated user

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Register a new pet for the authenticated user",
        operation_summary="Register Pet",
        tags=["Pet Registration"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "species"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Pet name",
                    max_length=255,
                    example="Buddy",
                ),
                "species": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Pet species",
                    max_length=100,
                    example="Dog",
                ),
                "breed": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Pet breed (optional)",
                    max_length=100,
                    example="Golden Retriever",
                ),
                "is_sterilized": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Whether the pet is sterilized",
                    default=False,
                    example=True,
                ),
                "longitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Longitude coordinate (optional)",
                    example=-122.4194,
                ),
                "latitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Latitude coordinate (optional)",
                    example=37.7749,
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Pet registered successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "pet": {
                            "id": 1,
                            "name": "Buddy",
                            "species": "Dog",
                            "breed": "Golden Retriever",
                            "type": "pet",
                            "is_sterilized": True,
                            "owner": {
                                "id": 1,
                                "username": "user123",
                                "name": "John Doe",
                            },
                            "location": {"latitude": 37.7749, "longitude": -122.4194},
                            "created_at": "2023-01-01T12:00:00Z",
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={"application/json": {"error": "Name is required"}},
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "error": "Authentication credentials were not provided"
                    }
                },
            ),
        },
    )
    def post(self, request):
        from .utils import register_pet
        from .validator import RegisterPetInputValidator

        try:
            # Validate input data
            validated_data = RegisterPetInputValidator(request.data).serialized_data()

            # Register the pet
            result = register_pet(validated_data, request.user)

            if result.get("error"):
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to register pet: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UploadImageAPI(APIView):
    """API view to upload images for pets

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]
    parser_classes = [MultiPartParser, FormParser]

    @swagger_auto_schema(
        operation_description="Upload an image for a pet or standalone image",
        operation_summary="Upload Pet Image",
        tags=["Pet Images"],
        manual_parameters=[
            openapi.Parameter(
                "image_file",
                openapi.IN_FORM,
                description="Image file to upload (JPEG, PNG, WEBP, max 10MB)",
                type=openapi.TYPE_FILE,
                required=True,
            ),
            openapi.Parameter(
                "animal_id",
                openapi.IN_FORM,
                description="Animal ID to link the image to (optional)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            201: openapi.Response(
                description="Image uploaded successfully",
                examples={
                    "application/json": {
                        "success": True,
                        "image": {
                            "id": 1,
                            "image_url": "https://storage.vultr.com/bucket/image123.jpg",
                            "animal_id": 1,
                            "uploaded_at": "2023-01-01T12:00:00Z",
                        },
                    }
                },
            ),
            400: openapi.Response(
                description="Validation error",
                examples={"application/json": {"error": "Image File is required"}},
            ),
            401: openapi.Response(
                description="Authentication required",
                examples={
                    "application/json": {
                        "error": "Authentication credentials were not provided"
                    }
                },
            ),
        },
    )
    def post(self, request):
        from .utils import upload_pet_image
        from .validator import UploadImageInputValidator

        try:
            # Validate input data
            validated_data = UploadImageInputValidator(request.data).serialized_data()

            # Upload the image
            result = upload_pet_image(validated_data, request.user)

            if result.get("error"):
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to upload image: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class UserPetsListAPI(APIView):
    """API view to list user's pets

    Methods:
        GET
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get list of pets owned by the authenticated user",
        operation_summary="List User's Pets",
        tags=["User Pets"],
        responses={
            200: openapi.Response(
                description="Successfully retrieved user's pets",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "pets": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "species": openapi.Schema(type=openapi.TYPE_STRING),
                                    "breed": openapi.Schema(type=openapi.TYPE_STRING),
                                    "type": openapi.Schema(type=openapi.TYPE_STRING),
                                    "is_sterilized": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                    "images": openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Schema(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                "id": openapi.Schema(
                                                    type=openapi.TYPE_INTEGER
                                                ),
                                                "image_url": openapi.Schema(
                                                    type=openapi.TYPE_STRING
                                                ),
                                            },
                                        ),
                                    ),
                                    "location": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "latitude": openapi.Schema(
                                                type=openapi.TYPE_NUMBER
                                            ),
                                            "longitude": openapi.Schema(
                                                type=openapi.TYPE_NUMBER
                                            ),
                                        },
                                        nullable=True,
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                    },
                ),
            ),
            401: openapi.Response(description="Authentication required"),
            500: openapi.Response(description="Internal server error"),
        },
    )
    def get(self, request):
        """Get list of pets owned by the authenticated user

        Args:
            request: HTTP request with authenticated user

        Returns:
            Response: List of user's pets with count
        """
        from .utils import get_user_pets

        try:
            result = get_user_pets(request.user)

            if result.get("error"):
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve pets: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MarkPetAsLostAPI(APIView):
    """API view to mark a pet as lost

    Methods:
        POST
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Mark a pet as lost and create an emergency post",
        operation_summary="Mark Pet as Lost",
        tags=["Lost Pets"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["pet_id", "description"],
            properties={
                "pet_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the pet to mark as lost",
                ),
                "description": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Description of the circumstances (minimum 10 characters)",
                ),
                "last_seen_longitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Longitude where pet was last seen (optional)",
                ),
                "last_seen_latitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Latitude where pet was last seen (optional)",
                ),
                "last_seen_time": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    format=openapi.FORMAT_DATETIME,
                    description="When pet was last seen (ISO format, optional)",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Pet marked as lost successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "lost_report": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "pet": openapi.Schema(type=openapi.TYPE_OBJECT),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                                "last_seen_location": openapi.Schema(
                                    type=openapi.TYPE_OBJECT
                                ),
                                "last_seen_time": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "emergency_post": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "emergency_type": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                                "location": openapi.Schema(type=openapi.TYPE_OBJECT),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Validation errors",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            401: openapi.Response(description="Unauthorized"),
            404: openapi.Response(
                description="Pet not found or permission denied",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            500: openapi.Response(description="Internal Server Error"),
        },
    )
    def post(self, request):
        """Mark a pet as lost"""
        if not request.user.is_authenticated:
            return Response(
                {"error": "Authentication required"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            # Validate input data
            validator = MarkPetAsLostInputValidator(request.data)
            validated_data = validator.serialized_data()

            if validator.get_errors():
                return Response(
                    {"error": validator.get_errors()},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mark pet as lost
            result = mark_pet_as_lost(validated_data, request.user)

            if result.get("error"):
                error_msg = result["error"]
                if "not found" in error_msg or "permission" in error_msg:
                    return Response(
                        {"error": error_msg},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                elif "already marked as lost" in error_msg:
                    return Response(
                        {"error": error_msg},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                else:
                    return Response(
                        {"error": error_msg},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    )

            return Response(result, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"error": f"Failed to mark pet as lost: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class NearbyAdoptionsAPI(APIView):
    """API view to get adoption listings from organizations within specified radius

    Methods:
        GET
    """

    authentication_classes = [UserTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get adoption listings from verified organizations within specified radius of user location",
        operation_summary="Get Nearby Adoption Listings",
        tags=["Adoptions"],
        manual_parameters=[
            openapi.Parameter(
                "latitude",
                openapi.IN_QUERY,
                description="User's latitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "longitude",
                openapi.IN_QUERY,
                description="User's longitude coordinate",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
            openapi.Parameter(
                "radius",
                openapi.IN_QUERY,
                description="Search radius in kilometers (default: 20km, max: 100km)",
                type=openapi.TYPE_NUMBER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved nearby adoption listings",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "adoptions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "profile": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "species": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "breed": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "type": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "images": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        "id": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER
                                                        ),
                                                        "image_url": openapi.Schema(
                                                            type=openapi.TYPE_STRING
                                                        ),
                                                    },
                                                ),
                                            ),
                                            "location": openapi.Schema(
                                                type=openapi.TYPE_OBJECT
                                            ),
                                        },
                                    ),
                                    "posted_by": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "email": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "is_verified": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                            "location": openapi.Schema(
                                                type=openapi.TYPE_OBJECT
                                            ),
                                            "address": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                        },
                                    ),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                    "distance_km": openapi.Schema(
                                        type=openapi.TYPE_NUMBER
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "search_radius_km": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "user_location": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "latitude": openapi.Schema(type=openapi.TYPE_NUMBER),
                                "longitude": openapi.Schema(type=openapi.TYPE_NUMBER),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid coordinates/radius"
            ),
            500: openapi.Response(description="Internal Server Error"),
        },
    )
    def get(self, request):
        """Get adoption listings from organizations within specified radius

        Args:
            request: HTTP request with latitude, longitude, and optional radius parameters

        Returns:
            Response: List of nearby adoption listings with organization details and distances
        """
        try:
            # Validate input data
            query_params = {
                "latitude": request.query_params.get("latitude"),
                "longitude": request.query_params.get("longitude"),
                "radius": request.query_params.get("radius", 20),  # Default 20km
            }

            # Convert radius to appropriate type
            if query_params["radius"]:
                try:
                    query_params["radius"] = float(query_params["radius"])
                except (ValueError, TypeError):
                    query_params["radius"] = 20

            validated_data = NearbyAdoptionsInputValidator(
                query_params
            ).serialized_data()

            # Get nearby adoptions
            result = get_nearby_adoptions(
                latitude=validated_data["latitude"],
                longitude=validated_data["longitude"],
                radius_km=validated_data["radius"],
            )

            if "error" in result:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve nearby adoptions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class OrganisationAdoptionsListAPI(APIView):
    """API view to list adoption listings posted by an organization

    Methods:
        GET
    """

    authentication_classes = [OrganisationTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Get list of adoption listings posted by the authenticated organization",
        operation_summary="List Organization's Adoption Listings",
        tags=["Adoptions"],
        responses={
            200: openapi.Response(
                description="Successfully retrieved organization's adoption listings",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "adoptions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "profile": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "species": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "breed": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "type": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "images": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(
                                                    type=openapi.TYPE_OBJECT,
                                                    properties={
                                                        "id": openapi.Schema(
                                                            type=openapi.TYPE_INTEGER
                                                        ),
                                                        "image_url": openapi.Schema(
                                                            type=openapi.TYPE_STRING
                                                        ),
                                                    },
                                                ),
                                            ),
                                            "location": openapi.Schema(
                                                type=openapi.TYPE_OBJECT
                                            ),
                                            "is_sterilized": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                        },
                                    ),
                                    "posted_by": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "id": openapi.Schema(
                                                type=openapi.TYPE_INTEGER
                                            ),
                                            "name": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "email": openapi.Schema(
                                                type=openapi.TYPE_STRING
                                            ),
                                            "is_verified": openapi.Schema(
                                                type=openapi.TYPE_BOOLEAN
                                            ),
                                        },
                                    ),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "updated_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "count": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "organisation": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_verified": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN
                                ),
                            },
                        ),
                    },
                ),
            ),
            401: openapi.Response(description="Authentication failed"),
            500: openapi.Response(description="Internal server error"),
        },
    )
    def get(self, request):
        """Get adoption listings posted by the authenticated organization

        Args:
            request: HTTP request object

        Returns:
            Response: List of adoption listings posted by the organization
        """
        try:
            # Get adoption listings for the authenticated organization
            result = get_organisation_adoptions(organisation=request.user)

            if "error" in result:
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve organization adoptions: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class MarkAdoptionAsAdoptedAPI(APIView):
    """API view to mark an adoption listing as adopted

    Methods:
        PATCH
    """

    authentication_classes = [OrganisationTokenAuthentication]

    @swagger_auto_schema(
        operation_description="Mark an adoption listing as adopted. Only the organization that posted the adoption can mark it as adopted.",
        operation_summary="Mark Adoption as Adopted",
        tags=["Adoptions"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["adoption_id"],
            properties={
                "adoption_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID of the adoption listing to mark as adopted",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successfully marked adoption as adopted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "adoption": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "profile": openapi.Schema(type=openapi.TYPE_OBJECT),
                                "posted_by": openapi.Schema(type=openapi.TYPE_OBJECT),
                                "description": openapi.Schema(type=openapi.TYPE_STRING),
                                "status": openapi.Schema(type=openapi.TYPE_STRING),
                                "created_at": openapi.Schema(type=openapi.TYPE_STRING),
                                "updated_at": openapi.Schema(type=openapi.TYPE_STRING),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(description="Invalid input data"),
            401: openapi.Response(description="Authentication failed"),
            404: openapi.Response(
                description="Adoption listing not found or no permission"
            ),
            500: openapi.Response(description="Internal server error"),
        },
    )
    def patch(self, request):
        """Mark an adoption listing as adopted

        Args:
            request: HTTP request object

        Returns:
            Response: Updated adoption details or error response
        """
        try:
            # Validate input data
            validated_data = MarkAdoptionAsAdoptedInputValidator(
                request.data
            ).serialized_data()

            # Check for validation errors
            if "error" in validated_data:
                return Response(validated_data, status=status.HTTP_400_BAD_REQUEST)

            # Mark adoption as adopted
            result = mark_adoption_as_adopted(
                adoption_id=validated_data["adoption_id"],
                organisation=request.user,
            )

            if "error" in result:
                # Check if it's a not found error
                if "not found" in result["error"] or "permission" in result["error"]:
                    return Response(
                        {"error": result["error"]},
                        status=status.HTTP_404_NOT_FOUND,
                    )
                return Response(
                    {"error": result["error"]},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to mark adoption as adopted: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
