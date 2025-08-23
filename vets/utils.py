import secrets

from vets.models import (
    Vet,
    VetAuthTokens,
)
from vets.serializers import VetSerializer


def generate_tokens():
    return {
        "auth_token": secrets.token_urlsafe(120),
        "device_token": secrets.token_urlsafe(16),
    }


def generate_otp():
    generateSecrets = secrets.SystemRandom()
    return generateSecrets.randint(100000, 999999)


def authorize_vet(data):
    vet = Vet.objects.filter(email=data["email"]).first()

    if not vet:
        return None

    # Check if vet is verified
    if not vet.is_verified:
        return {"error": "Vet not verified"}

    # For now, we'll use a simple email-based auth - you might want to implement proper password handling
    # Since Vet model doesn't inherit from AbstractBaseUser, we need a different approach
    # This is a placeholder - implement proper authentication logic based on your requirements

    tokens = generate_tokens()

    VetAuthTokens(
        vet=vet,
        auth_token=tokens["auth_token"],
        device_token=tokens["device_token"],
        type="web",
    ).save()

    return {
        "tokens": tokens,
        "vet_details": VetSerializer(vet).details_serializer(),
    }


def revoke_vet_tokens(auth_token, device_token):
    VetAuthTokens.objects.filter(
        auth_token=auth_token, device_token=device_token
    ).delete()


def create_vet(
    name,
    email,
    phone_number=None,
    license_number=None,
    specialization=None,
    clinic_name=None,
    address=None,
    latitude=None,
    longitude=None,
    years_of_experience=None,
):
    vet = Vet(
        name=name,
        email=email,
        phone_number=phone_number or "",
        license_number=license_number or "",
        specialization=specialization or "",
        clinic_name=clinic_name or "",
        address=address or "",
        years_of_experience=years_of_experience,
    )

    # Set location using the new PointField
    if latitude is not None and longitude is not None:
        vet.set_location(longitude, latitude)

    vet.save()

    return vet
