# import pytest

from questrya.common.value_objects.email import Email
from questrya.users.domain import User

class TestUserDomain:
    def test_instantiate_user(self):
        data = {
                'username': 'picard',
                'email': 'jean_luc_picard@enterprise.org',
                'password_hash': '12345678',
        }
        user_instance = User(**data)
        for key, value in data.items():
            if key == 'email':
                value = Email(value)
            assert getattr(user_instance, key) == value

    def test_check_password_when_equal(self): ...

    def test_check_password_when_different(self): ...

    def test_does_not_update_when_no_uuid(self): ...

    def test_update_successfully(self): ...
