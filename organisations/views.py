from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

from animals.models import AnimalSighting, Emergency
from animals.serializers import AnimalSightingSerializer, EmergencySerializer
from organisations.models import (
    Organisation,
    OrganisationMissions,
    OrganisationVerification,
)
from organisations.serializers import (
    OrganisationMissionsSerializer,
    OrganisationSerializer,
)
from organisations.utils import authorize_organisation, create_organisation
from organisations.validator import (
    OrganisationObtainAuthTokenInputValidator,
    OrganisationRegistrationInputValidator,
    OrganisationVerificationInputValidator,
)
from pawhubAPI.settings.custom_DRF_settings.authentication import (
    OrganisationTokenAuthentication,
    UserTokenAuthentication,
)


class OrganisationObtainAuthTokenAPI(APIView):
    """API view to obtain auth tokens for organisations

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Obtain authentication tokens for organisation login",
        operation_summary="Organisation Login",
        tags=["Organisation Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Organisation email address",
                    example="org@example.com",
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successfully authenticated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "tokens": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "auth_token": openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description="Authentication token",
                                ),
                                "device_token": openapi.Schema(
                                    type=openapi.TYPE_STRING, description="Device token"
                                ),
                            },
                        ),
                        "organisation_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "address": openapi.Schema(type=openapi.TYPE_STRING),
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
                                "is_verified": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN
                                ),
                                "date_joined": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                                "last_updated_at": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                        "field": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Field that caused the error",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """POST Method to generate and serve the auth tokens

        Input Serializer:
            - email

        Output Serializer:
            - tokens
            - Organisation Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - Organisation not found (email field)
                - Organisation not verified (email field)
            - Successes
                - tokens and organisation details

        """

        validated_data = OrganisationObtainAuthTokenInputValidator(
            request.data
        ).serialized_data()
        organisation_authorization = authorize_organisation(validated_data)

        if not organisation_authorization:
            raise ValidationError({"error": "organisation not found", "field": "email"})

        if "error" in organisation_authorization:
            raise ValidationError(
                {"error": organisation_authorization["error"], "field": "email"}
            )

        return Response(organisation_authorization, status=status.HTTP_200_OK)


class OrganisationRegistrationAPI(APIView):
    """API view to register organisations

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Register a new organisation",
        operation_summary="Organisation Registration",
        tags=["Organisation Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Organisation name",
                    example="Example Organization",
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Organisation email address",
                    example="contact@example.com",
                ),
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Organisation address",
                    example="123 Main St, City, Country",
                ),
                "latitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Latitude coordinate",
                    example=40.7128,
                ),
                "longitude": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Longitude coordinate",
                    example=-74.0060,
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Organisation successfully registered",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "organisation_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "address": openapi.Schema(type=openapi.TYPE_STRING),
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
                                "is_verified": openapi.Schema(
                                    type=openapi.TYPE_BOOLEAN
                                ),
                                "date_joined": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                                "last_updated_at": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                            },
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                        "field": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Field that caused the error",
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """POST Method to register a new organisation

        Input Serializer:
            - name
            - email
            - address (optional)
            - latitude (optional)
            - longitude (optional)

        Output Serializer:
            - Organisation Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - Validation errors
                - Email already exists
            - Successes
                - organisation details

        """

        validated_data = OrganisationRegistrationInputValidator(
            request.data
        ).serialized_data()

        # Check if organisation with this email already exists
        if Organisation.objects.filter(email=validated_data["email"]).exists():
            raise ValidationError(
                {
                    "error": "organisation with this email already exists",
                    "field": "email",
                }
            )

        organisation = create_organisation(
            name=validated_data["name"],
            email=validated_data["email"],
            address=validated_data.get("address"),
            latitude=validated_data.get("latitude"),
            longitude=validated_data.get("longitude"),
        )

        return Response(
            {
                "organisation_details": OrganisationSerializer(
                    organisation
                ).details_serializer()
            },
            status=status.HTTP_201_CREATED,
        )


