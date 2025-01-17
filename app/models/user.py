from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import json

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200))
    _preferences = db.Column('preferences', db.Text, default='{"language":"tr","currency":"TRY","theme":"light","notifications":{"email":true,"browser":true}}')
    preferred_currency = db.Column(db.String(3), default='USD')
    
    # Relationships
    stores = db.relationship('Store', back_populates='user', lazy=True)
    csv_files = db.relationship('CSVFile', backref='user', lazy=True)
    
    @property
    def preferences(self):
        if self._preferences is None:
            self._preferences = json.dumps({
                'language': 'tr',
                'currency': 'TRY',
                'theme': 'light',
                'notifications': {
                    'email': True,
                    'browser': True
                }
            })
            db.session.commit()
        return json.loads(self._preferences)

    @preferences.setter
    def preferences(self, value):
        self._preferences = json.dumps(value)

    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self._preferences = json.dumps({
            'language': 'tr',
            'currency': 'TRY',
            'theme': 'light',
            'notifications': {
                'email': True,
                'browser': True
            }
        })

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
        
    def __repr__(self):
        return f'<User {self.email}>'