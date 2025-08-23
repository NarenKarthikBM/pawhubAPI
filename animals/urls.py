from django.urls import path

from . import views

urlpatterns = [
    path(
        "profiles/",
        views.AnimalProfileListAPI.as_view(),
        name="animal-profiles-list",
    ),
    path(
        "sightings/",
        views.AnimalSightingListAPI.as_view(),
        name="animal-sightings-list",
    ),
    path(
        "sightings/nearby/",
        views.NearbySightingsAPI.as_view(),
        name="nearby-sightings",
    ),
    path(
        "emergencies/",
        views.EmergencyListAPI.as_view(),
        name="emergencies-list",
    ),
    path(
        "lost/",
        views.LostPetListAPI.as_view(),
        name="lost-pets-list",
    ),
    path(
        "adoptions/",
        views.AdoptionListAPI.as_view(),
        name="adoptions-list",
    ),
]
