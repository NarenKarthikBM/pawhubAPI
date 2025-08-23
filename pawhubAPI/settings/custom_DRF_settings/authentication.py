from rest_framework import authentication, exceptions

from organisations.models import OrganisationAuthTokens
from users.models import UserAuthToken
from vets.models import VetAuthTokens


class UserTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_token, device_token = (
            request.META.get("HTTP_AUTHORIZATION"),
            request.META.get("HTTP_DEVICE_TOKEN"),
        )
        if not auth_token or not device_token:
            return None

        try:
            user_auth_token = UserAuthToken.objects.get(
                auth_token=auth_token, device_token=device_token
            )
        except UserAuthToken.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user_auth_token.user, None)


class OrganisationTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_token, device_token = (
            request.META.get("HTTP_AUTHORIZATION"),
            request.META.get("HTTP_DEVICE_TOKEN"),
        )
        if not auth_token or not device_token:
            return None

        try:
            user_auth_token = OrganisationAuthTokens.objects.get(
                auth_token=auth_token, device_token=device_token
            )
        except OrganisationAuthTokens.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user_auth_token.user, None)


class VetTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_token, device_token = (
            request.META.get("HTTP_AUTHORIZATION"),
            request.META.get("HTTP_DEVICE_TOKEN"),
        )
        if not auth_token or not device_token:
            return None

        try:
            user_auth_token = VetAuthTokens.objects.get(
                auth_token=auth_token, device_token=device_token
            )
        except VetAuthTokens.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user_auth_token.user, None)
