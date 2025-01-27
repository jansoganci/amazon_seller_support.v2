"""Store model."""

from datetime import datetime, UTC
from app.extensions import db

class Store(db.Model):
    """Store model."""
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', name='fk_store_user'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    seller_id = db.Column(db.String(64), unique=True, nullable=True)
    marketplace = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC))
    updated_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    # Relationships
    csv_files = db.relationship('CSVFile', back_populates='store', lazy='dynamic')
    business_reports = db.relationship('BusinessReport', back_populates='store', lazy='dynamic')
    advertising_reports = db.relationship('AdvertisingReport', back_populates='store', lazy='dynamic')
    inventory_reports = db.relationship('InventoryReport', back_populates='store', lazy='dynamic')
    return_reports = db.relationship('ReturnReport', back_populates='store', lazy='dynamic')

    def __repr__(self):
        return f'<Store {self.name}>'

    def to_dict(self):
        """Return dictionary representation."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'seller_id': self.seller_id,
            'marketplace': self.marketplace,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }