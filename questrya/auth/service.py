"""
LAYER: services
ROLE: orchestrates business operations by coordinating domain logic with repositories
CAN communicate with: Repositories, Domain
MUST NOT communicate with: ORM models, Routes

This must have the application use cases
"""

from flask_jwt_extended import create_access_token, create_refresh_token
from datetime import timedelta
from questrya.users.repository import UserRepository


class AuthService:
    def __init__(self):
        self.user_repository = UserRepository()

    def authenticate(self, email: str, password: str):
        user = self.user_repository.get_by_email(email)
        if not user or not user.check_password(password):
            raise ValueError('Invalid credentials')

        access_token = create_access_token(
            identity=str(user.uuid), expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(identity=str(user.uuid))

        return access_token, refresh_token
