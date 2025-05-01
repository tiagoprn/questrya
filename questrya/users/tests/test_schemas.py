import pytest
from pydantic import ValidationError
from questrya.users.schemas import CreateUserRequest, UpdateUserRequest


class TestCreateUserRequest:
    def test_validate_email_with_valid_emails(self):
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "user-name@example.com",
            "user_name@example.com",
            "user+tag@example.com",
            "user@subdomain.example.com",
            "USER@EXAMPLE.COM"
        ]

        for email in valid_emails:
            request_data = {
                "username": "testuser",
                "email": email,
                "password": "password123"
            }

            request = CreateUserRequest(**request_data)
            assert request.email == email.lower()

    def test_validate_email_with_invalid_emails(self):
        invalid_emails = [
            "",
            "user",
            "user@",
            "@example.com",
            "user@.com",
            "user@example",
            "user@exam ple.com",
            "us er@example.com",
            "user@exam_ple.com",
        ]

        for email in invalid_emails:
            request_data = {
                "username": "testuser",
                "email": email,
                "password": "password123"
            }

            with pytest.raises(ValidationError) as excinfo:
                CreateUserRequest(**request_data)

            errors = excinfo.value.errors()
            assert any(error["loc"] == ("email",) for error in errors)

    def test_validate_username(self):
        invalid_usernames = ["", " ", "   "]

        for username in invalid_usernames:
            request_data = {
                "username": username,
                "email": "valid@example.com",
                "password": "password123"
            }

            with pytest.raises(ValidationError) as excinfo:
                CreateUserRequest(**request_data)

            errors = excinfo.value.errors()
            assert any(error["loc"] == ("username",) for error in errors)
            assert any("Username cannot be empty" in error["msg"] for error in errors)

        request_data = {
            "username": "validuser",
            "email": "valid@example.com",
            "password": "password123"
        }

        request = CreateUserRequest(**request_data)
        assert request.username == "validuser"

    def test_validate_password(self):
        invalid_passwords = ["", "123", "short"]

        for password in invalid_passwords:
            request_data = {
                "username": "testuser",
                "email": "valid@example.com",
                "password": password
            }

            with pytest.raises(ValidationError) as excinfo:
                CreateUserRequest(**request_data)

            errors = excinfo.value.errors()
            assert any(error["loc"] == ("password",) for error in errors)
            assert any("Password must be at least 8 characters long" in error["msg"] for error in errors)

        request_data = {
            "username": "testuser",
            "email": "valid@example.com",
            "password": "validpassword123"
        }

        request = CreateUserRequest(**request_data)
        assert request.password == "validpassword123"


class TestUpdateUserRequest:
    def test_validate_email_with_valid_emails(self):
        valid_emails = [
            "user@example.com",
            "user.name@example.com",
            "USER@EXAMPLE.COM"
        ]

        for email in valid_emails:
            request_data = {
                "email": email,
                "password": "password123"
            }

            request = UpdateUserRequest(**request_data)
            assert request.email == email.lower()

    def test_validate_email_with_invalid_emails(self):
        invalid_emails = [
            "",
            "user",
            "user@example",
        ]

        for email in invalid_emails:
            request_data = {
                "email": email,
                "password": "password123"
            }

            with pytest.raises(ValidationError) as excinfo:
                UpdateUserRequest(**request_data)

            errors = excinfo.value.errors()
            assert any(error["loc"] == ("email",) for error in errors)

    def test_validate_password(self):
        invalid_passwords = ["", "123", "short"]

        for password in invalid_passwords:
            request_data = {
                "email": "valid@example.com",
                "password": password
            }

            with pytest.raises(ValidationError) as excinfo:
                UpdateUserRequest(**request_data)

            errors = excinfo.value.errors()
            assert any(error["loc"] == ("password",) for error in errors)
            assert any("Password must be at least 8 characters long" in error["msg"] for error in errors)
