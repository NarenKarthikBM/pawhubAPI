from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

from organisations.models import Organisation, OrganisationVerification
from organisations.serializers import OrganisationSerializer
from organisations.utils import authorize_organisation, create_organisation
from organisations.validator import (
    OrganisationObtainAuthTokenInputValidator,
    OrganisationRegistrationInputValidator,
    OrganisationVerificationInputValidator,
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
