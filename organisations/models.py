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


class OrganisationMissions(models.Model):
    """This model stores organisation mission information like vaccination drives, adoption drives, etc.
    Returns:
        class: details of organisation missions
    """

    MISSION_TYPE_CHOICES = [
        ("vaccination", "Vaccination Drive"),
        ("adoption", "Adoption Drive"),
        ("rescue", "Rescue Mission"),
        ("awareness", "Awareness Campaign"),
        ("feeding", "Feeding Program"),
        ("medical", "Medical Camp"),
        ("other", "Other"),
    ]

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="organisation",
        help_text="Organisation organizing this mission",
        related_name="missions",
        related_query_name="missions",
    )

    title = models.CharField(
        _("title"), help_text="Mission Title", max_length=255, db_index=True
    )

    description = models.TextField(
        _("description"), help_text="Mission Description", blank=True
    )

    mission_type = models.CharField(
        _("mission type"),
        help_text="Type of mission",
        max_length=50,
        choices=MISSION_TYPE_CHOICES,
        default="other",
        db_index=True,
    )

    city = models.CharField(
        _("city"),
        help_text="City where mission is conducted",
        max_length=100,
        db_index=True,
    )

    area = models.CharField(
        _("area"),
        help_text="Area/locality where mission is conducted",
        max_length=255,
        db_index=True,
    )

    location = models.PointField(
        _("location"),
        help_text="Mission location coordinates (longitude, latitude)",
        null=True,
        blank=True,
        srid=4326,  # WGS 84 coordinate system
    )

    area_coverage = models.PolygonField(
        _("area coverage"),
        help_text="Geographic area coverage of the mission",
        null=True,
        blank=True,
        srid=4326,  # WGS 84 coordinate system
    )

    start_datetime = models.DateTimeField(
        _("start datetime"), help_text="Mission start date and time", db_index=True
    )

    end_datetime = models.DateTimeField(
        _("end datetime"), help_text="Mission end date and time", db_index=True
    )

    is_active = models.BooleanField(
        _("is active"),
        help_text="Is mission currently active",
        default=True,
        db_index=True,
    )

    max_participants = models.PositiveIntegerField(
        _("max participants"),
        help_text="Maximum number of participants/beneficiaries",
        null=True,
        blank=True,
    )

    contact_phone = models.CharField(
        _("contact phone"),
        help_text="Contact phone number for the mission",
        max_length=20,
        blank=True,
    )

    contact_email = models.EmailField(
        _("contact email"),
        help_text="Contact email for the mission",
        blank=True,
    )

    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
    )

    def __str__(self):
        return f"{self.title} - {self.organisation.name}"

    class Meta:
        verbose_name = "organisation mission"
        verbose_name_plural = "organisation missions"
        ordering = ["-start_datetime"]
        indexes = [
            models.Index(fields=["start_datetime", "end_datetime"]),
            models.Index(fields=["city", "area"]),
            models.Index(fields=["mission_type", "is_active"]),
        ]


class PetAdoptions(models.Model):
    """This model stores animal profiles put up for adoption by organisations
    Returns:
        class: details of pet adoptions
    """

    ADOPTION_STATUS_CHOICES = [
        ("available", "Available for Adoption"),
        ("pending", "Adoption Pending"),
        ("adopted", "Adopted"),
        ("withdrawn", "Withdrawn"),
        ("on_hold", "On Hold"),
    ]

    animal = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.CASCADE,
        verbose_name="animal",
        help_text="Animal put up for adoption",
        related_name="org_adoption_listings",
        related_query_name="org_adoption_listings",
    )

    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="organisation",
        help_text="Organisation managing the adoption",
        related_name="pet_adoptions",
        related_query_name="pet_adoptions",
    )

    adoption_status = models.CharField(
        _("adoption status"),
        help_text="Current adoption status",
        max_length=20,
        choices=ADOPTION_STATUS_CHOICES,
        default="available",
        db_index=True,
    )

    adopted = models.BooleanField(
        _("adopted"), help_text="Has the pet been adopted", default=False, db_index=True
    )

    adoption_fee = models.DecimalField(
        _("adoption fee"),
        help_text="Adoption fee amount",
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
    )

    special_requirements = models.TextField(
        _("special requirements"),
        help_text="Special care requirements or adoption criteria",
        blank=True,
    )

    adoption_notes = models.TextField(
        _("adoption notes"),
        help_text="Additional notes about the adoption",
        blank=True,
    )

    contact_phone = models.CharField(
        _("contact phone"),
        help_text="Contact phone for adoption inquiries",
        max_length=20,
        blank=True,
    )

    contact_email = models.EmailField(
        _("contact email"),
        help_text="Contact email for adoption inquiries",
        blank=True,
    )

    adoption_date = models.DateTimeField(
        _("adoption date"),
        help_text="Date when the pet was adopted",
        null=True,
        blank=True,
    )

    adopter_name = models.CharField(
        _("adopter name"),
        help_text="Name of the person who adopted the pet",
        max_length=255,
        blank=True,
    )

    adopter_contact = models.CharField(
        _("adopter contact"),
        help_text="Contact information of the adopter",
        max_length=255,
        blank=True,
    )

    listed_at = models.DateTimeField(
        _("listed at"), help_text="Date when listed for adoption", auto_now_add=True
    )

    updated_at = models.DateTimeField(
        _("updated at"), help_text="Last Updated At", auto_now=True
    )

    def __str__(self):
        return f"{self.animal.name} - {self.organisation.name} ({self.adoption_status})"

    def save(self, *args, **kwargs):
        # Auto-update adopted field based on adoption_status
        if self.adoption_status == "adopted":
            self.adopted = True
            if not self.adoption_date:
                from django.utils import timezone

                self.adoption_date = timezone.now()
        else:
            self.adopted = False
            self.adoption_date = None
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "pet adoption"
        verbose_name_plural = "pet adoptions"
        ordering = ["-listed_at"]
        indexes = [
            models.Index(fields=["adoption_status", "adopted"]),
            models.Index(fields=["organisation", "adoption_status"]),
            models.Index(fields=["listed_at", "adoption_status"]),
        ]
        unique_together = [
            "animal",
            "organisation",
        ]  # Prevent duplicate listings by same org
