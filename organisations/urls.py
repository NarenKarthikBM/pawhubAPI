from django.urls import path

from . import views

urlpatterns = [
    path(
        "obtain-auth-token/",
        views.OrganisationObtainAuthTokenAPI.as_view(),
        name="organisation-obtain-auth-token",
    ),
    path(
        "register/",
        views.OrganisationRegistrationAPI.as_view(),
        name="organisation-register",
    ),
    path(
        "verification/",
        views.OrganisationVerificationAPI.as_view(),
        name="organisation-verification",
    ),
    path(
        "missions/",
        views.OrganisationMissionsListAPI.as_view(),
        name="organisation-missions-list",
    ),
    path(
        "missions/nearby/",
        views.NearbyMissionsAPI.as_view(),
        name="nearby-missions",
    ),
    path(
        "sightings-emergencies/nearby/",
        views.NearbySightingsAndEmergenciesAPI.as_view(),
        name="nearby-sightings-emergencies",
    ),
]
