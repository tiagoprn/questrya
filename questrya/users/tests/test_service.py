from uuid import UUID, uuid4

import pytest

from questrya.users.domain import User
from questrya.users.service import UserService


class TestUserService:
    def test_register_user_successfully(self, domain_user_data_picard, db_session):
        # GIVEN
        service = UserService()

        # WHEN
        new_user = service.register_user(**domain_user_data_picard)

        # THEN
        assert isinstance(new_user, User)
        assert isinstance(new_user.uuid, UUID)
        assert new_user.username == domain_user_data_picard['username']

        assert new_user.email.address == domain_user_data_picard['email'].address

        assert isinstance(new_user.password_hash, str)
        assert new_user.check_password(password=domain_user_data_picard['password']) is True

        assert new_user.created_at
        assert new_user.last_updated_at

    def test_register_user_must_fail_if_user_email_exists(self, domain_user_data_picard, db_session):
        # GIVEN
        service = UserService()
        new_user = service.register_user(**domain_user_data_picard)
        assert isinstance(new_user, User)
        assert isinstance(new_user.uuid, UUID)

        # WHEN/THEN
        with pytest.raises(ValueError) as exception_instance:
            _ = service.register_user(**domain_user_data_picard)

        assert exception_instance.type is ValueError
        expected_exception_value = f'Email already registered ({domain_user_data_picard["email"].address})'
        assert exception_instance.value.args[0] == expected_exception_value

    def test_update_user_successfully(self, domain_user_data_picard, db_session):
        # GIVEN
        service = UserService()
        new_user = service.register_user(**domain_user_data_picard)
        assert isinstance(new_user, User)
        assert isinstance(new_user.uuid, UUID)

        # WHEN
        email = 'captain-picard@startrek.com'
        password = 'ABC123abc'
        updated_user = service.update_user(uuid=new_user.uuid, email=email, password=password)

        assert isinstance(updated_user, User)
        assert isinstance(updated_user.uuid, UUID)
        assert updated_user.email.address == email
        assert updated_user.check_password(password=password) is True

    def test_update_user_must_fail_if_uuid_does_not_exist(self, db_session):
        # GIVEN
        service = UserService()

        # WHEN/THEN
        email = 'captain-picard@startrek.com'
        password = 'ABC123abc'
        non_existing_uuid = uuid4()
        with pytest.raises(ValueError) as exception_instance:
            _ = service.update_user(uuid=non_existing_uuid, email=email, password=password)

        assert exception_instance.type is ValueError
        expected_exception_value = f'User not found (uuid="{non_existing_uuid}")'
        assert exception_instance.value.args[0] == expected_exception_value

    def test_get_user_successfully(self, domain_user_data_picard, db_session):
        # GIVEN
        service = UserService()
        new_user = service.register_user(**domain_user_data_picard)
        assert isinstance(new_user, User)
        assert isinstance(new_user.uuid, UUID)

        # WHEN
        existing_user = service.get_user(uuid=new_user.uuid)

        # THEN
        assert isinstance(existing_user, User)
        assert existing_user.uuid == new_user.uuid

    def test_get_user_must_fail_if_uuid_does_not_exist(self, db_session):
        # GIVEN
        service = UserService()

        # WHEN/THEN
        non_existing_uuid = uuid4()
        with pytest.raises(ValueError) as exception_instance:
            _ = service.get_user(uuid=non_existing_uuid)

        assert exception_instance.type is ValueError
        expected_exception_value = f'User not found (uuid="{non_existing_uuid}")'
        assert exception_instance.value.args[0] == expected_exception_value
