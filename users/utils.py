import secrets

from users.models import (
    CustomUser,
    UserAuthTokens,
)
from users.serializers import UserSerializer


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


def create_user(email, name, username, password):
    """Create a new user with the provided details"""
    user = CustomUser(
        email=email,
        name=name,
        username=username,
    )
    user.set_password(password)
    user.save()

    return user


def register_user(data):
    """Register a new user and generate auth tokens"""
    # Check if user with email already exists
    if CustomUser.objects.filter(email=data["email"]).exists():
        return {"error": "User with this email already exists", "field": "email"}

    # Check if user with username already exists
    if CustomUser.objects.filter(username=data["username"]).exists():
        return {"error": "User with this username already exists", "field": "username"}

    # Create the user
    user = create_user(
        email=data["email"],
        name=data["name"],
        username=data["username"],
        password=data["password"],
    )

    # Generate tokens for the newly created user
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
