"""Base report model for all report types."""

from datetime import datetime, UTC
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship, declared_attr
from app.extensions import db

class BaseReport(db.Model):
    """Abstract base class for all report models.
    
    This class provides common fields and relationships that all report types share.
    Each specific report type should inherit from this class and add its own fields.
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(UTC))
    
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.id} for store {self.store_id}>'
