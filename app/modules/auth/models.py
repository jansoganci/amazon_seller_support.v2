"""Authentication models."""
from datetime import datetime
from typing import List, Optional, Dict, Any
from flask_login import UserMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
import json

from app.extensions import db

# Default user preferences
DEFAULT_PREFERENCES = {
    "notifications": {
        "email": True,
        "browser": True,
        "mobile": False
    },
    "display": {
        "theme": "light",
        "language": "en",
        "timezone": "UTC"
    },
    "reports": {
        "default_date_range": "last_7_days",
        "auto_refresh": False,
        "refresh_interval": 300  # 5 minutes
    }
}

class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(80), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(db.String(128))
    role: Mapped[str] = mapped_column(db.String(20), nullable=False, default='user')
    active_store_id: Mapped[Optional[int]] = mapped_column(db.Integer, db.ForeignKey('stores.id'), nullable=True)
    _preferences: Mapped[Optional[str]] = mapped_column('preferences', db.Text, nullable=True)
    _is_active: Mapped[bool] = mapped_column('is_active', db.Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stores: Mapped[List["Store"]] = relationship("Store", back_populates="owner", foreign_keys="Store.user_id")
    active_store: Mapped[Optional["Store"]] = relationship("Store", foreign_keys=[active_store_id])
    csv_files: Mapped[List["CSVFile"]] = relationship("CSVFile", back_populates="user", lazy=True)

    def has_store_access(self, store_id: int) -> bool:
        """Check if user has access to a specific store.
        
        Args:
            store_id: ID of the store to check access for
            
        Returns:
            bool: True if user has access, False otherwise
        """
        return any(store.id == store_id for store in self.stores)

    @property
    def preferences(self) -> Dict[str, Any]:
        """Get user preferences."""
        if not self._preferences:
            return DEFAULT_PREFERENCES.copy()
        return json.loads(self._preferences)

    @preferences.setter
    def preferences(self, value: Dict[str, Any]) -> None:
        """Set user preferences."""
        if value is None:
            self._preferences = None
        else:
            # Merge with defaults to ensure all required keys exist
            prefs = DEFAULT_PREFERENCES.copy()
            prefs.update(value)
            self._preferences = json.dumps(prefs)

    @property
    def is_active(self) -> bool:
        """Get user active status."""
        return self._is_active

    @is_active.setter
    def is_active(self, value: bool) -> None:
        """Set user active status."""
        self._is_active = value

    def set_password(self, password: str) -> None:
        """Set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Check password."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f'<User {self.username}>'

__all__ = ['User']
