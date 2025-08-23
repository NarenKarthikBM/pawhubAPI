from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _


class Vet(models.Model):
    """This model stores the details of veterinarians
    Returns:
        class: details of vets
    """

    name = models.CharField(
        _("name"), help_text="Vet Name", max_length=255, db_index=True
    )
    email = models.EmailField(
        _("email address"), help_text="Email Address", unique=True, db_index=True
    )
    phone_number = models.CharField(
        _("phone number"), help_text="Phone Number", max_length=20, blank=True
    )
    license_number = models.CharField(
        _("license number"),
        help_text="Veterinary License Number",
        max_length=100,
        unique=True,
        db_index=True,
    )
    specialization = models.CharField(
        _("specialization"),
        help_text="Veterinary Specialization",
        max_length=255,
        blank=True,
    )
    clinic_name = models.CharField(
        _("clinic name"), help_text="Clinic Name", max_length=255, blank=True
    )
    address = models.TextField(_("address"), help_text="Vet Address", blank=True)
    location = gis_models.PointField(
        _("location"),
        help_text="Geographic location (longitude, latitude)",
        srid=4326,  # WGS84 coordinate system
        null=True,
        blank=True,
    )
    years_of_experience = models.PositiveIntegerField(
        _("years of experience"), help_text="Years of Experience", null=True, blank=True
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

    @property
    def latitude(self):
        """Get latitude from location point"""
        return self.location.y if self.location else None

    @property
    def longitude(self):
        """Get longitude from location point"""
        return self.location.x if self.location else None

    def set_location(self, longitude, latitude):
        """Set location from longitude and latitude coordinates"""
        from django.contrib.gis.geos import Point

        if longitude is not None and latitude is not None:
            self.location = Point(longitude, latitude, srid=4326)
        else:
            self.location = None

    def __str__(self):
        return f"Dr. {self.name}"

    class Meta:
        """Stores Meta data of the model class"""

        verbose_name = "vet"
        verbose_name_plural = "vets"


class VetAuthTokens(models.Model):
    """This model stores vet's auth tokens
    Returns:
        class: details of vet's auth tokens
    """

    vet = models.ForeignKey(
        "vets.Vet",
        on_delete=models.CASCADE,
        verbose_name="vet",
        help_text="Vet",
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
        return f"{self.vet.email} - {self.type}"

    class Meta:
        verbose_name = "vet auth token"
        verbose_name_plural = "vet auth tokens"


class VetEmailVerificationToken(models.Model):
    """This model stores vet's email verification tokens
    Returns:
        class: details of vet's email verification tokens
    """

    vet = models.ForeignKey(
        "vets.Vet",
        on_delete=models.CASCADE,
        verbose_name="vet",
        help_text="Vet",
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
        return f"{self.vet.email}"

    class Meta:
        verbose_name = "vet email verification token"
        verbose_name_plural = "vet email verification tokens"


class VetVerification(models.Model):
    """This model stores vet verification details
    Returns:
        class: details of vet verification
    """

    vet = models.OneToOneField(
        "vets.Vet",
        on_delete=models.CASCADE,
        verbose_name="vet",
        help_text="Vet",
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
    license_document_url = models.URLField(
        _("license document URL"),
        help_text="License Document URL",
        blank=True,
    )
    education_certificates_url = models.URLField(
        _("education certificates URL"),
        help_text="Education Certificates URL",
        blank=True,
    )
    submitted_at = models.DateTimeField(
        _("submitted at"), help_text="Submitted At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
    )

    def __str__(self):
        return f"Verification for Dr. {self.vet.name}"

    class Meta:
        verbose_name = "vet verification"
        verbose_name_plural = "vet verifications"
