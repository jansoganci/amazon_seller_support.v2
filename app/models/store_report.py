from app.extensions import db
from datetime import datetime

class StoreReport(db.Model):
    """Model for storing store report data."""
    __tablename__ = 'store_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    total_sales = db.Column(db.Numeric(10, 2), nullable=False)
    total_orders = db.Column(db.Integer, nullable=False)
    total_units = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), 
                          onupdate=db.func.current_timestamp())

    # Relationships
    store = db.relationship('Store', back_populates='store_reports')

    def __repr__(self):
        return f'<StoreReport {self.store_id} - {self.report_date}>' 