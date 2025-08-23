from rest_framework import status
from rest_framework.response import Response
from rest_framework.validators import ValidationError
from rest_framework.views import APIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import CustomUser
from users.serializers import UserSerializer
from users.utils import authorize_user
from users.validator import UserObtainAuthTokenInputValidator


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
            required=['email', 'password'],
            properties={
                'email': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User email address',
                    example='user@example.com'
                ),
                'password': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='User password',
                    example='securepassword123'
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description="Successfully authenticated",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'tokens': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'auth_token': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description='Authentication token'
                                ),
                                'device_token': openapi.Schema(
                                    type=openapi.TYPE_STRING,
                                    description='Device token'
                                ),
                            }
                        ),
                        'user_details': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(type=openapi.TYPE_INTEGER),
                                'name': openapi.Schema(type=openapi.TYPE_STRING),
                                'email': openapi.Schema(type=openapi.TYPE_STRING),
                                'username': openapi.Schema(type=openapi.TYPE_STRING),
                                'is_active': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                'date_joined': openapi.Schema(type=openapi.TYPE_STRING, format='date-time'),
                            }
                        ),
                    }
                )
            ),
            400: openapi.Response(
                description="Validation error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'error': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Error message'
                        ),
                        'field': openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description='Field that caused the error'
                        ),
                    }
                )
            ),
        }
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
