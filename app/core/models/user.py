"""User model for authentication and store management."""

from datetime import datetime, UTC, timedelta
import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    """User model for authentication and store management.
    
    Each user can own multiple stores and access their reports.
    """
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(UTC))
    
    # Store relationships
    stores = relationship('Store', back_populates='user', 
                         foreign_keys='Store.user_id',
                         lazy='dynamic')
    
    # Last accessed store
    last_accessed_store_id = db.Column(db.Integer, ForeignKey('store.id'), 
                                     nullable=True)
    last_accessed_store = relationship('Store', 
                                     foreign_keys=[last_accessed_store_id],
                                     post_update=True)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set the user's password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_jwt_token(self, expires_in=3600):
        """Generate a JWT token for API authentication."""
        return jwt.encode(
            {
                'user_id': self.id,
                'exp': datetime.now(UTC) + timedelta(seconds=expires_in)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
    
    @staticmethod
    def verify_jwt_token(token):
        """Verify a JWT token and return the user."""
        try:
            user_id = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )['user_id']
            return User.query.get(user_id)
        except jwt.exceptions.InvalidTokenError:
            return None
    
    def has_store_access(self, store_id):
        """Check if user has access to a specific store."""
        return self.stores.filter_by(id=store_id).first() is not None
    
    def set_last_accessed_store(self, store):
        """Set the last accessed store for the user."""
        if self.has_store_access(store.id):
            self.last_accessed_store = store
            db.session.commit()

@login_manager.user_loader
def load_user(id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(id))
