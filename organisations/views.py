from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

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
