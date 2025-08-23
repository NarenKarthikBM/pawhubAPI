from datetime import datetime
from typing import Union

from rest_framework import exceptions, serializers


class GeneralValidator:
    """
    GeneralValidator is a class that provides methods for validating data.

    Attributes:
        None

    Methods:
        validate_type(label: str, data: any, type: type) -> Union[str, None]:
            Validates the type of the data.

        validate_number_range(label: str, string: str,  min: int = 1, max: int = 100,) -> Union[str, None]:
            Validates if the number is in range.

        validate_len(label: str, string: str,  min: int = 1, max: int = 100,) -> Union[str, None]:
            Validates the length of the string.

        validate_choices(label: str, data: any, choices: list) -> Union[str, None]:
            Validates the choices of the data.

        validate_date_time(label: str, data: str) -> Union[str, datetime]:
            Validates the date and time of the data.

        validate_contains(label: str, data: str, substrings: list) -> Union[str, datetime]:
            Validates if the data contains specific substrings.

        raise_validation_error(error: str) -> None:
            Raises a validation error.

        raise_permission_denied(error: str) -> None:
            Raises a permission denied error.

    """

    def validate_data(
        self, data, validation_error: Union[str, None], label: Union[str, None] = None
    ) -> any:
        return (
            self.raise_validation_error(validation_error, label)
            if validation_error
            else data
        )

    def validate_type(self, label: str, data, type: type) -> Union[str, None]:
        """
        Validates the type of the data.

        Args:
            label (str): The label of the data.
            data (any): The data to validate.
            type (type): The type to validate against.

        Returns:
            str: The error message if the data is not of the correct type.
            None: If the data is of the correct type.

        """

        return None if isinstance(data, type) else f"{label} not in correct format"

    def validate_number_range(
        self,
        label: str,
        num: int,
        min: int = 1,
        max: int = 100,
    ) -> Union[str, None]:
        """
        Validates if the number is in range.

        Args:
            label (str): The label of the string.
            num (int): The number to validate.
            min (int): The minimum number.
            max (int): The maximum number.

        Returns:
            str: The error message if the number is not in range.
            None: If the number is in range.

        """
        return (
            None
            if num > min or num < max
            else f"{label} should have more than {min} and less than {max}"
        )

    def validate_len(
        self,
        label: str,
        string: str,
        min: int = 1,
        max: int = 100,
    ) -> Union[str, None]:
        """
        Validates the length of the string.

        Args:
            label (str): The label of the string.
            string (str): The string to validate.
            min (int): The minimum length of the string.
            max (int): The maximum length of the string.

        Returns:
            str: The error message if the string is not of the correct length.
            None: If the string is of the correct length.

        """
        return (
            None
            if len(string) > min or len(string) < max
            else f"{label} should have more than {min} and less than {max} characters"
        )

    def validate_choices(self, label: str, data, choices: list) -> Union[str, None]:
        """
        Validates the choices of the data.

        Args:
            label (str): The label of the data.
            data (any): The data to validate.
            choices (list): The list of choices to validate against.

        Returns:
            str: The error message if the data is not in the given choices.
            None: If the data is in the given choices.

        """
        return None if data in choices else f"{label} not in given choices"

    def validate_date_time(self, label: str, data: str) -> Union[str, datetime]:
        """
        Validates the date and time of the data.

        Args:
            label (str): The label of the data.
            data (str): The data to validate.

        Returns:
            str: The error message if the data is not in ISO format.
            None: If the data contains the substrings.

        """
        return self.validate_type(label, data, str) or (
            datetime.fromisoformat(data)
            if datetime.fromisoformat(data) != ValueError
            else f"{label} not in ISO format"
        )

    def validate_contains(
        self, label: str, data: str, substrings: list
    ) -> Union[str, None]:
        """
        Validates if the data contains specific substrings.

        Args:
            label (str): The label of the data.
            data (str): The data to validate.
            substrings (str): The substrings to check for.

        Returns:
            str: The error message if the data does not contain te substrings.
            datetime: If the data is in ISO format.

        """
        return self.validate_type(label, data, str) or (
            None
            if all(sub in data for sub in substrings)
            else f"{label} does not contain {' '.join(substrings)}"
        )

    def validate_foreign_key(self, label: str, data: int, model) -> Union[str, None]:
        """
        Validates the foreign key of the data.

        Args:
            label (str): The label of the data.
            data (int): The data to validate.
            model (any): The model to validate against.

        Returns:
            str: The error message if the data is not in the given choices.
            None: If the data is in the given choices.

        """
        return (
            None
            if model.objects.filter(id=data).exists()
            else f"{label} not in given choices"
        )

    def raise_validation_error(self, error: str, label: str) -> None:
        # Define docstring for raise_validation_error
        """
        Raises a validation error.

        Args:
            error (str): The error message to raise.

        Returns:
            None

        """
        raise serializers.ValidationError({"error": error, "field": label})

    def raise_permission_denied(self, error: str) -> None:
        # Define docstring for raise_permission_denied
        """
        Raises a permission denied error.

        Args:
            error (str): The error message to raise.

        Returns:
            None

        """

        raise exceptions.PermissionDenied({"error": error})
