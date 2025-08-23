from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    Adoption,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
    Lost,
)
from .serializers import (
    AdoptionSerializer,
    AnimalProfileModelSerializer,
    AnimalSightingSerializer,
    EmergencySerializer,
    LostSerializer,
)


class AnimalProfileListAPI(APIView):
    """API view to list and create animal profiles

    Methods:
        GET, POST
    """

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

    @swagger_auto_schema(
        operation_description="Create a new animal profile",
        operation_summary="Create Animal Profile",
        tags=["Animal Profiles"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "species", "type"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING, description="Animal name", example="Buddy"
                ),
                "type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Animal type",
                    enum=["pet", "stray"],
                ),
                "species": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Animal species",
                    example="Dog",
                ),
                "breed": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Animal breed",
                    example="Golden Retriever",
                ),
                "is_sterilized": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN, description="Is the animal sterilized"
                ),
                "location": openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "latitude": openapi.Schema(type=openapi.TYPE_NUMBER),
                        "longitude": openapi.Schema(type=openapi.TYPE_NUMBER),
                    },
                ),
                "owner_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Owner ID (for pets only)"
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Animal profile created successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                        "name": openapi.Schema(type=openapi.TYPE_STRING),
                        "species": openapi.Schema(type=openapi.TYPE_STRING),
                        "type": openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """POST Method to create a new animal profile"""

        data = request.data
        profile = AnimalProfileModel.objects.create(
            name=data.get("name"),
            type=data.get("type"),
            species=data.get("species"),
            breed=data.get("breed", ""),
            is_sterilized=data.get("is_sterilized", False),
        )

        # Set location if provided
        location = data.get("location")
        if location:
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            if latitude is not None and longitude is not None:
                profile.set_location(longitude, latitude)
                profile.save()

        # Set owner if provided (for pets)
        owner_id = data.get("owner_id")
        if owner_id and data.get("type") == "pet":
            from users.models import CustomUser

            try:
                owner = CustomUser.objects.get(id=owner_id)
                profile.owner = owner
                profile.save()
            except CustomUser.DoesNotExist:
                pass

        return Response(
            AnimalProfileModelSerializer(profile).details_serializer(),
            status=status.HTTP_201_CREATED,
        )


class AnimalSightingListAPI(APIView):
    """API view to list and create animal sightings

    Methods:
        GET, POST
    """

    @swagger_auto_schema(
        operation_description="Get list of all animal sightings",
        operation_summary="List Animal Sightings",
        tags=["Animal Sightings"],
        responses={
            200: openapi.Response(
                description="Successfully retrieved animal sightings",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "animal": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "species": openapi.Schema(type=openapi.TYPE_STRING),
                                },
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
                            ),
                            "reporter": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "username": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
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
        """GET Method to retrieve all animal sightings"""

        sightings = AnimalSighting.objects.all().order_by("-created_at")
        sightings_data = [
            AnimalSightingSerializer(sighting).details_serializer()
            for sighting in sightings
        ]

        return Response(sightings_data, status=status.HTTP_200_OK)


class EmergencyListAPI(APIView):
    """API view to list and create emergencies

    Methods:
        GET, POST
    """

    @swagger_auto_schema(
        operation_description="Get list of all emergencies",
        operation_summary="List Emergencies",
        tags=["Emergencies"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=["active", "resolved"],
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved emergencies",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "reporter": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "username": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
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
                            ),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
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
        """GET Method to retrieve all emergencies"""

        emergencies = Emergency.objects.all().order_by("-created_at")

        # Apply filters
        status_filter = request.query_params.get("status")
        if status_filter:
            emergencies = emergencies.filter(status=status_filter)

        emergencies_data = [
            EmergencySerializer(emergency).details_serializer()
            for emergency in emergencies
        ]

        return Response(emergencies_data, status=status.HTTP_200_OK)


class LostPetListAPI(APIView):
    """API view to list and create lost pet reports

    Methods:
        GET, POST
    """

    @swagger_auto_schema(
        operation_description="Get list of all lost pets",
        operation_summary="List Lost Pets",
        tags=["Lost Pets"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=["active", "found"],
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved lost pets",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "pet": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "species": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                            "last_seen_time": openapi.Schema(
                                type=openapi.TYPE_STRING, format="date-time"
                            ),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
        },
    )
    def get(self, request):
        """GET Method to retrieve all lost pets"""

        lost_pets = Lost.objects.all().order_by("-created_at")

        # Apply filters
        status_filter = request.query_params.get("status")
        if status_filter:
            lost_pets = lost_pets.filter(status=status_filter)

        lost_pets_data = [
            LostSerializer(lost_pet).details_serializer() for lost_pet in lost_pets
        ]

        return Response(lost_pets_data, status=status.HTTP_200_OK)


class AdoptionListAPI(APIView):
    """API view to list and create adoption listings

    Methods:
        GET, POST
    """

    @swagger_auto_schema(
        operation_description="Get list of all adoption listings",
        operation_summary="List Adoption Listings",
        tags=["Adoptions"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status",
                type=openapi.TYPE_STRING,
                enum=["available", "adopted"],
            ),
            openapi.Parameter(
                "species",
                openapi.IN_QUERY,
                description="Filter by animal species",
                type=openapi.TYPE_STRING,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved adoption listings",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "profile": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                    "species": openapi.Schema(type=openapi.TYPE_STRING),
                                    "breed": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                            "posted_by": openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "name": openapi.Schema(type=openapi.TYPE_STRING),
                                },
                            ),
                            "status": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
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
        """GET Method to retrieve all adoption listings"""

        adoptions = Adoption.objects.all().order_by("-created_at")

        # Apply filters
        status_filter = request.query_params.get("status")
        if status_filter:
            adoptions = adoptions.filter(status=status_filter)

        species = request.query_params.get("species")
        if species:
            adoptions = adoptions.filter(profile__species__icontains=species)

        adoptions_data = [
            AdoptionSerializer(adoption).details_serializer() for adoption in adoptions
        ]

        return Response(adoptions_data, status=status.HTTP_200_OK)
