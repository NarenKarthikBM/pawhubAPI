from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    Organisation,
    OrganisationAuthTokens,
    OrganisationEmailVerificationToken,
    OrganisationMissions,
    OrganisationVerification,
    PetAdoptions,
)


@admin.register(Organisation)
class OrganisationAdmin(GISModelAdmin):
    list_display = ["name", "email", "is_verified", "date_joined"]
    list_filter = ["is_verified", "date_joined"]
    search_fields = ["name", "email"]
    readonly_fields = ["date_joined", "last_updated_at"]
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(OrganisationAuthTokens)
class OrganisationAuthTokensAdmin(admin.ModelAdmin):
    list_display = ["organisation", "type", "created_at", "last_used_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["organisation__name", "organisation__email"]
    readonly_fields = ["auth_token", "device_token", "created_at"]


@admin.register(OrganisationEmailVerificationToken)
class OrganisationEmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["organisation", "created_at", "expires_at"]
    list_filter = ["created_at", "expires_at"]
    search_fields = ["organisation__name", "organisation__email"]
    readonly_fields = ["verification_token", "created_at"]


@admin.register(OrganisationVerification)
class OrganisationVerificationAdmin(admin.ModelAdmin):
    list_display = ["organisation", "submitted_at", "updated_at"]
    list_filter = ["submitted_at", "updated_at"]
    search_fields = ["organisation__name", "organisation__email"]
    readonly_fields = ["submitted_at", "updated_at"]


@admin.register(OrganisationMissions)
class OrganisationMissionsAdmin(GISModelAdmin):
    list_display = [
        "title",
        "organisation",
        "mission_type",
        "city",
        "start_datetime",
        "end_datetime",
        "is_active",
    ]
    list_filter = [
        "mission_type",
        "is_active",
        "city",
        "start_datetime",
        "end_datetime",
    ]
    search_fields = ["title", "description", "organisation__name", "city", "area"]
    readonly_fields = ["created_at", "updated_at"]
    date_hierarchy = "start_datetime"
    gis_widget_kwargs = {
        "attrs": {
            "default_lat": 37.7749,
            "default_lon": -122.4194,
            "default_zoom": 12,
        },
    }


@admin.register(PetAdoptions)
class PetAdoptionsAdmin(admin.ModelAdmin):
    list_display = [
        "animal",
        "organisation",
        "adoption_status",
        "adopted",
        "adoption_fee",
        "listed_at",
    ]
    list_filter = ["adoption_status", "adopted", "listed_at", "adoption_date"]
    search_fields = ["animal__name", "organisation__name", "adopter_name"]
    readonly_fields = ["listed_at", "updated_at"]
    date_hierarchy = "listed_at"

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("animal", "organisation", "adoption_status", "adopted")},
        ),
        (
            "Adoption Details",
            {"fields": ("adoption_fee", "special_requirements", "adoption_notes")},
        ),
        ("Contact Information", {"fields": ("contact_phone", "contact_email")}),
        (
            "Adoption Completion",
            {
                "fields": ("adoption_date", "adopter_name", "adopter_contact"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {"fields": ("listed_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
