from utils.validator import GeneralValidator


class OrganisationObtainAuthTokenInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        email = self.data.get("email")
        return {
            "email": self.validate_data(
                email,
                self.validate_type("Email", email, str)
                or self.validate_contains("Email", email, ["@"]),
                "email",
            ),
        }


class OrganisationRegistrationInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        name = self.data.get("name")
        email = self.data.get("email")
        address = self.data.get("address", "")
        latitude = self.data.get("latitude")
        longitude = self.data.get("longitude")

        validated_data = {
            "name": self.validate_data(
                name,
                self.validate_type("Name", name, str),
                "name",
            ),
            "email": self.validate_data(
                email,
                self.validate_type("Email", email, str)
                or self.validate_contains("Email", email, ["@"]),
                "email",
            ),
            "address": address,
        }

        if latitude is not None:
            validated_data["latitude"] = self.validate_data(
                latitude,
                self.validate_type("Latitude", latitude, (int, float)),
                "latitude",
            )

        if longitude is not None:
            validated_data["longitude"] = self.validate_data(
                longitude,
                self.validate_type("Longitude", longitude, (int, float)),
                "longitude",
            )

        return validated_data


class OrganisationVerificationInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        verification_text = self.data.get("verification_text", "")
        verification_document_url = self.data.get("verification_document_url", "")

        return {
            "verification_text": verification_text,
            "verification_document_url": verification_document_url,
        }
