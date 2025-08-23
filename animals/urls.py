from django.urls import path

from . import views

urlpatterns = [
    path(
        "profiles/",
        views.AnimalProfileListAPI.as_view(),
        name="animal-profiles-list",
    ),
    path(
        "sightings/nearby/",
        views.NearbySightingsAPI.as_view(),
        name="nearby-sightings",
    ),
    path(
        "sightings/create/",
        views.CreateSightingAPI.as_view(),
        name="create-sighting",
    ),
    path(
        "sightings/select-profile/",
        views.SightingSelectProfileAPI.as_view(),
        name="sighting-select-profile",
    ),
    path(
        "emergencies/nearby/",
        views.NearbyEmergenciesAPI.as_view(),
        name="nearby-emergencies",
    ),
    path(
        "emergencies/",
        views.EmergencyCreateAPI.as_view(),
        name="emergency-create",
    ),
]
