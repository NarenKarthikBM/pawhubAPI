from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

from vets.models import Vet, VetVerification
from vets.serializers import VetSerializer
from vets.utils import authorize_vet, create_vet
from vets.validator import (
    VetObtainAuthTokenInputValidator,
    VetRegistrationInputValidator,
    VetVerificationInputValidator,
)


class VetObtainAuthTokenAPI(APIView):
    """API view to obtain auth tokens for vets

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Obtain authentication tokens for vet login",
        operation_summary="Vet Login",
        tags=["Vet Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Vet email address",
                    example="vet@example.com",
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
                        "vet_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "license_number": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "specialization": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "clinic_name": openapi.Schema(type=openapi.TYPE_STRING),
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
                                "years_of_experience": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
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
            - Vet Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - Vet not found (email field)
                - Vet not verified (email field)
            - Successes
                - tokens and vet details

        """

        validated_data = VetObtainAuthTokenInputValidator(
            request.data
        ).serialized_data()
        vet_authorization = authorize_vet(validated_data)

        if not vet_authorization:
            raise ValidationError({"error": "vet not found", "field": "email"})

        if "error" in vet_authorization:
            raise ValidationError(
                {"error": vet_authorization["error"], "field": "email"}
            )

        return Response(vet_authorization, status=status.HTTP_200_OK)


class VetRegistrationAPI(APIView):
    """API view to register vets

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Register a new vet",
        operation_summary="Vet Registration",
        tags=["Vet Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["name", "email"],
            properties={
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Vet name",
                    example="Dr. Jane Smith",
                ),
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Vet email address",
                    example="dr.jane@vetclinic.com",
                ),
                "phone_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Phone number",
                    example="+1234567890",
                ),
                "license_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Veterinary license number",
                    example="VET123456",
                ),
                "specialization": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Veterinary specialization",
                    example="Small Animal Medicine",
                ),
                "clinic_name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Clinic name",
                    example="Happy Paws Veterinary Clinic",
                ),
                "address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Vet address",
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
                "years_of_experience": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Years of experience",
                    example=5,
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="Vet successfully registered",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "vet_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "phone_number": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "license_number": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "specialization": openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                                "clinic_name": openapi.Schema(type=openapi.TYPE_STRING),
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
                                "years_of_experience": openapi.Schema(
                                    type=openapi.TYPE_INTEGER
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
        """POST Method to register a new vet

        Input Serializer:
            - name
            - email
            - phone_number (optional)
            - license_number (optional)
            - specialization (optional)
            - clinic_name (optional)
            - address (optional)
            - latitude (optional)
            - longitude (optional)
            - years_of_experience (optional)

        Output Serializer:
            - Vet Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - Validation errors
                - Email already exists
            - Successes
                - vet details

        """

        validated_data = VetRegistrationInputValidator(request.data).serialized_data()

        # Check if vet with this email already exists
        if Vet.objects.filter(email=validated_data["email"]).exists():
            raise ValidationError(
                {"error": "vet with this email already exists", "field": "email"}
            )

        # Check if license number is provided and already exists
        if (
            validated_data.get("license_number")
            and Vet.objects.filter(
                license_number=validated_data["license_number"]
            ).exists()
        ):
            raise ValidationError(
                {
                    "error": "vet with this license number already exists",
                    "field": "license_number",
                }
            )

        vet = create_vet(
            name=validated_data["name"],
            email=validated_data["email"],
            phone_number=validated_data.get("phone_number"),
            license_number=validated_data.get("license_number"),
            specialization=validated_data.get("specialization"),
            clinic_name=validated_data.get("clinic_name"),
            address=validated_data.get("address"),
            latitude=validated_data.get("latitude"),
            longitude=validated_data.get("longitude"),
            years_of_experience=validated_data.get("years_of_experience"),
        )

        return Response(
            {"vet_details": VetSerializer(vet).details_serializer()},
            status=status.HTTP_201_CREATED,
        )


class VetVerificationAPI(APIView):
    """API view to submit vet verification

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Submit vet verification documents",
        operation_summary="Vet Verification",
        tags=["Vet Management"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["vet_id"],
            properties={
                "vet_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER, description="Vet ID", example=1
                ),
                "verification_text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Verification text in markdown format",
                    example="## About My Practice\n\nI am a licensed veterinarian...",
                ),
                "verification_document_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="URL to verification document",
                    example="https://example.com/documents/verification.pdf",
                ),
                "license_document_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="URL to license document",
                    example="https://example.com/documents/license.pdf",
                ),
                "education_certificates_url": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="URL to education certificates",
                    example="https://example.com/documents/education.pdf",
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
                description="Vet not found",
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
        """POST Method to submit vet verification

        Input Serializer:
            - vet_id
            - verification_text (optional)
            - verification_document_url (optional)
            - license_document_url (optional)
            - education_certificates_url (optional)

        Output Serializer:
            - Success message

        Possible Outputs:
            - Errors
                - Vet not found
                - Validation errors
            - Successes
                - Verification submitted message

        """

        vet_id = request.data.get("vet_id")

        if not vet_id:
            raise ValidationError({"error": "vet_id is required", "field": "vet_id"})

        try:
            vet = Vet.objects.get(id=vet_id)
        except Vet.DoesNotExist:
            return Response(
                {"error": "vet not found"}, status=status.HTTP_404_NOT_FOUND
            )

        validated_data = VetVerificationInputValidator(request.data).serialized_data()

        # Create or update verification
        verification, created = VetVerification.objects.get_or_create(
            vet=vet,
            defaults={
                "verification_text": validated_data["verification_text"],
                "verification_document_url": validated_data[
                    "verification_document_url"
                ],
                "license_document_url": validated_data["license_document_url"],
                "education_certificates_url": validated_data[
                    "education_certificates_url"
                ],
            },
        )

        if not created:
            verification.verification_text = validated_data["verification_text"]
            verification.verification_document_url = validated_data[
                "verification_document_url"
            ]
            verification.license_document_url = validated_data["license_document_url"]
            verification.education_certificates_url = validated_data[
                "education_certificates_url"
            ]
            verification.save()

        return Response(
            {"message": "Verification submitted successfully"},
            status=status.HTTP_201_CREATED,
        )
