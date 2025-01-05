"""Report models for the application."""

from app import db
from datetime import datetime
import json

class StoreReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    seller_id = db.Column(db.String(50), nullable=False)
    store_name = db.Column(db.String(200), nullable=False)
    performance_metrics = db.Column(db.Text)  # JSON as Text for SQLite
    rating = db.Column(db.Numeric(3, 2), nullable=False)  # Örn: 4.85
    total_sales = db.Column(db.Numeric(12, 2), nullable=False)
    order_count = db.Column(db.Integer, nullable=False)
    customer_satisfaction = db.Column(db.Numeric(3, 2))  # Müşteri memnuniyet puanı
    account_health = db.Column(db.String(20))  # Good, Fair, Poor
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<StoreReport {self.store_name}>'

    @property
    def metrics(self):
        """JSON olarak kaydedilen performans metriklerini dict olarak döndür"""
        if self.performance_metrics:
            return json.loads(self.performance_metrics)
        return {}

    @metrics.setter
    def metrics(self, value):
        """Dict olarak verilen performans metriklerini JSON olarak kaydet"""
        if value is None:
            self.performance_metrics = None
        else:
            self.performance_metrics = json.dumps(value)

    def to_dict(self):
        """Model verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'seller_id': self.seller_id,
            'store_name': self.store_name,
            'performance_metrics': self.metrics,
            'rating': float(self.rating) if self.rating else None,
            'total_sales': float(self.total_sales) if self.total_sales else None,
            'order_count': self.order_count,
            'customer_satisfaction': float(self.customer_satisfaction) if self.customer_satisfaction else None,
            'account_health': self.account_health,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class BusinessReport(db.Model):
    """Business report model."""
    
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)
    returns = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Numeric(5, 4), nullable=False)
    page_views = db.Column(db.Integer, nullable=False)
    sessions = db.Column(db.Integer, nullable=False)
    report_period = db.Column(db.String(20), nullable=False)  # Daily, Weekly, Monthly
    category = db.Column(db.String(100))
    buy_box_percentage = db.Column(db.Numeric(5, 2))  # Buy Box kazanma yüzdesi

    def __repr__(self):
        return f'<BusinessReport {self.asin} {self.created_at}>'
        
    def to_dict(self):
        """Convert report to dictionary."""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'created_at': self.created_at.isoformat(),
            'asin': self.asin,
            'title': self.title,
            'units_sold': self.units_sold,
            'revenue': float(self.revenue),
            'returns': self.returns,
            'conversion_rate': float(self.conversion_rate),
            'page_views': self.page_views,
            'sessions': self.sessions,
            'report_period': self.report_period,
            'category': self.category,
            'buy_box_percentage': float(self.buy_box_percentage) if self.buy_box_percentage else None,
        }

class AdvertisingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    campaign_name = db.Column(db.String(100), nullable=False)
    campaign_type = db.Column(db.String(50))  # Sponsored Products, Sponsored Brands, etc.
    target_type = db.Column(db.String(50))  # Manual, Automatic
    impressions = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    sales = db.Column(db.Numeric(10, 2), nullable=False)
    acos = db.Column(db.Numeric(6, 4), nullable=False)  # Advertising Cost of Sales
    roi = db.Column(db.Numeric(6, 4), nullable=False)  # Return on Investment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    keywords = db.Column(db.Text)  # JSON as Text for SQLite

    def __repr__(self):
        return f'<AdvertisingReport {self.store_id}-{self.campaign_name}>'

    @property
    def ctr(self):
        """Click Through Rate hesapla"""
        if self.impressions == 0:
            return 0
        return self.clicks / self.impressions

    @property
    def keyword_data(self):
        """JSON olarak kaydedilen keyword verilerini dict olarak döndür"""
        if self.keywords:
            return json.loads(self.keywords)
        return {}

    @keyword_data.setter
    def keyword_data(self, value):
        """Dict olarak verilen keyword verilerini JSON olarak kaydet"""
        if value is None:
            self.keywords = None
        else:
            self.keywords = json.dumps(value)

    def to_dict(self):
        """Model verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'campaign_name': self.campaign_name,
            'campaign_type': self.campaign_type,
            'target_type': self.target_type,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'cost': float(self.cost) if self.cost else None,
            'sales': float(self.sales) if self.sales else None,
            'ACOS': float(self.acos) if self.acos else None,
            'ROI': float(self.roi) if self.roi else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'keywords': self.keyword_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReturnReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    return_reason = db.Column(db.String(200), nullable=False)
    return_count = db.Column(db.Integer, nullable=False)
    total_units_sold = db.Column(db.Integer, nullable=False)
    return_rate = db.Column(db.Numeric(5, 4), nullable=False)  # Örn: 0.0234
    customer_feedback = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    refund_amount = db.Column(db.Numeric(10, 2))  # İade edilen toplam tutar
    shipping_cost = db.Column(db.Numeric(8, 2))  # İade kargo maliyeti
    resolution = db.Column(db.String(50))  # Refunded, Replaced, Rejected
    category = db.Column(db.String(100))  # İade kategorisi

    def __repr__(self):
        return f'<ReturnReport {self.store_id}-{self.asin}>'

    @property
    def total_cost(self):
        """Toplam iade maliyetini hesapla"""
        return (self.refund_amount or 0) + (self.shipping_cost or 0)

    def to_dict(self):
        """Model verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'asin': self.asin,
            'title': self.title,
            'return_reason': self.return_reason,
            'return_count': self.return_count,
            'total_units_sold': self.total_units_sold,
            'return_rate': float(self.return_rate) if self.return_rate else None,
            'customer_feedback': self.customer_feedback,
            'refund_amount': float(self.refund_amount) if self.refund_amount else None,
            'shipping_cost': float(self.shipping_cost) if self.shipping_cost else None,
            'resolution': self.resolution,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class InventoryReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    units_available = db.Column(db.Integer, nullable=False)
    units_inbound = db.Column(db.Integer, nullable=False)
    units_reserved = db.Column(db.Integer, nullable=False)
    units_total = db.Column(db.Integer, nullable=False)
    reorder_required = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sku = db.Column(db.String(50))  # Stok Kodu
    condition = db.Column(db.String(20))  # New, Used, etc.
    fulfillment_type = db.Column(db.String(20))  # FBA, FBM
    storage_cost = db.Column(db.Numeric(8, 2))  # Depolama maliyeti
    supplier_info = db.Column(db.Text)  # JSON as Text for SQLite

    def __repr__(self):
        return f'<InventoryReport {self.store_id}-{self.asin}>'

    @property
    def stock_value(self):
        """Toplam stok değerini hesapla"""
        if not hasattr(self, '_unit_cost'):
            return None
        return self.units_total * self._unit_cost

    @property
    def supplier_data(self):
        """JSON olarak kaydedilen tedarikçi bilgilerini dict olarak döndür"""
        if self.supplier_info:
            return json.loads(self.supplier_info)
        return {}

    @supplier_data.setter
    def supplier_data(self, value):
        """Dict olarak verilen tedarikçi bilgilerini JSON olarak kaydet"""
        if value is None:
            self.supplier_info = None
        else:
            self.supplier_info = json.dumps(value)

    def to_dict(self):
        """Model verilerini sözlük olarak döndürür"""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'asin': self.asin,
            'title': self.title,
            'units_available': self.units_available,
            'units_inbound': self.units_inbound,
            'units_reserved': self.units_reserved,
            'units_total': self.units_total,
            'reorder_required': self.reorder_required,
            'sku': self.sku,
            'condition': self.condition,
            'fulfillment_type': self.fulfillment_type,
            'storage_cost': float(self.storage_cost) if self.storage_cost else None,
            'supplier_info': self.supplier_data,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
