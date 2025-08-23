from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from pawhubAPI.settings.custom_DRF_settings.authentication import (
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
