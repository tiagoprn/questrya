"""
LAYER: domain
ROLE: busines logic
CAN communicate with: nothing
MUST NOT communicate with: ORM models, Repositories, Services, Routes

This must contain ONLY pure python objects.
"""

from datetime import datetime
from questrya.common.value_objects.email import Email
from questrya.extensions import bcrypt


class User:
    def __init__(
        self,
        uuid,
        username,
        email,
        password_hash,
        created_at=None,
        last_updated_at=None,
    ):
        self.uuid = uuid
        self.username = username
        self.email = Email(email)  # ✅ Uses a Value Object for validation
        self.password_hash = password_hash
        self.created_at = created_at or datetime.utcnow()
        self.last_updated_at = last_updated_at or datetime.utcnow()

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def update(self, email=None, password=None):
        if email:
            self.email = Email(email)
        if password:
            self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        self.last_updated_at = datetime.utcnow()
