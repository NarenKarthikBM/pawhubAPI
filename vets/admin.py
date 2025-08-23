from django.contrib import admin
from django.contrib.gis.admin import GISModelAdmin

from .models import (
    Vet,
    VetAuthTokens,
    VetEmailVerificationToken,
    VetVerification,
)


@admin.register(Vet)
class VetAdmin(GISModelAdmin):
    list_display = [
        "name",
        "email",
        "license_number",
        "specialization",
        "clinic_name",
        "is_verified",
        "date_joined",
    ]
    list_filter = ["is_verified", "specialization", "date_joined"]
    search_fields = ["name", "email", "license_number", "clinic_name"]
    readonly_fields = ["date_joined", "last_updated_at"]
    gis_widget_kwargs = {
        'attrs': {
            'default_lat': 37.7749,
            'default_lon': -122.4194,
            'default_zoom': 12,
        },
    }


@admin.register(VetAuthTokens)
class VetAuthTokensAdmin(admin.ModelAdmin):
    list_display = ["vet", "type", "created_at", "last_used_at"]
    list_filter = ["type", "created_at"]
    search_fields = ["vet__name", "vet__email"]
    readonly_fields = ["auth_token", "device_token", "created_at"]


@admin.register(VetEmailVerificationToken)
class VetEmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ["vet", "created_at", "expires_at"]
    list_filter = ["created_at", "expires_at"]
    search_fields = ["vet__name", "vet__email"]
    readonly_fields = ["verification_token", "created_at"]


@admin.register(VetVerification)
class VetVerificationAdmin(admin.ModelAdmin):
    list_display = ["vet", "submitted_at", "updated_at"]
    list_filter = ["submitted_at", "updated_at"]
    search_fields = ["vet__name", "vet__email"]
    readonly_fields = ["submitted_at", "updated_at"]
