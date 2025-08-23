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
        }


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
