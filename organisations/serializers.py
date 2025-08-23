from utils.datetime import serialize_datetime

from . import models


class OrganisationSerializer:
    """This serializer class contains serialization methods for Organisation Model"""

    def __init__(self, obj: models.Organisation):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the Organisation model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "email": self.obj.email,
            "address": self.obj.address,
            "location": {
                "latitude": float(self.obj.location_latitude)
                if self.obj.location_latitude
                else None,
                "longitude": float(self.obj.location_longitude)
                if self.obj.location_longitude
                else None,
            },
            "is_verified": self.obj.is_verified,
            "date_joined": serialize_datetime(self.obj.date_joined),
            "last_updated_at": serialize_datetime(self.obj.last_updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes all descriptive fields of the Organisation model

        Returns:
            dict: Dictionary of all organisation descriptive details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "email": self.obj.email,
        }
