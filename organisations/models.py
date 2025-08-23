from django.contrib.gis.db import models
from django.utils.translation import gettext_lazy as _


class Organisation(models.Model):
    """This model stores the details of organisations
    Returns:
        class: details of organisations
    """

    name = models.CharField(
        _("name"), help_text="Organisation Name", max_length=255, db_index=True
    )
    email = models.EmailField(
        _("email address"), help_text="Email Address", unique=True, db_index=True
    )
    address = models.TextField(
        _("address"), help_text="Organisation Address", blank=True
    )
    location = models.PointField(
        _("location"),
        help_text="Organisation location coordinates (longitude, latitude)",
        null=True,
        blank=True,
        srid=4326,  # WGS 84 coordinate system
    )
    is_verified = models.BooleanField(
        _("is verified"), help_text="Is Verified", default=False
    )
    date_joined = models.DateTimeField(
        _("date joined"), help_text="Date Joined", auto_now_add=True
    )
    last_updated_at = models.DateTimeField(
        _("last updated at"), help_text="Last Updated At", auto_now=True
    )

    def __str__(self):
        return self.name

    class Meta:
        """Stores Meta data of the model class"""

        verbose_name = "organisation"
        verbose_name_plural = "organisations"


class OrganisationAuthTokens(models.Model):
    """This model stores organisation's auth tokens
    Returns:
        class: details of organisation's auth tokens
    """

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="organisation",
        help_text="Organisation",
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
        return f"{self.organisation.email} - {self.type}"

    class Meta:
        verbose_name = "organisation auth token"
        verbose_name_plural = "organisation auth tokens"


class OrganisationEmailVerificationToken(models.Model):
    """This model stores organisation's email verification tokens
    Returns:
        class: details of organisation's email verification tokens
    """

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="organisation",
        help_text="Organisation",
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
        return f"{self.organisation.email}"

    class Meta:
        verbose_name = "organisation email verification token"
        verbose_name_plural = "organisation email verification tokens"


class OrganisationVerification(models.Model):
    """This model stores organisation verification details
    Returns:
        class: details of organisation verification
    """

    organisation = models.OneToOneField(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="organisation",
        help_text="Organisation",
        related_name="verification",
        related_query_name="verification",
    )

    verification_text = models.TextField(
        _("verification text"),
        help_text="Verification Text (Markdown format)",
        blank=True,
    )
    verification_document_url = models.URLField(
        _("verification document URL"),
        help_text="Verification Document URL",
        blank=True,
    )
    submitted_at = models.DateTimeField(
        _("submitted at"), help_text="Submitted At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
    )

    def __str__(self):
        return f"Verification for {self.organisation.name}"

    class Meta:
        verbose_name = "organisation verification"
        verbose_name_plural = "organisation verifications"
