"""Inventory report model for storing Amazon seller inventory data."""

from decimal import Decimal
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from app.core.models.base_report import BaseReport
from app import db

class InventoryReport(BaseReport):
    """Inventory report model for storing Amazon seller inventory data.
    
    This model extends BaseReport and adds inventory-specific fields.
    Each record represents inventory data for a specific SKU/ASIN combination,
    including both MFN (Merchant Fulfilled) and AFN (Amazon Fulfilled) quantities.
    """
    __tablename__ = 'inventory_reports'
    
    # Product Information
    sku = db.Column(db.String(50), nullable=False)
    asin = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    
    # MFN (Merchant Fulfilled Network) fields
    mfn_listing_exists = db.Column(db.Boolean, nullable=False)
    mfn_fulfillable_quantity = db.Column(db.Integer, nullable=False)
    
    # AFN (Amazon Fulfilled Network) fields
    afn_listing_exists = db.Column(db.Boolean, nullable=False)
    afn_warehouse_quantity = db.Column(db.Integer, nullable=False)
    afn_fulfillable_quantity = db.Column(db.Integer, nullable=False)
    afn_unsellable_quantity = db.Column(db.Integer, nullable=False)
    afn_reserved_quantity = db.Column(db.Integer, nullable=False)
    afn_total_quantity = db.Column(db.Integer, nullable=False)
    per_unit_volume = db.Column(db.Numeric(10, 4), nullable=False)
    
    # Relationships
    store = relationship('Store', back_populates='inventory_reports')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_inventory_store_date', 'store_id', 'date'),
        Index('idx_inventory_sku', 'sku'),
        Index('idx_inventory_asin', 'asin')
    )
    
    def __repr__(self):
        return f'<InventoryReport {self.id} for {self.sku}>'
    
    def to_dict(self) -> dict:
        """Convert report to dictionary format.
        
        Returns:
            dict: Report data in dictionary format.
        """
        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.strftime('%Y-%m-%d'),
            'sku': self.sku,
            'asin': self.asin,
            'product_name': self.product_name,
            'condition': self.condition,
            'price': float(self.price),
            'mfn_listing_exists': self.mfn_listing_exists,
            'mfn_fulfillable_quantity': self.mfn_fulfillable_quantity,
            'afn_listing_exists': self.afn_listing_exists,
            'afn_warehouse_quantity': self.afn_warehouse_quantity,
            'afn_fulfillable_quantity': self.afn_fulfillable_quantity,
            'afn_unsellable_quantity': self.afn_unsellable_quantity,
            'afn_reserved_quantity': self.afn_reserved_quantity,
            'afn_total_quantity': self.afn_total_quantity,
            'per_unit_volume': float(self.per_unit_volume),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
    
    @property
    def total_fulfillable_quantity(self) -> int:
        """Calculate total fulfillable quantity across MFN and AFN.
        
        Returns:
            int: Total fulfillable quantity.
        """
        return self.mfn_fulfillable_quantity + self.afn_fulfillable_quantity
    
    @property
    def total_inventory_value(self) -> Decimal:
        """Calculate total inventory value based on price and fulfillable quantity.
        
        Returns:
            Decimal: Total inventory value.
        """
        return self.price * Decimal(str(self.total_fulfillable_quantity))
    
    @property
    def afn_utilization_rate(self) -> Decimal:
        """Calculate AFN warehouse utilization rate.
        
        Returns:
            Decimal: Utilization rate as a percentage, or 0 if no warehouse quantity.
        """
        if not self.afn_warehouse_quantity:
            return Decimal('0')
        return (Decimal(str(self.afn_fulfillable_quantity)) / 
                Decimal(str(self.afn_warehouse_quantity))) * 100
