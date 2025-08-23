from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from . import models


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password1 = forms.CharField(label="Password", widget=forms.PasswordInput)
    password2 = forms.CharField(
        label="Password confirmation", widget=forms.PasswordInput
    )

    class Meta:
        model = models.CustomUser
        fields = (
            "name",
            "email",
            "username",
            "password1",
            "password2",
            "is_active",
            "is_staff",
            "is_superuser",
        )

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """

    password = ReadOnlyPasswordHashField()

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        # user.set_password(self.cleaned_data.get("password1"))
        user.save()
        return user

    class Meta:
        model = models.CustomUser
        fields = (
            "name",
            "email",
            "username",
            "password",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class CustomUserAdmin(AuthUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    list_display = (
        "name",
        "email",
        "username",
        "is_active",
    )
    search_fields = (
        "name",
        "email",
        "username",
    )
    list_filter = (
        "is_active",
        "is_superuser",
    )
    ordering = ("date_joined",)
    list_per_page = 50
    list_max_show_all = 1000
    list_select_related = ()
    fieldsets = [
        (None, {"fields": ["email", "password"]}),
        (
            "Personal info",
            {
                "fields": [
                    "name",
                    "username",
                ]
            },
        ),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (None, {"fields": ["email", "password1", "password2"]}),
        (
            "Personal info",
            {
                "fields": [
                    "name",
                    "username",
                ]
            },
        ),
        ("Permissions", {"fields": ["is_active", "is_staff", "is_superuser"]}),
    ]


class UserAccessTokensAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "auth_token",
        "device_token",
        "type",
        "created_at",
        "last_used_at",
    )
    search_fields = (
        "user__email",
        "token",
        "type",
    )
    list_filter = (
        "type",
        "created_at",
        "last_used_at",
    )
    ordering = (
        "user",
        "created_at",
    )
    list_per_page = 20
    list_max_show_all = 1000
    list_select_related = ("user",)
    autocomplete_fields = ("user",)


class UserPermissionsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "updated_at",
        "updated_by",
    )
    search_fields = (
        "user__email",
        "updated_by__email",
    )
    list_filter = ("updated_at",)
    ordering = (
        "user",
        "updated_at",
    )
    list_per_page = 20
    list_max_show_all = 1000
    list_select_related = ("user", "updated_by")
    autocomplete_fields = ("user", "updated_by")


class UserAccessRequestsAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "approved",
        "created_at",
        "approved_at",
    )
    search_fields = (
        "user__name",
        "user__email",
        "approved",
    )
    list_filter = ("approved",)
    ordering = ("user",)
    list_per_page = 20
    list_max_show_all = 1000
    list_select_related = ("user",)
    autocomplete_fields = ("user",)


# admin.site.register(models.UserAccessRequests, UserAccessRequestsAdmin)
admin.site.register(models.CustomUser, CustomUserAdmin)
admin.site.register(models.UserAuthTokens, UserAccessTokensAdmin)
# admin.site.register(models.UserPermissions, UserPermissionsAdmin)
