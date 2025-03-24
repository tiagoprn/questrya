import pytest
# from time import sleep
from typing import Dict
from uuid import uuid4, UUID

from questrya.common.exceptions import DomainException
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

    def test_check_password_when_equal(self, domain_user_data_picard: Dict):
        user_instance = User(**domain_user_data_picard)
        assert user_instance.check_password(password='12345678') is True

    def test_check_password_when_different(self, domain_user_data_picard: Dict):
        user_instance = User(**domain_user_data_picard)
        assert user_instance.check_password(password='23456789') is False

    def test_does_not_update_when_no_uuid(self, domain_user_data_picard: Dict):
        user_instance = User(**domain_user_data_picard)
        with pytest.raises(DomainException) as exception_instance:
            user_instance.update(email='newpicard@enterprise.org')

        assert exception_instance.type is DomainException
        expected_exception_value = 'You cannot update a user object that does not have a uuid.'
        assert exception_instance.value.args[0] == expected_exception_value

    def test_update_successfully(self, domain_user_data_picard: Dict):
        user_instance = User(**domain_user_data_picard)
        user_instance.uuid = uuid4()
        assert isinstance(user_instance.uuid, UUID)

        original_created_at = user_instance.created_at
        original_updated_at = user_instance.last_updated_at

        new_email = 'newpicard@enterprise.org'

        user_instance.update(email=new_email)

        assert isinstance(user_instance.email, Email)
        assert user_instance.email == Email(new_email)
        assert user_instance.created_at == original_created_at
        assert user_instance.last_updated_at > original_updated_at
