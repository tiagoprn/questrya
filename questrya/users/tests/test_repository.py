from datetime import datetime
from uuid import UUID

from questrya.users.repository import UserRepository
from questrya.users.domain import User


class TestUserRepository:
    def test_save_new_user(self, domain_user_data_picard, db_session):
        domain_user = User(**domain_user_data_picard)
        domain_user = UserRepository.save(user=domain_user)
        assert isinstance(domain_user, User)
        assert isinstance(domain_user.uuid, UUID)
        assert isinstance(domain_user.created_at, datetime)
        assert isinstance(domain_user.last_updated_at, datetime)

    def test_save_existing_user(self):
        ...
