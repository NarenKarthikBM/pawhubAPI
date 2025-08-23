from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """This model stores the details of users
    Returns:
        class: details of users
    """

    email = models.EmailField(
        _("email address"), help_text="Email Address", unique=True, db_index=True
    )
    username = models.CharField(_("username"), help_text="Username", max_length=20, unique=True, db_index=True)
    name = models.CharField(_("name"), help_text="Name", max_length=50, db_index=True)
    is_staff = models.BooleanField(_("is staff"), help_text="Is Staff", default=False)
    is_superuser = models.BooleanField(
        _("is superuser"), help_text="Is Superuser", default=False
    )
    is_active = models.BooleanField(_("is active"), help_text="Is Active", default=True)
    date_joined = models.DateTimeField(
        _("date joined"), help_text="Date Joined", auto_now_add=True
    )

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["name", "email"]

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    class Meta:
        """Stores Meta data of the model class"""

        verbose_name = "user"
        verbose_name_plural = "users"


class UserAuthTokens(models.Model):
    """This model stores user's auth tokens
    Returns:
        class: details of user's auth tokens
    """

    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="user",
        help_text="User",
        related_name="auth_tokens",
        related_query_name="auth_tokens",
    )

    auth_token = models.CharField(
        _("auth token"), help_text="Auth Token", max_length=255, unique=True, default=""
    )
    device_token = models.CharField(
        _("device token"),
        help_text="Device Token",
        max_length=255,
        unique=True,
        default="",
    )
    type = models.CharField(
        _("type"),
        help_text="Type of token",
        max_length=50,
        choices=[("web", "Web"), ("api", "API")],
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    last_used_at = models.DateTimeField(
        _("last used at"), help_text="Last Used At", null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.type}"

    class Meta:
        verbose_name = "user auth token"
        verbose_name_plural = "user auth tokens"



class UserEmailVerificationToken(models.Model):
    """This model stores user's email verification tokens
    Returns:
        class: details of user's auth tokens
    """

    user = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="user",
        help_text="User",
        related_name="email_verification_tokens",
        related_query_name="email_verification_tokens",
    )

    verification_token = models.CharField(
        _("verification token"),
        help_text="Verification Token",
        max_length=255,
        unique=True,
        default="",
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    expires_at = models.DateTimeField(
        _("expires at"), help_text="Expires At", null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.email}"

    class Meta:
        verbose_name = "user email verification token"
        verbose_name_plural = "user email verification tokens"