class OrganisationVerificationAPI(APIView):
    """API view to submit organisation verification

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Submit organisation verification documents",
        operation_summary="Organisation Verification",
        tags=["Organisation Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["organisation_id"],
            properties={
                "organisation_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Organisation ID", example=1
                ),
                "verification_text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Verification text in markdown format",
                    example="## About Our Organization\n\nWe are a registered...",
                ),
                "verification_document_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="URL to verification document",
                    example="https://example.com/documents/verification.pdf",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Verification submitted successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Success message"
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                        "field": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Field that caused the error",
                        ),
                    },
                ),
            ),
            404: openapi.Response(
                description="Organisation not found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(
                            type=openapi.TYPE_STRING, description="Error message"
                        ),
                    },
                ),
            ),
        },
    )
    def post(self, request):
        """POST Method to submit organisation verification

        Input Serializer:
            - organisation_id
            - verification_text (optional)
            - verification_document_url (optional)

        Output Serializer:
            - Success message

        Possible Outputs:
            - Errors
                - Organisation not found
                - Validation errors
            - Successes
                - Verification submitted message

        """

        organisation_id = request.data.get("organisation_id")

        if not organisation_id:
            raise ValidationError(
                {"error": "organisation_id is required", "field": "organisation_id"}
            )

        try:
            organisation = Organisation.objects.get(id=organisation_id)
        except Organisation.DoesNotExist:
            return Response(
                {"error": "organisation not found"}, status=status.HTTP_404_NOT_FOUND
            )

        validated_data = OrganisationVerificationInputValidator(
            request.data
        ).serialized_data()

        # Create or update verification
        verification, created = OrganisationVerification.objects.get_or_create(
            organisation=organisation,
            defaults={
                "verification_text": validated_data["verification_text"],
                "verification_document_url": validated_data[
                    "verification_document_url"
                ],
            },
        )

        if not created:
            verification.verification_text = validated_data["verification_text"]
            verification.verification_document_url = validated_data[
                "verification_document_url"
            ]
            verification.save()

        return Response(
            {"message": "Verification submitted successfully"},
            status=status.HTTP_201_CREATED,
        )


class NearbyMissionsAPI(APIView):
    """API view to get upcoming and ongoing organisation missions within 20km of given coordinates

    Gets missions that are active and within the date range (upcoming or ongoing)
    Requires user authentication
    """

    authentication_classes = [UserTokenAuthentication]
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Get upcoming and ongoing organisation missions within 20km of given coordinates",
        operation_summary="Get Nearby Organisation Missions",
        tags=["Organisation Missions"],
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
            openapi.Parameter(
                "mission_type",
                openapi.IN_QUERY,
                description="Filter by mission type (vaccination, adoption, rescue, awareness, feeding, medical, other)",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of nearby organisation missions",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                            "title": openapi.Schema(type=openapi.TYPE_STRING),
                            "description": openapi.Schema(type=openapi.TYPE_STRING),
                            "mission_type": openapi.Schema(type=openapi.TYPE_STRING),
                            "mission_type_display": openapi.Schema(
                                type=openapi.TYPE_STRING
                            ),
                            "city": openapi.Schema(type=openapi.TYPE_STRING),
                            "area": openapi.Schema(type=openapi.TYPE_STRING),
                            "location": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "start_datetime": openapi.Schema(type=openapi.TYPE_STRING),
                            "end_datetime": openapi.Schema(type=openapi.TYPE_STRING),
                            "organisation": openapi.Schema(type=openapi.TYPE_OBJECT),
                            "contact_phone": openapi.Schema(type=openapi.TYPE_STRING),
                            "contact_email": openapi.Schema(type=openapi.TYPE_STRING),
                        },
                    ),
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid coordinates"
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid or missing authentication token"
            ),
        },
    )
    def get(self, request):
        """Get upcoming and ongoing organisation missions within 20km of given coordinates

        Args:
            request: HTTP request with latitude and longitude parameters

        Returns:
            Response: List of nearby organisation missions with organisation details
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

        # Get optional mission type filter
        mission_type = request.query_params.get("mission_type")

        # Create a point from the coordinates
        user_location = Point(longitude, latitude, srid=4326)

        # Get current datetime
        now = timezone.now()

        # Build query filter for missions within 20km
        query_filter = {
            "location__distance_lte": (user_location, D(km=20)),
            "location__isnull": False,  # Only include missions with location data
            "is_active": True,  # Only active missions
            "end_datetime__gte": now,  # Mission hasn't ended yet (upcoming or ongoing)
        }

        # Add mission type filter if provided
        if mission_type and mission_type in dict(
            OrganisationMissions.MISSION_TYPE_CHOICES
        ):
            query_filter["mission_type"] = mission_type

        # Get missions within 20km that are upcoming or ongoing
        nearby_missions = (
            OrganisationMissions.objects.filter(**query_filter)
            .select_related("organisation")
            .order_by("start_datetime")
        )

        # Serialize the data
        missions_data = [
            OrganisationMissionsSerializer(mission).details_serializer()
            for mission in nearby_missions
        ]

        return Response(missions_data, status=status.HTTP_200_OK)


