import re


class InvalidEmailError(ValueError):
    """Raised when an invalid email is provided."""

    pass


class Email:
    """Value Object for Email with validation and immutability."""

    EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    def __init__(self, address: str):
        if not self._is_valid_email(address):
            raise InvalidEmailError(f'Invalid email address: {address}')
        self._address = address.lower()  # Normalize to lowercase

    def __eq__(self, other):
        if isinstance(other, Email):
            return self._address == other._address
        return False

    def __str__(self):
        return self._address

    def __repr__(self):
        return f"Email('{self._address}')"

    @property
    def address(self):
        """Returns the email address as a string."""
        return self._address

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Checks if the email matches a valid pattern."""
        return bool(re.match(Email.EMAIL_REGEX, email))
