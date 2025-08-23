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
                "latitude": float(self.obj.location.y) if self.obj.location else None,
                "longitude": float(self.obj.location.x) if self.obj.location else None,
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
            "is_verified": self.obj.is_verified,
        }


class OrganisationMissionsSerializer:
    """This serializer class contains serialization methods for OrganisationMissions Model"""

    def __init__(self, obj: models.OrganisationMissions):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the OrganisationMissions model

        Returns:
            dict: Dictionary of all mission details
        """

        return {
            "id": self.obj.id,
            "title": self.obj.title,
            "description": self.obj.description,
            "mission_type": self.obj.mission_type,
            "mission_type_display": self.obj.get_mission_type_display(),
            "city": self.obj.city,
            "area": self.obj.area,
            "location": {
                "latitude": float(self.obj.location.y) if self.obj.location else None,
                "longitude": float(self.obj.location.x) if self.obj.location else None,
            },
            "start_datetime": serialize_datetime(self.obj.start_datetime),
            "end_datetime": serialize_datetime(self.obj.end_datetime),
            "is_active": self.obj.is_active,
            "max_participants": self.obj.max_participants,
            "contact_phone": self.obj.contact_phone,
            "contact_email": self.obj.contact_email,
            "organisation": OrganisationSerializer(
                self.obj.organisation
            ).condensed_details_serializer(),
            "created_at": serialize_datetime(self.obj.created_at),
            "updated_at": serialize_datetime(self.obj.updated_at),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes key fields of the OrganisationMissions model

        Returns:
            dict: Dictionary of mission key details
        """

        return {
            "id": self.obj.id,
            "title": self.obj.title,
            "mission_type": self.obj.mission_type,
            "mission_type_display": self.obj.get_mission_type_display(),
            "city": self.obj.city,
            "area": self.obj.area,
            "location": {
                "latitude": float(self.obj.location.y) if self.obj.location else None,
                "longitude": float(self.obj.location.x) if self.obj.location else None,
            },
            "start_datetime": serialize_datetime(self.obj.start_datetime),
            "end_datetime": serialize_datetime(self.obj.end_datetime),
            "organisation": OrganisationSerializer(
                self.obj.organisation
            ).condensed_details_serializer(),
        }
