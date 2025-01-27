"""Business report models."""

from datetime import datetime
from app.extensions import db

class BusinessReport(db.Model):
    """Business report model."""
    __tablename__ = 'business_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(100), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    units_sold = db.Column(db.Integer, default=0)
    revenue = db.Column(db.Numeric(10, 2), default=0)
    views = db.Column(db.Integer, default=0)
    sessions = db.Column(db.Integer, default=0)
    conversion_rate = db.Column(db.Numeric(5, 2), default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    store = db.relationship('Store', backref=db.backref('business_reports', lazy=True))

    def __repr__(self):
        """String representation."""
        return f'<BusinessReport {self.id} - Store {self.store_id} - {self.date}>'
