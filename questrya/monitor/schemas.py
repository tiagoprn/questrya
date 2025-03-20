"""
LAYER: schemas
ROLE: Request/Response serialization/validation rules
CAN communicate with: pydantic
MUST NOT communicate with: ORM models, Repositories, Domain, Services, Routes

This must contain serialization/validations rules used by the APIs
"""

from pydantic import BaseModel


class ReadinessResponseSuccess(BaseModel):
    ready: str
    app_version: str
    app_type: str


class LivenessResponseSuccess(BaseModel):
    live: str
    version: str
    timestamp: str
