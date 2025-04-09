from datetime import datetime
from uuid import UUID

from questrya.common.value_objects.email import Email
from questrya.users.repository import UserRepository
from questrya.users.domain import User


class TestUserRepository:
    def test_save_new_user(self, domain_user_data_picard, db_session):
        # GIVEN
        domain_user = User(**domain_user_data_picard)

        # WHEN
        domain_user = UserRepository.save(user=domain_user)

        # THEN
        assert isinstance(domain_user, User)
        for key, value in domain_user_data_picard.items():
            if key == 'password':
                hash_value = getattr(domain_user, 'password_hash')
                assert hash_value != value
                continue
            assert getattr(domain_user, key) == value
        assert isinstance(domain_user.uuid, UUID)
        assert isinstance(domain_user.created_at, datetime)
        assert isinstance(domain_user.last_updated_at, datetime)

    def test_update_existing_user_email(self, domain_user_data_picard, db_session):
        # GIVEN
        domain_user = User(**domain_user_data_picard)
        domain_user = UserRepository.save(user=domain_user)  # creates the user
        assert domain_user.uuid

        original_email = domain_user.email
        new_email = Email('picard-new@enterprise.org')
        domain_user.email = new_email

        # WHEN
        domain_user = UserRepository.save(user=domain_user)  # updates the user

        # THEN
        updated_domain_user = UserRepository.get_by_email(email=domain_user.email)
        assert updated_domain_user.email.address == new_email.address
        assert updated_domain_user.email.address != original_email.address
