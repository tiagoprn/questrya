"""
LAYER: schemas
ROLE: Request/Response serialization/validation rules
CAN communicate with: pydantic
MUST NOT communicate with: ORM models, Repositories, Domain, Services, Routes

This must contain serialization/validations rules used by the APIs
"""

from pydantic import BaseModel, validator
from questrya.common.value_objects.email import Email, InvalidEmailError
from uuid import UUID


class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str

    @validator('email')
    def validate_email(cls, value):
        try:
            email = Email(value)
            return email
        except InvalidEmailError as e:
            raise ValueError(str(e))

    @validator('username')
    def validate_username(cls, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('Username cannot be empty')
        return value

    @validator('password')
    def validate_password(cls, value):
        if not value or len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value


class CreateUserResponseSuccess(BaseModel):
    uuid: UUID


class UpdateUserRequest(BaseModel):
    email: str
    password: str

    @validator('email')
    def validate_email(cls, value):
        try:
            email = Email(value)
            return email.address
        except InvalidEmailError as e:
            raise ValueError(str(e))

    @validator('password')
    def validate_password(cls, value):
        if not value or len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return value


class UpdateUserResponseSuccess(BaseModel):
    uuid: UUID
    email: str
    password: str


class GetUserResponseSuccess(BaseModel):
    uuid: UUID
    email: str
    username: str
