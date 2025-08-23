import secrets

from organisations.models import (
    Organisation,
    OrganisationAuthTokens,
)
from organisations.serializers import OrganisationSerializer


def generate_tokens():
    return {
        "auth_token": secrets.token_urlsafe(120),
        "device_token": secrets.token_urlsafe(16),
    }


def generate_otp():
    generateSecrets = secrets.SystemRandom()
    return generateSecrets.randint(100000, 999999)


def authorize_organisation(data):
    organisation = Organisation.objects.filter(email=data["email"]).first()

    if not organisation:
        return None

    # Check if organisation is verified
    if not organisation.is_verified:
        return {"error": "Organisation not verified"}

    # For now, we'll use a simple password check - you might want to implement proper password handling
    # Since Organisation model doesn't inherit from AbstractBaseUser, we need a different approach
    # This is a placeholder - implement proper authentication logic based on your requirements

    tokens = generate_tokens()

    OrganisationAuthTokens(
        organisation=organisation,
        auth_token=tokens["auth_token"],
        device_token=tokens["device_token"],
        type="web",
    ).save()

    return {
        "tokens": tokens,
        "organisation_details": OrganisationSerializer(
            organisation
        ).details_serializer(),
    }


def revoke_organisation_tokens(auth_token, device_token):
    OrganisationAuthTokens.objects.filter(
        auth_token=auth_token, device_token=device_token
    ).delete()


def create_organisation(name, email, address=None, latitude=None, longitude=None):
    organisation = Organisation(
        name=name,
        email=email,
        address=address or "",
        location_latitude=latitude,
        location_longitude=longitude,
    )
    organisation.save()

    return organisation
