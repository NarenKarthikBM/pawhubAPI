from django.contrib.gis.db import models as gis_models
from django.db import models
from django.utils.translation import gettext_lazy as _
from pgvector.django import VectorField


class AnimalMedia(models.Model):
    """This model stores animal media files
    Returns:
        class: details of animal media
    """

    image_url = models.URLField(_("image url"), help_text="Image URL", max_length=500)
    animal = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.CASCADE,
        verbose_name="animal",
        help_text="Animal",
        related_name="media_files",
        related_query_name="media_files",
        null=True,
        blank=True,
    )
    embedding = VectorField(
        dimensions=512,  # Updated to match ML API output (was 384)
        help_text="Vector embedding for similarity matching",
        null=True,
        blank=True,
    )
    uploaded_at = models.DateTimeField(
        _("uploaded at"), help_text="Uploaded At", auto_now_add=True
    )

    def __str__(self):
        return f"Media for {self.animal.name if self.animal else 'Unknown'}"

    class Meta:
        verbose_name = "animal media"
        verbose_name_plural = "animal media"
        # indexes = [HnswIndex(fields=["embedding"], name="embedding_hnsw_idx")]


class AnimalProfileModel(models.Model):
    """This model stores animal profile information
    Returns:
        class: details of animal profiles
    """

    ANIMAL_TYPE_CHOICES = [
        ("pet", "Pet"),
        ("stray", "Stray"),
    ]

    name = models.CharField(
        _("name"), help_text="Animal Name", max_length=255, db_index=True
    )
    type = models.CharField(
        _("type"),
        help_text="Animal Type",
        max_length=10,
        choices=ANIMAL_TYPE_CHOICES,
        db_index=True,
    )
    images = models.ManyToManyField(
        "animals.AnimalMedia",
        verbose_name="images",
        help_text="Animal Images",
        related_name="profile_animals",
        blank=True,
    )
    owner = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="owner",
        help_text="Pet Owner",
        related_name="pets",
        related_query_name="pets",
        null=True,
        blank=True,
    )
    location = gis_models.PointField(
        _("location"),
        help_text="Animal location coordinates (longitude, latitude)",
        srid=4326,  # WGS84 coordinate system
        null=True,
        blank=True,
    )
    species = models.CharField(
        _("species"), help_text="Animal Species", max_length=100, db_index=True
    )
    breed = models.CharField(
        _("breed"), help_text="Animal Breed", max_length=100, blank=True
    )
    breed_analysis = models.JSONField(
        _("breed analysis"),
        help_text="Unique features of the animal related to breed identification from ML analysis",
        null=True,
        blank=True,
        default=list,
    )
    is_sterilized = models.BooleanField(
        _("is sterilized"), help_text="Is Sterilized", default=False
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
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
        return f"{self.name} ({self.species})"

    class Meta:
        verbose_name = "animal profile"
        verbose_name_plural = "animal profiles"


class AnimalSighting(models.Model):
    """This model stores animal sighting reports
    Returns:
        class: details of animal sightings
    """

    animal = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.SET_NULL,
        verbose_name="animal",
        help_text="Sighted Animal",
        related_name="sightings",
        related_query_name="sightings",
        null=True,
        blank=True,
    )
    location = gis_models.PointField(
        _("location"),
        help_text="Sighting location coordinates (longitude, latitude)",
        srid=4326,  # WGS84 coordinate system
    )
    image = models.ForeignKey(
        "animals.AnimalMedia",
        on_delete=models.CASCADE,
        verbose_name="image",
        help_text="Sighting Image",
        related_name="sightings",
        related_query_name="sightings",
    )
    reporter = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="reporter",
        help_text="User who reported the sighting",
        related_name="reported_sightings",
        related_query_name="reported_sightings",
    )
    breed_analysis = models.JSONField(
        _("breed analysis"),
        help_text="Unique features of the animal related to breed identification from ML analysis",
        null=True,
        blank=True,
        default=list,
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
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
        animal_name = self.animal.name if self.animal else "Unknown Animal"
        return f"Sighting of {animal_name} by {self.reporter.username}"

    class Meta:
        verbose_name = "animal sighting"
        verbose_name_plural = "animal sightings"


class Emergency(models.Model):
    """This model stores emergency reports
    Returns:
        class: details of emergency reports
    """

    EMERGENCY_TYPE_CHOICES = [
        ("injury", "Injury"),
        ("rescue_needed", "Rescue Needed"),
        ("aggressive_behavior", "Aggressive Behavior"),
        ("missing_lost_pet", "Missing/Lost Pet"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("resolved", "Resolved"),
    ]

    emergency_type = models.CharField(
        _("emergency type"),
        help_text="Type of Emergency",
        max_length=20,
        choices=EMERGENCY_TYPE_CHOICES,
        default="injury",
        db_index=True,
    )
    reporter = models.ForeignKey(
        "users.CustomUser",
        on_delete=models.CASCADE,
        verbose_name="reporter",
        help_text="User who reported the emergency",
        related_name="reported_emergencies",
        related_query_name="reported_emergencies",
    )
    location = gis_models.PointField(
        _("location"),
        help_text="Emergency location coordinates (longitude, latitude)",
        srid=4326,  # WGS84 coordinate system
    )
    image = models.ForeignKey(
        "animals.AnimalMedia",
        on_delete=models.SET_NULL,
        verbose_name="image",
        help_text="Emergency Image",
        related_name="emergencies",
        related_query_name="emergencies",
        null=True,
        blank=True,
    )
    animal = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.SET_NULL,
        verbose_name="animal",
        help_text="Animal involved in emergency (for lost pets)",
        related_name="emergency_reports",
        related_query_name="emergency_reports",
        null=True,
        blank=True,
    )
    description = models.TextField(_("description"), help_text="Emergency Description")
    status = models.CharField(
        _("status"),
        help_text="Emergency Status",
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
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
        return f"Emergency reported by {self.reporter.username} - {self.status}"

    class Meta:
        verbose_name = "emergency"
        verbose_name_plural = "emergencies"


class Lost(models.Model):
    """This model stores lost pet reports
    Returns:
        class: details of lost pets
    """

    STATUS_CHOICES = [
        ("active", "Active"),
        ("found", "Found"),
    ]

    pet = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.CASCADE,
        verbose_name="pet",
        help_text="Lost Pet",
        related_name="lost_reports",
        related_query_name="lost_reports",
    )
    last_seen_at = gis_models.PointField(
        _("last seen at"),
        help_text="Last seen location coordinates (longitude, latitude)",
        srid=4326,  # WGS84 coordinate system
        null=True,
        blank=True,
    )
    last_seen_time = models.DateTimeField(
        _("last seen time"), help_text="Last Seen Time"
    )
    description = models.TextField(_("description"), help_text="Lost Pet Description")
    status = models.CharField(
        _("status"),
        help_text="Lost Pet Status",
        max_length=10,
        choices=STATUS_CHOICES,
        default="active",
        db_index=True,
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
    )

    @property
    def last_seen_latitude(self):
        """Get latitude from last seen location point"""
        return self.last_seen_at.y if self.last_seen_at else None

    @property
    def last_seen_longitude(self):
        """Get longitude from last seen location point"""
        return self.last_seen_at.x if self.last_seen_at else None

    def set_last_seen_location(self, longitude, latitude):
        """Set last seen location from longitude and latitude coordinates"""
        from django.contrib.gis.geos import Point

        if longitude is not None and latitude is not None:
            self.last_seen_at = Point(longitude, latitude, srid=4326)
        else:
            self.last_seen_at = None

    def __str__(self):
        return f"Lost: {self.pet.name} - {self.status}"

    class Meta:
        verbose_name = "lost pet"
        verbose_name_plural = "lost pets"


class Adoption(models.Model):
    """This model stores adoption listings
    Returns:
        class: details of adoption listings
    """

    STATUS_CHOICES = [
        ("available", "Available"),
        ("adopted", "Adopted"),
    ]

    profile = models.ForeignKey(
        "animals.AnimalProfileModel",
        on_delete=models.CASCADE,
        verbose_name="profile",
        help_text="Animal Profile for Adoption",
        related_name="adoption_listings",
        related_query_name="adoption_listings",
    )
    posted_by = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.CASCADE,
        verbose_name="posted by",
        help_text="Organisation posting the adoption",
        related_name="adoption_listings",
        related_query_name="adoption_listings",
    )
    description = models.TextField(_("description"), help_text="Adoption Description")
    status = models.CharField(
        _("status"),
        help_text="Adoption Status",
        max_length=10,
        choices=STATUS_CHOICES,
        default="available",
        db_index=True,
    )
    created_at = models.DateTimeField(
        _("created at"), help_text="Created At", auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _("updated at"), help_text="Updated At", auto_now=True
    )

    def __str__(self):
        return f"Adoption: {self.profile.name} by {self.posted_by.name} - {self.status}"

    class Meta:
        verbose_name = "adoption listing"
        verbose_name_plural = "adoption listings"
