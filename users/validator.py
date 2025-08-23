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


class UserRegistrationInputValidator(GeneralValidator):
    def __init__(self, data) -> None:
        self.data = data

    def serialized_data(self):
        email = self.data.get("email")
        password = self.data.get("password")
        username = self.data.get("username")
        name = self.data.get("name")

        return {
            "email": self.validate_data(
                email,
                self.validate_type("Email", email, str)
                or self.validate_contains("Email", email, ["@"]),
                "email",
            ),
            "password": self.validate_data(
                password,
                self.validate_type("Password", password, str)
                or self.validate_len("Password", password, min=8, max=100),
                "password",
            ),
            "username": self.validate_data(
                username,
                self.validate_type("Username", username, str)
                or self.validate_len("Username", username, min=3, max=20),
                "username",
            ),
            "name": self.validate_data(
                name,
                self.validate_type("Name", name, str)
                or self.validate_len("Name", name, min=1, max=50),
                "name",
            ),
        }
