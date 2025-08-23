from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    Adoption,
    AnimalMedia,
    AnimalProfileModel,
    AnimalSighting,
    Emergency,
    Lost,
)


@admin.register(AnimalMedia)
class AnimalMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "animal", "uploaded_at")
    list_filter = ("uploaded_at",)
    search_fields = ("animal__name",)
    readonly_fields = ("uploaded_at",)


@admin.register(AnimalProfileModel)
class AnimalProfileModelAdmin(GISModelAdmin):
    list_display = (
        "name",
        "species",
        "breed",
        "type",
        "owner",
        "is_sterilized",
        "created_at",
    )
    list_filter = ("type", "species", "is_sterilized", "created_at")
    search_fields = ("name", "species", "breed", "owner__username")
    readonly_fields = ("created_at", "updated_at", "latitude", "longitude")
    filter_horizontal = ("images",)
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,  # Default to San Francisco
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(AnimalSighting)
class AnimalSightingAdmin(GISModelAdmin):
    list_display = ("id", "animal", "reporter", "created_at")
    list_filter = ("created_at",)
    search_fields = ("animal__name", "reporter__username")
    readonly_fields = ("created_at", "latitude", "longitude")
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(Emergency)
class EmergencyAdmin(GISModelAdmin):
    list_display = ("id", "reporter", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("reporter__username", "description")
    readonly_fields = ("created_at", "updated_at", "latitude", "longitude")
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(Lost)
class LostAdmin(GISModelAdmin):
    list_display = ("pet", "status", "last_seen_time", "created_at")
    list_filter = ("status", "created_at", "last_seen_time")
    search_fields = ("pet__name", "description")
    readonly_fields = (
        "created_at",
        "updated_at",
        "last_seen_latitude",
        "last_seen_longitude",
    )
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(Adoption)
class AdoptionAdmin(admin.ModelAdmin):
    list_display = ("profile", "posted_by", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("profile__name", "posted_by__name", "description")
    readonly_fields = ("created_at", "updated_at")
