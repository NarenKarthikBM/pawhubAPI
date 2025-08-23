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
]
