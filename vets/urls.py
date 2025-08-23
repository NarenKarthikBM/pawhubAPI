from django.urls import path

from . import views

urlpatterns = [
    path(
        "obtain-auth-token/",
        views.VetObtainAuthTokenAPI.as_view(),
        name="vet-obtain-auth-token",
    ),
    path(
        "register/",
        views.VetRegistrationAPI.as_view(),
        name="vet-register",
    ),
    path(
        "verification/",
        views.VetVerificationAPI.as_view(),
        name="vet-verification",
    ),
]
