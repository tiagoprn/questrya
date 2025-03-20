"""
LAYER: repository
ROLE: orchestrate persistance with SQLAchemy; translate between SQLAlchemy and pure domain objects
CAN communicate with: ORM models, Domain
MUST NOT communicate with: Services, Routes

This must be a translation layer between the ORM and the pure domain objects
"""

from questrya.orm.models import UserORMModel
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
        db_user = UserORMModel.query.filter_by(uuid=uuid).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def get_by_email(email) -> User:
        db_user = UserORMModel.query.filter_by(email=email).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def get_by_username(username) -> User:
        db_user = UserORMModel.query.filter_by(username=username).first()
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def save(user: User) -> User:
        db_user = UserRepository.from_domain(user=user)
        db.session.add(db_user)
        db.session.commit()
        db.session.refresh(db_user)
        return UserRepository.to_domain(user_model=db_user)

    @staticmethod
    def to_domain(user_model: UserORMModel) -> User:
        return User(
            uuid=user_model.uuid,
            username=user_model.username,
            email=user_model.email,
            password_hash=user_model.password_hash,
        )

    @staticmethod
    def from_domain(user: User) -> UserORMModel:
        return UserORMModel(
            uuid=user.uuid,
            username=user.username,
            email=user.email.address,  # Assuming Email is a Value Object with an 'address' property
            password_hash=user.password_hash,
        )
