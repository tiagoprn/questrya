"""
LAYER: services
ROLE: orchestrates business operations by coordinating domain logic with repositories
CAN communicate with: Repositories, Domain
MUST NOT communicate with: ORM models, Routes

This must have the application use cases
"""

from questrya.users.repository import UserRepository
from questrya.users.domain import User


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()

    def register_user(self, username, email, password):
        if self.user_repository.get_by_email(email):
            raise ValueError('Email already registered')

        # Create a domain object
        user = User(
            uuid=None,
            username=username,
            email=email,
            password=password
        )
        self.user_repository.save(user=user)

        return user

    def update_user(self, uuid, email=None, password=None):
        user = self.user_repository.get_by_uuid(uuid)
        if not user:
            raise ValueError('User not found')

        # Convert ORM model to domain object using the repository method
        user.update(email=email, password=password)
        self.user_repository.save(user=user)

        return user

    def get_user(self, uuid):
        user = self.user_repository.get_by_uuid(uuid)
        if not user:
            raise ValueError('User not found')

        return user
