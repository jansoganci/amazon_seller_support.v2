from app import db
from datetime import datetime

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    marketplace = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship('User')
    business_reports = db.relationship('BusinessReport', backref='store', lazy=True)
    advertising_reports = db.relationship('AdvertisingReport', backref='store', lazy=True)
    return_reports = db.relationship('ReturnReport', backref='store', lazy=True)
    inventory_reports = db.relationship('InventoryReport', backref='store', lazy=True)

    def __repr__(self):
        return f'<Store {self.name} (ID: {self.id}, User: {self.user_id})>'