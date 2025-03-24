# import pytest
from typing import Dict

from questrya.common.value_objects.email import Email
from questrya.users.domain import User


class TestUserDomain:
    def test_instantiate_user(self, domain_user_data_picard: Dict):
        user_instance = User(**domain_user_data_picard)
        for key, value in domain_user_data_picard.items():
            if key == 'email':
                value = Email(value)
            elif key == 'password':
                assert getattr(user_instance, 'password_hash') != domain_user_data_picard['password']
                continue
            assert getattr(user_instance, key) == value

    def test_check_password_when_equal(self): ...

    def test_check_password_when_different(self): ...

    def test_does_not_update_when_no_uuid(self): ...

    def test_update_successfully(self): ...
