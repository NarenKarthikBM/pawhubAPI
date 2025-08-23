from utils.validator import GeneralValidator


class VetObtainAuthTokenInputValidator(GeneralValidator):
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


class VetRegistrationInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        name = self.data.get("name")
        email = self.data.get("email")
        phone_number = self.data.get("phone_number", "")
        license_number = self.data.get("license_number", "")
        specialization = self.data.get("specialization", "")
        clinic_name = self.data.get("clinic_name", "")
        address = self.data.get("address", "")
        latitude = self.data.get("latitude")
        longitude = self.data.get("longitude")
        years_of_experience = self.data.get("years_of_experience")

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
            "phone_number": phone_number,
            "license_number": license_number,
            "specialization": specialization,
            "clinic_name": clinic_name,
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

        if years_of_experience is not None:
            validated_data["years_of_experience"] = self.validate_data(
                years_of_experience,
                self.validate_type("Years of Experience", years_of_experience, int),
                "years_of_experience",
            )

        return validated_data


class VetVerificationInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        verification_text = self.data.get("verification_text", "")
        verification_document_url = self.data.get("verification_document_url", "")
        license_document_url = self.data.get("license_document_url", "")
        education_certificates_url = self.data.get("education_certificates_url", "")

        return {
            "verification_text": verification_text,
            "verification_document_url": verification_document_url,
            "license_document_url": license_document_url,
            "education_certificates_url": education_certificates_url,
        }
