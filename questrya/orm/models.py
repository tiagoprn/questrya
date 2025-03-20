"""
LAYER: orm models
ROLE: orm models
CAN communicate with: SQLAlchemy
MUST NOT communicate with: Domain, Repositories, Services, Routes

This must contain ONLY ORM (thin) models
"""

from questrya.extensions import db
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4


class UserORMModel(db.Model):
    __tablename__ = 'users'

    uuid = db.Column(UUID(as_uuid=True), default=uuid4, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    # NOTE: use backref here to automatically create the reverse side so on the DependantModel model
    #       I can get e.g. "dependant_model_instance.user.email".
    #       The alternative would be to use back_populates to make this explicit on both models
    #       (so I would need to declare the relationship on both models)
    # dependant_instances = db.relationship("DependantModel", backref="user", lazy=True)
