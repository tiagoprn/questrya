from datetime import datetime
from uuid import UUID, uuid4

from questrya.common.value_objects.email import Email
from questrya.extensions import bcrypt
from questrya.sql_db.models import UserSQLModel
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

    def test_get_by_uuid(self, domain_user_data_picard, db_session):
        # GIVEN
        domain_user = User(**domain_user_data_picard)
        domain_user = UserRepository.save(user=domain_user)  # creates the user
        assert domain_user.uuid

        # WHEN
        found_domain_user = UserRepository.get_by_uuid(uuid=domain_user.uuid)

        # THEN
        assert found_domain_user
        assert isinstance(found_domain_user, User)
        for key, value in domain_user_data_picard.items():
            if key == 'password':
                password_hash = getattr(found_domain_user, 'password_hash')
                assert isinstance(password_hash, str)
                continue
            assert getattr(found_domain_user, key) == value

    def test_get_by_username(self, domain_user_data_picard, db_session):
        # GIVEN
        domain_user = User(**domain_user_data_picard)
        domain_user = UserRepository.save(user=domain_user)  # creates the user
        assert domain_user.uuid

        # WHEN
        found_domain_user = UserRepository.get_by_username(username='picard')

        # THEN
        assert isinstance(found_domain_user, User)
        assert isinstance(found_domain_user.uuid, UUID)
        for key, value in domain_user_data_picard.items():
            if key == 'password':
                password_hash = getattr(found_domain_user, 'password_hash')
                assert isinstance(password_hash, str)
                continue
            assert getattr(found_domain_user, key) == value

    def test_from_domain_to_sqlmodel(self, domain_user_data_picard, db_session):
        # GIVEN
        domain_user = User(**domain_user_data_picard)
        domain_user.uuid = uuid4()
        domain_user.created_at = datetime.utcnow()
        domain_user.last_updated_at = datetime.utcnow()

        # WHEN
        db_user = UserRepository.from_domain(user=domain_user)

        # THEN
        assert isinstance(db_user, UserSQLModel)
        assert isinstance(db_user.uuid, UUID)
        assert db_user.uuid == domain_user.uuid
        assert db_user.username == domain_user.username
        assert db_user.email == domain_user.email.address
        assert db_user.password_hash == domain_user.password_hash
        assert db_user.created_at == domain_user.created_at
        assert db_user.last_updated_at == domain_user.last_updated_at

    def test_from_sqlmodel_to_domain(self, domain_user_data_picard, db_session):
        # GIVEN
        hashed_password = bcrypt.generate_password_hash(password=domain_user_data_picard['password']).decode('utf-8')
        db_user = UserSQLModel(
            username=domain_user_data_picard['username'],
            email=domain_user_data_picard['email'].address,
            password_hash=hashed_password,
        )
        db_session.add(db_user)
        db_session.commit()
        db_session.refresh(db_user)

        # WHEN
        domain_user = UserRepository.to_domain(user_model=db_user)

        # THEN
        assert isinstance(domain_user, User)
        assert isinstance(domain_user.uuid, UUID)
        assert domain_user.username == db_user.username
        assert domain_user.email.address == db_user.email

        assert domain_user.password_hash == hashed_password
        assert domain_user.check_password(password=domain_user_data_picard['password']) is True

        assert domain_user.created_at == db_user.created_at
        assert domain_user.last_updated_at == db_user.last_updated_at
