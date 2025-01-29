from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime, UTC, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from flask import current_app
import json
from sqlalchemy import UniqueConstraint

@login_manager.user_loader
def load_user(id):
    """Load user by ID."""
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    """User model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False, default='user')  # 'admin' or 'user'
    active_store_id = db.Column(db.Integer, db.ForeignKey('stores.id', name='fk_user_active_store'), nullable=True)
    preferences = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    stores = db.relationship('Store', backref='user', lazy='dynamic', foreign_keys='Store.user_id')
    active_store = db.relationship('Store', foreign_keys=[active_store_id], uselist=False)
    csv_files = db.relationship('CSVFile', back_populates='user', lazy='dynamic')
    upload_history = db.relationship('UploadHistory', back_populates='user', lazy='dynamic')

    def __repr__(self):
        """Return string representation."""
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password hash."""
        return check_password_hash(self.password_hash, password)

    def get_token(self, expires_in=3600):
        """Generate authentication token."""
        now = datetime.now(UTC)
        payload = {
            'user_id': self.id,
            'exp': now + timedelta(seconds=expires_in),
            'iat': now
        }
        return jwt.encode(
            payload,
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )

    def has_store_access(self, store_id):
        """Check if user has access to store."""
        if not store_id:
            return False
            
        # Convert store_id to integer for comparison
        try:
            store_id = int(store_id)
        except (ValueError, TypeError):
            return False
            
        # Check if user owns the store
        return bool(self.stores.filter_by(id=store_id).first())

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == 'admin'

    @staticmethod
    def verify_token(token):
        """Verify authentication token."""
        try:
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            return User.query.get(payload['user_id'])
        except:
            return None

    def to_dict(self):
        """Return dictionary representation."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class UploadHistory(db.Model):
    """Upload history model."""
    __tablename__ = 'upload_history'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    csv_file_id = db.Column(db.Integer, db.ForeignKey('csv_files.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(UTC), onupdate=datetime.now(UTC))

    # Relationships
    user = db.relationship('User', back_populates='upload_history')
    csv_file = db.relationship('CSVFile', back_populates='upload_history')

    def __repr__(self):
        return f'<UploadHistory {self.csv_file.filename} ({self.status})>'