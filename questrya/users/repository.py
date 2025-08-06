"""
LAYER: repository
ROLE: orchestrate persistance with SQLAchemy; translate between SQLAlchemy and pure domain objects
CAN communicate with: ORM models, Domain
MUST NOT communicate with: Services, Routes

This must be a translation layer between the ORM and the pure domain objects
"""
from datetime import datetime

from questrya.common.value_objects.email import Email
from questrya.sql_db.models import UserSQLModel
from questrya.extensions import db
from questrya.users.domain import User
from uuid import UUID


class UserRepository:
    """
    All methods here must receive and return domain User pure objects.

    So, all conversion needed to handle the ORM (database) must be done internally,
    without leaking to the caller of this class.
    """

    @staticmethod
    def get_by_uuid(uuid: UUID) -> User:
        db_user = UserSQLModel.query.filter_by(uuid=uuid).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def get_by_email(email: Email) -> User:
        db_user = UserSQLModel.query.filter_by(email=email.address).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def get_by_username(username) -> User:
        db_user = UserSQLModel.query.filter_by(username=username).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def save(user: User) -> User:
        """
        IMPORTANT: when calling this method, always override the value of the original domain object
                   (because it does not refresh automatically.). E.g.:

        domain_user = UserRepository.save(user=domain_user)

        This way, after saving the object on the repository,
        the domain user will be updated with the new properties
        (uuid, created_at, etc...)
        """
        if getattr(user, 'uuid'):
            # For existing users, fetch from DB first.
            # If I do not do this, UserRepository.from_domain will create a new python object
            # and SQLALchemy will treat the update as an INSERT rather than an UPDATE.
            existing_db_user = UserSQLModel.query.filter_by(uuid=user.uuid).first()
            if existing_db_user:
                # Update fields from domain object
                existing_db_user.username = user.username

                if isinstance(user.email, Email):
                    user.email = user.email._address

                existing_db_user.email = user.email

                existing_db_user.password_hash = user.password_hash
                existing_db_user.last_updated_at = datetime.utcnow()
                db_user = existing_db_user
            else:
                db_user = UserRepository.from_domain(user=user)
                db_user.last_updated_at = datetime.utcnow()
        else:
            # New user
            db_user = UserRepository.from_domain(user=user)

        db.session.add(db_user)
        db.session.commit()
        db.session.refresh(db_user)
        updated_domain_user = UserRepository.to_domain(user_model=db_user)
        return updated_domain_user

    @staticmethod
    def to_domain(user_model: UserSQLModel) -> User:
        if not user_model:
            return None

        domain_user = User(
            uuid=user_model.uuid,
            username=user_model.username,
            email=Email(user_model.email),
            password_hash=user_model.password_hash,
            created_at=user_model.created_at,
            last_updated_at=user_model.last_updated_at
        )
        return domain_user

    @staticmethod
    def from_domain(user: User) -> UserSQLModel:
        if not user:
            return None

        db_user = UserSQLModel(
            uuid=user.uuid if user.uuid else None,
            username=user.username,
            email=user.email.address,  # Email is a Value Object with an 'address' property
            password_hash=user.password_hash,
            created_at=user.created_at,
            last_updated_at=user.last_updated_at
        )
        return db_user
