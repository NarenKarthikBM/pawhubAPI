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
