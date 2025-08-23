from utils.datetime import serialize_datetime

from . import models


class VetSerializer:
    """This serializer class contains serialization methods for Vet Model"""

    def __init__(self, obj: models.Vet):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the Vet model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "email": self.obj.email,
            "phone_number": self.obj.phone_number,
            "license_number": self.obj.license_number,
            "specialization": self.obj.specialization,
            "clinic_name": self.obj.clinic_name,
            "address": self.obj.address,
            "location": {
                "latitude": self.obj.latitude,
                "longitude": self.obj.longitude,
            },
            "years_of_experience": self.obj.years_of_experience,
            "is_verified": self.obj.is_verified,
            "date_joined": serialize_datetime(self.obj.date_joined),
            "last_updated_at": serialize_datetime(self.obj.last_updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes all descriptive fields of the Vet model

        Returns:
            dict: Dictionary of all vet descriptive details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "email": self.obj.email,
            "specialization": self.obj.specialization,
            "clinic_name": self.obj.clinic_name,
        }
