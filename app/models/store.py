from app import db
from datetime import datetime

class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(50))  # Opsiyonel alan
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # İlişkiler
    business_reports = db.relationship('BusinessReport', backref='store', lazy=True)
    advertising_reports = db.relationship('AdvertisingReport', backref='store', lazy=True)
    return_reports = db.relationship('ReturnReport', backref='store', lazy=True)
    inventory_reports = db.relationship('InventoryReport', backref='store', lazy=True)
    csv_files = db.relationship('CSVFile', backref='store', lazy=True)
    
    def __repr__(self):
        return f'<Store {self.name}>'
