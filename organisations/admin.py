from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    Organisation,
    OrganisationAuthTokens,
    OrganisationEmailVerificationToken,
    OrganisationVerification,
)


@admin.register(Organisation)
class OrganisationAdmin(GISModelAdmin):
    list_display = ["name", "email", "is_verified", "date_joined"]
    list_filter = ["is_verified", "date_joined"]
    search_fields = ["name", "email"]
    readonly_fields = ["date_joined", "last_updated_at"]
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': 37.7749,
            'default_lon': -122.4194,
            'default_zoom': 12,
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
