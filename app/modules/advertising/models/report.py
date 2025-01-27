"""Advertising report model for storing Amazon seller advertising data."""

from decimal import Decimal
from sqlalchemy import Index
from sqlalchemy.orm import relationship
from app.core.models.base_report import BaseReport
from app import db

class AdvertisingReport(BaseReport):
    """Advertising report model for storing Amazon seller advertising data.
    
    This model extends BaseReport and adds advertising-specific fields.
    Each record represents performance data for a specific search term
    within an ad group in a campaign.
    """
    __tablename__ = 'advertising_reports'
    
    # Campaign Structure
    campaign_name = db.Column(db.String(100), nullable=False)
    ad_group_name = db.Column(db.String(100), nullable=False)
    targeting_type = db.Column(db.String(50), nullable=False)
    match_type = db.Column(db.String(50), nullable=False)
    search_term = db.Column(db.String(200), nullable=False)
    
    # Performance Metrics
    impressions = db.Column(db.Integer, nullable=False, default=0)
    clicks = db.Column(db.Integer, nullable=False, default=0)
    ctr = db.Column(db.Numeric(7, 4), nullable=False, default=0)
    cpc = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    spend = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    total_sales = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    acos = db.Column(db.Numeric(7, 4), nullable=False, default=0)
    total_orders = db.Column(db.Integer, nullable=False, default=0)
    total_units = db.Column(db.Integer, nullable=False, default=0)
    conversion_rate = db.Column(db.Numeric(7, 4), nullable=False, default=0)
    
    # Relationships
    store = relationship('Store', back_populates='advertising_reports')
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_advertising_store_date', 'store_id', 'date'),
        Index('idx_advertising_campaign', 'campaign_name'),
    )
    
    def __repr__(self):
        return f'<AdvertisingReport {self.id} for {self.campaign_name}>'
    
    def to_dict(self) -> dict:
        """Convert report to dictionary format.
        
        Returns:
            dict: Report data in dictionary format.
        """
        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.isoformat() if self.date else None,
            'campaign_name': self.campaign_name,
            'ad_group_name': self.ad_group_name,
            'targeting_type': self.targeting_type,
            'match_type': self.match_type,
            'search_term': self.search_term,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'ctr': float(self.ctr) if self.ctr else None,
            'cpc': float(self.cpc) if self.cpc else None,
            'spend': float(self.spend) if self.spend else None,
            'total_sales': float(self.total_sales) if self.total_sales else None,
            'acos': float(self.acos) if self.acos else None,
            'total_orders': self.total_orders,
            'total_units': self.total_units,
            'conversion_rate': float(self.conversion_rate) if self.conversion_rate else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def roas(self) -> Decimal:
        """Calculate Return on Ad Spend (ROAS).
        
        Returns:
            Decimal: ROAS value, or 0 if no spend.
        """
        if not self.spend or self.spend == 0:
            return Decimal('0')
        return self.total_sales / self.spend
    
    @property
    def cost_per_order(self) -> Decimal:
        """Calculate average cost per order.
        
        Returns:
            Decimal: Cost per order, or 0 if no orders.
        """
        if not self.total_orders or self.total_orders == 0:
            return Decimal('0')
        return self.spend / Decimal(str(self.total_orders))
