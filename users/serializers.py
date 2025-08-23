from utils.datetime import serialize_datetime

from . import models


class UserSerializer:
    """This serializer class contains serialization methods for User Model"""

    def __init__(self, obj: models.CustomUser):
        self.obj = obj

    def details_serializer(self):
        """This serializer method serializes all fields of the User model

        Returns:
            dict: Dictionary of all details
        """

        return {
            "id": self.obj.id,
            "name": self.obj.name,
            "username": self.obj.username,
            "email": self.obj.email,
            "is_active": self.obj.is_active,
            "is_staff": self.obj.is_staff,
            "is_superuser": self.obj.is_superuser,
            "date_joined": serialize_datetime(self.obj.date_joined),
        }

    def condensed_details_serializer(self):
        """This serializer method serializes all descriptive fields of the User model

        Returns:
            dict: Dictionary of all user descriptive details
        """

        return {
            "id": self.obj.id,
            "email": self.obj.email,
            "username": self.obj.username,
        }
