from utils.validator import GeneralValidator


class UserObtainAuthTokenInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        email, password = self.data.get("email"), self.data.get("password")
        return {
            "email": self.validate_data(
                email,
                self.validate_type("Email", email, str)
                or self.validate_contains("Email", email, ["@"]),
                "email",
            ),
            "password": self.validate_data(
                password, self.validate_type("Password", password, str), "password"
            ),
        }


class CreateEmergencyInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        longitude = self.data.get("longitude")
        latitude = self.data.get("latitude")
        description = self.data.get("description")
        image_url = self.data.get("image_url")
        emergency_type = self.data.get("emergency_type")

        # Valid emergency types
        valid_types = [
            "injury",
            "rescue_needed",
            "aggressive_behavior",
            "missing_lost_pet",
        ]

        return {
            "longitude": self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float)),
                "longitude",
            ),
            "latitude": self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float)),
                "latitude",
            ),
            "description": self.validate_data(
                description,
                self.validate_type("Description", description, str)
                or self.validate_len("Description", description, min=10, max=1000),
                "description",
            ),
            "image_url": self.validate_data(
                image_url,
                self.validate_type("Image URL", image_url, str) if image_url else None,
                "image_url",
            ),
            "emergency_type": self.validate_data(
                emergency_type,
                self.validate_type("Emergency Type", emergency_type, str)
                or self.validate_choice("Emergency Type", emergency_type, valid_types)
                if emergency_type
                else None,
                "emergency_type",
            ),
        }

    def validate_choice(self, field_name, value, choices):
        """Validate if value is in allowed choices"""
        if value not in choices:
            return f"{field_name} must be one of: {', '.join(choices)}"
        return None


class CreateSightingInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        longitude = self.data.get("longitude")
        latitude = self.data.get("latitude")
        image_file = self.data.get("image_file")

        return {
            "longitude": self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float)),
                "longitude",
            ),
            "latitude": self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float)),
                "latitude",
            ),
            "image_file": self.validate_data(
                image_file,
                self.validate_file("Image File", image_file),
                "image_file",
            ),
        }

    def validate_file(self, field_name, file):
        """Validate uploaded file"""
        if not file:
            return f"{field_name} is required"

        # Check if it's a file object
        if not hasattr(file, "read") or not hasattr(file, "size"):
            return f"{field_name} must be a valid file"

        return None


class SightingSelectProfileInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        sighting_id = self.data.get("sighting_id")
        action = self.data.get("action")
        profile_id = self.data.get("profile_id")
        new_profile_data = self.data.get("new_profile_data", {})

        validated_data = {
            "sighting_id": self.validate_data(
                sighting_id,
                self.validate_type("Sighting ID", sighting_id, int),
                "sighting_id",
            ),
            "action": self.validate_data(
                action,
                self.validate_type("Action", action, str)
                or self.validate_choices(
                    "Action", action, ["select_existing", "create_new"]
                ),
                "action",
            ),
        }

        if action == "select_existing":
            validated_data["profile_id"] = self.validate_data(
                profile_id,
                self.validate_type("Profile ID", profile_id, int),
                "profile_id",
            )
        elif action == "create_new":
            validated_data["new_profile_data"] = self.validate_new_profile_data(
                new_profile_data
            )

        return validated_data

    def validate_new_profile_data(self, data):
        """Validate new animal profile data"""
        name = data.get("name")
        species = data.get("species")
        breed = data.get("breed", "")

        return {
            "name": self.validate_data(
                name,
                self.validate_type("Name", name, str)
                or self.validate_len("Name", name, min=1, max=255),
                "name",
            ),
            "species": self.validate_data(
                species,
                self.validate_type("Species", species, str)
                or self.validate_len("Species", species, min=1, max=100),
                "species",
            ),
            "breed": self.validate_data(
                breed,
                self.validate_type("Breed", breed, str) if breed else None,
                "breed",
            ),
        }


class RegisterPetInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        name = self.data.get("name")
        species = self.data.get("species")
        breed = self.data.get("breed")
        is_sterilized = self.data.get("is_sterilized")
        longitude = self.data.get("longitude")
        latitude = self.data.get("latitude")

        return {
            "name": self.validate_data(
                name,
                self.validate_type("Name", name, str)
                or self.validate_len("Name", name, min=1, max=255),
                "name",
            ),
            "species": self.validate_data(
                species,
                self.validate_type("Species", species, str)
                or self.validate_len("Species", species, min=1, max=100),
                "species",
            ),
            "breed": self.validate_data(
                breed,
                self.validate_type("Breed", breed, str)
                or self.validate_len("Breed", breed, min=0, max=100)
                if breed
                else None,
                "breed",
            ),
            "is_sterilized": self.validate_data(
                is_sterilized,
                self.validate_type("Is Sterilized", is_sterilized, bool)
                if is_sterilized is not None
                else None,
                "is_sterilized",
            ),
            "longitude": self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float))
                if longitude is not None
                else None,
                "longitude",
            ),
            "latitude": self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float))
                if latitude is not None
                else None,
                "latitude",
            ),
        }


class MarkPetAsLostInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        pet_id = self.data.get("pet_id")
        longitude = self.data.get("longitude")
        latitude = self.data.get("latitude")
        last_seen_time = self.data.get("last_seen_time")
        description = self.data.get("description")

        return {
            "pet_id": self.validate_data(
                pet_id,
                self.validate_type("Pet ID", pet_id, int),
                "pet_id",
            ),
            "longitude": self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float))
                if longitude
                else None,
                "longitude",
            ),
            "latitude": self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float))
                if latitude
                else None,
                "latitude",
            ),
            "last_seen_time": self.validate_data(
                last_seen_time,
                self.validate_type("Last Seen Time", last_seen_time, str)
                if last_seen_time
                else None,
                "last_seen_time",
            ),
            "description": self.validate_data(
                description,
                self.validate_type("Description", description, str)
                or self.validate_len("Description", description, min=10, max=1000),
                "description",
            ),
        }


class NearbyAdoptionsInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        latitude = self.data.get("latitude")
        longitude = self.data.get("longitude")
        radius = self.data.get("radius", 20)  # Default 20km radius

        return {
            "latitude": self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float)),
                "latitude",
            ),
            "longitude": self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float)),
                "longitude",
            ),
            "radius": self.validate_data(
                radius,
                self.validate_type("Radius", radius, (int, float))
                or self.validate_range("Radius", radius, min_val=1, max_val=100),
                "radius",
            ),
        }

    def validate_range(self, field_name, value, min_val=None, max_val=None):
        """Validate if value is within allowed range"""
        if min_val is not None and value < min_val:
            return f"{field_name} must be at least {min_val}"
        if max_val is not None and value > max_val:
            return f"{field_name} must be at most {max_val}"
        return None


class UploadImageInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        image_file = self.data.get("image_file")
        animal_id = self.data.get("animal_id")

        return {
            "image_file": self.validate_data(
                image_file,
                self.validate_file("Image File", image_file),
                "image_file",
            ),
            "animal_id": self.validate_data(
                animal_id,
                self.validate_type("Animal ID", animal_id, int)
                if animal_id is not None
                else None,
                "animal_id",
            ),
        }

    def validate_file(self, field_name, file):
        """Validate uploaded file"""
        if not file:
            return f"{field_name} is required"

        # Check if it's a file object
        if not hasattr(file, "read") or not hasattr(file, "size"):
            return f"{field_name} must be a valid file"

        # Check file size (max 10MB)
        max_size = 10 * 1024 * 1024  # 10MB
        if file.size > max_size:
            return f"{field_name} size must be less than 10MB"

        # Check file type
        allowed_types = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
        content_type = getattr(file, "content_type", "")
        if content_type and content_type not in allowed_types:
            return f"{field_name} must be a valid image file (JPEG, PNG, WEBP)"

        return None
