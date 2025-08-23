from utils.datetime import serialize_datetime

from . import models


class AnimalMediaSerializer:
    """This serializer class contains serialization methods for AnimalMedia Model"""

    def __init__(self, obj: models.AnimalMedia):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the AnimalMedia model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "image_url": self.obj.image_url,
            "animal_id": self.obj.animal.id if self.obj.animal else None,
            "uploaded_at": serialize_datetime(self.obj.uploaded_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the AnimalMedia model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "image_url": self.obj.image_url,
        }


class AnimalProfileModelSerializer:
    """This serializer class contains serialization methods for AnimalProfileModel Model"""

    def __init__(self, obj: models.AnimalProfileModel):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the AnimalProfileModel model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "type": self.obj.type,
            "images": [
                AnimalMediaSerializer(image).condensed_details_serializer()
                for image in self.obj.images.all()
            ],
            "owner": {
                "id": self.obj.owner.id,
                "username": self.obj.owner.username,
                "name": self.obj.owner.name,
            }
            if self.obj.owner
            else None,
            "location": {
                "latitude": self.obj.latitude,
                "longitude": self.obj.longitude,
            }
            if self.obj.location
            else None,
            "species": self.obj.species,
            "breed": self.obj.breed,
            "is_sterilized": self.obj.is_sterilized,
            "created_at": serialize_datetime(self.obj.created_at),
            "updated_at": serialize_datetime(self.obj.updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the AnimalProfileModel model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "species": self.obj.species,
            "breed": self.obj.breed,
            "type": self.obj.type,
        }


class AnimalSightingSerializer:
    """This serializer class contains serialization methods for AnimalSighting Model"""

    def __init__(self, obj: models.AnimalSighting):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the AnimalSighting model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "animal": AnimalProfileModelSerializer(
                self.obj.animal
            ).condensed_details_serializer()
            if self.obj.animal
            else None,
            "location": {
                "latitude": self.obj.latitude,
                "longitude": self.obj.longitude,
            },
            "image": AnimalMediaSerializer(
                self.obj.image
            ).condensed_details_serializer(),
            "reporter": {
                "id": self.obj.reporter.id,
                "username": self.obj.reporter.username,
                "name": self.obj.reporter.name,
            },
            "created_at": serialize_datetime(self.obj.created_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the AnimalSighting model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "animal_id": self.obj.animal.id if self.obj.animal else None,
            "location": {
                "latitude": self.obj.latitude,
                "longitude": self.obj.longitude,
            },
            "created_at": serialize_datetime(self.obj.created_at),
        }


class EmergencySerializer:
    """This serializer class contains serialization methods for Emergency Model"""

    def __init__(self, obj: models.Emergency):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the Emergency model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "reporter": {
                "id": self.obj.reporter.id,
                "username": self.obj.reporter.username,
                "name": self.obj.reporter.name,
            },
            "location": {
                "latitude": self.obj.latitude,
                "longitude": self.obj.longitude,
            },
            "image": AnimalMediaSerializer(
                self.obj.image
            ).condensed_details_serializer()
            if self.obj.image
            else None,
            "description": self.obj.description,
            "status": self.obj.status,
            "created_at": serialize_datetime(self.obj.created_at),
            "updated_at": serialize_datetime(self.obj.updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the Emergency model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "status": self.obj.status,
            "description": self.obj.description[:100] + "..."
            if len(self.obj.description) > 100
            else self.obj.description,
            "created_at": serialize_datetime(self.obj.created_at),
        }


class LostSerializer:
    """This serializer class contains serialization methods for Lost Model"""

    def __init__(self, obj: models.Lost):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the Lost model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "pet": AnimalProfileModelSerializer(
                self.obj.pet
            ).condensed_details_serializer(),
            "last_seen_at": {
                "latitude": self.obj.last_seen_latitude,
                "longitude": self.obj.last_seen_longitude,
            }
            if self.obj.last_seen_at
            else None,
            "last_seen_time": serialize_datetime(self.obj.last_seen_time),
            "description": self.obj.description,
            "status": self.obj.status,
            "created_at": serialize_datetime(self.obj.created_at),
            "updated_at": serialize_datetime(self.obj.updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the Lost model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "pet": {
                "id": self.obj.pet.id,
                "name": self.obj.pet.name,
                "species": self.obj.pet.species,
            },
            "status": self.obj.status,
            "last_seen_time": serialize_datetime(self.obj.last_seen_time),
        }


class AdoptionSerializer:
    """This serializer class contains serialization methods for Adoption Model"""

    def __init__(self, obj: models.Adoption):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the Adoption model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "profile": AnimalProfileModelSerializer(
                self.obj.profile
            ).details_serializer(),
            "posted_by": {
                "id": self.obj.posted_by.id,
                "name": self.obj.posted_by.name,
                "email": self.obj.posted_by.email,
                "is_verified": self.obj.posted_by.is_verified,
            },
            "description": self.obj.description,
            "status": self.obj.status,
            "created_at": serialize_datetime(self.obj.created_at),
            "updated_at": serialize_datetime(self.obj.updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes condensed fields of the Adoption model

        Returns:
            dict: Dictionary of condensed details
        """

        return {
            "id": self.obj.id,
            "profile": {
                "id": self.obj.profile.id,
                "name": self.obj.profile.name,
                "species": self.obj.profile.species,
                "breed": self.obj.profile.breed,
            },
            "posted_by": {
                "id": self.obj.posted_by.id,
                "name": self.obj.posted_by.name,
            },
            "status": self.obj.status,
            "created_at": serialize_datetime(self.obj.created_at),
        }