class NearbySightingsAndEmergenciesAPI(APIView):
    """API view to get animal sightings and emergencies within specified radius for organizations

    Methods:
        GET
    """

    @swagger_auto_schema(
        operation_description="Get animal sightings and emergencies within specified radius",
        operation_summary="Get Nearby Sightings and Emergencies for Organizations",
        tags=["Organization Operations"],
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
            openapi.Parameter(
                "radius",
                openapi.IN_QUERY,
                description="Radius in kilometers",
                type=openapi.TYPE_NUMBER,
                required=True,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of nearby animal sightings and emergencies",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "sightings": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "animal": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "location": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "image": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "reporter": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                        "emergencies": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "emergency_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "reporter": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "location": openapi.Schema(
                                        type=openapi.TYPE_OBJECT
                                    ),
                                    "image": openapi.Schema(type=openapi.TYPE_OBJECT),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "status": openapi.Schema(type=openapi.TYPE_STRING),
                                    "created_at": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                },
                            ),
                        ),
                    },
                ),
            ),
            400: openapi.Response(
                description="Bad Request - Missing or invalid parameters"
            ),
        },
    )
    def get(self, request):
        """Get animal sightings and emergencies within specified radius

        Args:
            request: HTTP request with latitude, longitude, and radius parameters

        Returns:
            Response: Combined list of nearby sightings and emergencies
        """
        # Get latitude, longitude, and radius from query parameters
        try:
            latitude = float(request.query_params.get("latitude"))
            longitude = float(request.query_params.get("longitude"))
            radius = float(request.query_params.get("radius"))
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "latitude, longitude, and radius are required and must be valid numbers"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate radius is positive
        if radius <= 0:
            return Response(
                {"error": "Radius must be a positive number"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a point from the coordinates
        user_location = Point(longitude, latitude, srid=4326)

        # Get sightings within specified radius
        nearby_sightings = (
            AnimalSighting.objects.filter(
                location__distance_lte=(user_location, D(km=radius)),
                animal__isnull=False,  # Only include sightings with associated animals
            )
            .select_related("animal", "image", "reporter")
            .order_by("-created_at")
        )

        # Get emergencies within specified radius
        nearby_emergencies = (
            Emergency.objects.filter(
                location__distance_lte=(user_location, D(km=radius)),
                status="active",  # Only include active emergencies
            )
            .select_related("reporter", "image", "animal")
            .order_by("-created_at")
        )

        # Serialize the data
        sightings_data = [
            AnimalSightingSerializer(sighting).details_serializer()
            for sighting in nearby_sightings
        ]

        emergencies_data = [
            EmergencySerializer(emergency).details_serializer()
            for emergency in nearby_emergencies
        ]

        response_data = {
            "sightings": sightings_data,
            "emergencies": emergencies_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class OrganisationMissionsListAPI(APIView):
    """API view to get missions created by an organisation

    Methods:
        GET
    """

    authentication_classes = [OrganisationTokenAuthentication]
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Get all missions created by the authenticated organisation",
        operation_summary="Get Organisation's Missions List",
        tags=["Organisation Missions"],
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by mission status (upcoming, ongoing, completed, all)",
                type=openapi.TYPE_STRING,
                required=False,
                enum=["upcoming", "ongoing", "completed", "all"],
            ),
            openapi.Parameter(
                "mission_type",
                openapi.IN_QUERY,
                description="Filter by mission type",
                type=openapi.TYPE_STRING,
                required=False,
                enum=[
                    "vaccination",
                    "adoption",
                    "rescue",
                    "awareness",
                    "feeding",
                    "medical",
                    "other",
                ],
            ),
            openapi.Parameter(
                "city",
                openapi.IN_QUERY,
                description="Filter by city",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                "limit",
                openapi.IN_QUERY,
                description="Number of missions to return (default: 20, max: 100)",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
            openapi.Parameter(
                "offset",
                openapi.IN_QUERY,
                description="Number of missions to skip for pagination",
                type=openapi.TYPE_INTEGER,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of organisation missions",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "count": openapi.Schema(
                            type=openapi.TYPE_INTEGER,
                            description="Total number of missions",
                        ),
                        "missions": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    "title": openapi.Schema(type=openapi.TYPE_STRING),
                                    "description": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "mission_type": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "mission_type_display": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "city": openapi.Schema(type=openapi.TYPE_STRING),
                                    "area": openapi.Schema(type=openapi.TYPE_STRING),
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
                                    "start_datetime": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "end_datetime": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "is_active": openapi.Schema(
                                        type=openapi.TYPE_BOOLEAN
                                    ),
                                    "max_participants": openapi.Schema(
                                        type=openapi.TYPE_INTEGER
                                    ),
                                    "contact_phone": openapi.Schema(
                                        type=openapi.TYPE_STRING
                                    ),
                                    "contact_email": openapi.Schema(
                                        type=openapi.TYPE_STRING
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
                    },
                ),
            ),
            401: openapi.Response(
                description="Unauthorized - Invalid or missing authentication token"
            ),
            400: openapi.Response(description="Bad Request - Invalid parameters"),
        },
    )
    def get(self, request):
        """Get all missions created by the authenticated organisation

        Args:
            request: HTTP request with optional filter parameters

        Returns:
            Response: List of organisation's missions with pagination and filtering
        """
        # Get the authenticated organisation
        organisation = request.user

        # Get filter parameters
        status_filter = request.query_params.get("status", "all")
        mission_type = request.query_params.get("mission_type")
        city = request.query_params.get("city")

        # Get pagination parameters
        try:
            limit = min(int(request.query_params.get("limit", 20)), 100)
            offset = int(request.query_params.get("offset", 0))
        except (TypeError, ValueError):
            return Response(
                {"error": "limit and offset must be valid integers"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build base query
        missions_query = OrganisationMissions.objects.filter(organisation=organisation)

        # Apply status filter
        now = timezone.now()
        if status_filter == "upcoming":
            missions_query = missions_query.filter(
                start_datetime__gt=now, is_active=True
            )
        elif status_filter == "ongoing":
            missions_query = missions_query.filter(
                start_datetime__lte=now, end_datetime__gte=now, is_active=True
            )
        elif status_filter == "completed":
            missions_query = missions_query.filter(end_datetime__lt=now)
        elif status_filter == "all":
            # No additional filter for "all"
            pass
        else:
            return Response(
                {
                    "error": "Invalid status filter. Use: upcoming, ongoing, completed, or all"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Apply mission type filter
        if mission_type:
            if mission_type not in dict(OrganisationMissions.MISSION_TYPE_CHOICES):
                return Response(
                    {"error": "Invalid mission type"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            missions_query = missions_query.filter(mission_type=mission_type)

        # Apply city filter
        if city:
            missions_query = missions_query.filter(city__icontains=city)

        # Get total count before pagination
        total_count = missions_query.count()

        # Apply ordering and pagination
        missions = missions_query.order_by("-start_datetime")[offset : offset + limit]

        # Serialize the data
        missions_data = [
            OrganisationMissionsSerializer(
                mission
            ).organisation_owned_missions_serializer()
            for mission in missions
        ]

        response_data = {
            "count": total_count,
            "missions": missions_data,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class OrganisationDashboardStatsAPI(APIView):
    """API view to get dashboard statistics for an organisation

    Methods:
        GET
    """

    authentication_classes = [OrganisationTokenAuthentication]
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Get dashboard statistics for the authenticated organisation including missions, adoption listings, nearby sightings and emergencies",
        operation_summary="Get Organisation Dashboard Statistics",
        tags=["Organisation Dashboard"],
        responses={
            200: openapi.Response(
                description="Dashboard statistics retrieved successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "success": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "stats": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "missions": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "active": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "upcoming": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "completed": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                                "adoptions": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "total_listings": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "active_listings": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "completed_adoptions": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                                "nearby_activity": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "sightings_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "emergencies_count": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "active_emergencies": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                                "recent_activity": openapi.Schema(
                                    type=openapi.TYPE_OBJECT,
                                    properties={
                                        "recent_missions": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "recent_sightings": openapi.Schema(type=openapi.TYPE_INTEGER),
                                        "recent_emergencies": openapi.Schema(type=openapi.TYPE_INTEGER),
                                    },
                                ),
                            },
                        ),
                    },
                ),
            ),
            401: openapi.Response(description="Authentication credentials were not provided"),
        },
    )
    def get(self, request):
        """Get comprehensive dashboard statistics for the organisation"""
        try:
            organisation = request.user
            current_time = timezone.now()
            
            # Calculate date ranges for recent activity (last 7 days)
            seven_days_ago = current_time - timezone.timedelta(days=7)
            
            # Mission Statistics
            all_missions = OrganisationMissions.objects.filter(organisation=organisation)
            total_missions = all_missions.count()
            
            # Active missions (ongoing)
            active_missions = all_missions.filter(
                start_datetime__lte=current_time,
                end_datetime__gte=current_time,
                is_active=True
            ).count()
            
            # Upcoming missions
            upcoming_missions = all_missions.filter(
                start_datetime__gt=current_time,
                is_active=True
            ).count()
            
            # Completed missions
            completed_missions = all_missions.filter(
                end_datetime__lt=current_time
            ).count()
            
            # Adoption Statistics
            from organisations.models import PetAdoptions
            
            all_adoptions = PetAdoptions.objects.filter(organisation=organisation)
            total_adoption_listings = all_adoptions.count()
            active_adoption_listings = all_adoptions.filter(is_adopted=False).count()
            completed_adoptions = all_adoptions.filter(is_adopted=True).count()
            
            # Nearby Activity Statistics (within 20km of organisation location)
            sightings_count = 0
            emergencies_count = 0
            active_emergencies_count = 0
            
            if organisation.location:
                # Get nearby sightings and emergencies within 20km radius
                nearby_sightings = AnimalSighting.objects.filter(
                    location__distance_lte=(organisation.location, D(km=20))
                )
                sightings_count = nearby_sightings.count()
                
                nearby_emergencies = Emergency.objects.filter(
                    location__distance_lte=(organisation.location, D(km=20))
                )
                emergencies_count = nearby_emergencies.count()
                active_emergencies_count = nearby_emergencies.filter(status="active").count()
            
            # Recent Activity Statistics (last 7 days)
            recent_missions = all_missions.filter(
                created_at__gte=seven_days_ago
            ).count()
            
            recent_sightings = 0
            recent_emergencies = 0
            
            if organisation.location:
                recent_sightings = AnimalSighting.objects.filter(
                    location__distance_lte=(organisation.location, D(km=20)),
                    created_at__gte=seven_days_ago
                ).count()
                
                recent_emergencies = Emergency.objects.filter(
                    location__distance_lte=(organisation.location, D(km=20)),
                    created_at__gte=seven_days_ago
                ).count()
            
            # Compile statistics
            stats = {
                "missions": {
                    "total": total_missions,
                    "active": active_missions,
                    "upcoming": upcoming_missions,
                    "completed": completed_missions,
                },
                "adoptions": {
                    "total_listings": total_adoption_listings,
                    "active_listings": active_adoption_listings,
                    "completed_adoptions": completed_adoptions,
                },
                "nearby_activity": {
                    "sightings_count": sightings_count,
                    "emergencies_count": emergencies_count,
                    "active_emergencies": active_emergencies_count,
                },
                "recent_activity": {
                    "recent_missions": recent_missions,
                    "recent_sightings": recent_sightings,
                    "recent_emergencies": recent_emergencies,
                },
            }
            
            response_data = {
                "success": True,
                "message": "Dashboard statistics retrieved successfully",
                "stats": stats,
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            response_data = {
                "success": False,
                "error": f"Failed to retrieve dashboard statistics: {str(e)}",
            }
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
