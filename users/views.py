from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView

from users.utils import authorize_user, register_user
from users.validator import (
    UserObtainAuthTokenInputValidator,
    UserRegistrationInputValidator,
)


class UserObtainAuthTokenAPI(APIView):
    """API view to obtain auth tokens

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Obtain authentication tokens for user login",
        operation_summary="User Login",
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User email address",
                    example="user@example.com",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User password",
                    example="securepassword123",
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
                        "user_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "date_joined": openapi.Schema(
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
            - password

        Output Serializer:
            - tokens
            - User Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - User not found (email field)
                - incorrect password (password field)
            - Successes
                - tokens and user details

        """

        validated_data = UserObtainAuthTokenInputValidator(
            request.data
        ).serialized_data()
        user_authorization = authorize_user(validated_data)

        if not user_authorization:
            raise ValidationError({"error": "user not found", "field": "email"})

        if "error" in user_authorization:
            raise ValidationError({"error": "incorrect password", "field": "password"})

        return Response(user_authorization, status=status.HTTP_200_OK)


class UserRegistrationAPI(APIView):
    """API view to register a new user

    Methods:
        POST
    """

    permission_classes = []
    authentication_classes = []

    @swagger_auto_schema(
        operation_description="Register a new user account",
        operation_summary="User Registration",
        tags=["Authentication"],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["email", "password", "username", "name"],
            properties={
                "email": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User email address",
                    example="user@example.com",
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User password (minimum 8 characters)",
                    example="securepassword123",
                ),
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Unique username (3-20 characters)",
                    example="john_doe",
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="User full name",
                    example="John Doe",
                ),
            },
        ),
        responses={
            201: openapi.Response(
                description="User successfully registered",
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
                        "user_details": openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                "id": openapi.Schema(type=openapi.TYPE_INTEGER),
                                "name": openapi.Schema(type=openapi.TYPE_STRING),
                                "email": openapi.Schema(type=openapi.TYPE_STRING),
                                "username": openapi.Schema(type=openapi.TYPE_STRING),
                                "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                "date_joined": openapi.Schema(
                                    type=openapi.TYPE_STRING, format="date-time"
                                ),
                            },
                        ),
                    },
                ),
                examples={
                    "application/json": {
                        "tokens": {
                            "auth_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                            "device_token": "device_abc123",
                        },
                        "user_details": {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "username": "john_doe",
                            "is_active": True,
                            "date_joined": "2025-08-23T10:30:00Z",
                        },
                    }
                },
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
        """POST Method to register a new user account

        Input Serializer:
            - email
            - password
            - username
            - name

        Output Serializer:
            - tokens
            - User Serializer (details_serializer)

        Possible Outputs:
            - Errors
                - Email already exists (email field)
                - Username already exists (username field)
                - Validation errors (various fields)
            - Success
                - tokens and user details

        """

        validated_data = UserRegistrationInputValidator(request.data).serialized_data()

        user_registration = register_user(validated_data)

        if "error" in user_registration:
            raise ValidationError(
                {
                    "error": user_registration["error"],
                    "field": user_registration["field"],
                }
            )

        return Response(user_registration, status=status.HTTP_201_CREATED)
