"""Return report model for storing Amazon seller return data."""

from decimal import Decimal
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from app.core.models.base_report import BaseReport
from app import db

class ReturnReport(BaseReport):
    """Return report model for storing Amazon seller return data.
    
    This model extends BaseReport and adds return-specific fields.
    Each record represents a returned item with its order details,
    return reason, and processing status.
    """
    __tablename__ = 'return_reports'
    
    # Override date column from BaseReport
    date = None  # This removes the column from BaseReport
    
    # Order Information
    return_date = db.Column(db.DateTime, nullable=False)  # Specific return date
    order_id = db.Column(db.String(50), nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    asin = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)  # Keep as title since that's what's in CSV
    quantity = db.Column(db.Integer, nullable=False)
    
    # Return Details
    return_reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)  # Keep as status since that's what's in CSV
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False)
    
    # Shipping Information
    return_center = db.Column(db.String(200), nullable=False)
    return_carrier = db.Column(db.String(100), nullable=False)
    tracking_number = db.Column(db.String(100), nullable=False)
    
    # Relationships
    store = relationship('Store', back_populates='return_reports')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_return_store_date', 'store_id', 'return_date'),
        Index('idx_return_order', 'order_id'),
        Index('idx_return_sku', 'sku'),
        Index('idx_return_asin', 'asin')
    )
    
    def __repr__(self):
        return f'<ReturnReport {self.id} for order {self.order_id}>'
    
    def to_dict(self) -> dict:
        """Convert report to dictionary format."""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'return_date': self.return_date.isoformat() if self.return_date else None,
            'order_id': self.order_id,
            'sku': self.sku,
            'asin': self.asin,
            'title': self.title,
            'quantity': self.quantity,
            'return_reason': self.return_reason,
            'status': self.status,
            'refund_amount': str(self.refund_amount),
            'return_center': self.return_center,
            'return_carrier': self.return_carrier,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def is_processed(self) -> bool:
        """Check if return has been processed.
        
        Returns:
            bool: True if status indicates processing is complete.
        """
        processed_statuses = {'Completed', 'Refunded', 'Closed'}
        return self.status in processed_statuses
    
    @property
    def is_refunded(self) -> bool:
        """Check if return has been refunded.
        
        Returns:
            bool: True if status indicates refund is complete.
        """
        refunded_statuses = {'Refunded'}
        return self.status in refunded_statuses
