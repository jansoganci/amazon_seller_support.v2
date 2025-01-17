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
    date = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sku = db.Column(db.String(50), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    sessions = db.Column(db.Integer, nullable=False)
    units_ordered = db.Column(db.Integer, nullable=False)
    ordered_product_sales = db.Column(db.Numeric(10, 2), nullable=False)
    total_order_items = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Numeric(5, 4), nullable=False)

    def __repr__(self):
        return f'<BusinessReport {self.id} (Store: {self.store_id}, Date: {self.date})>'
        
    def to_dict(self):
        """Convert report to dictionary."""
        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sku': self.sku,
            'asin': self.asin,
            'title': self.title,
            'sessions': self.sessions,
            'units_ordered': self.units_ordered,
            'ordered_product_sales': float(self.ordered_product_sales),
            'total_order_items': self.total_order_items,
            'conversion_rate': float(self.conversion_rate)
        }

class AdvertisingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    campaign_name = db.Column(db.String(100), nullable=False)
    ad_group_name = db.Column(db.String(100), nullable=False)
    targeting_type = db.Column(db.String(50), nullable=False)
    match_type = db.Column(db.String(50), nullable=False)
    search_term = db.Column(db.String(200), nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    ctr = db.Column(db.Numeric(7, 4), nullable=False)  # 4 basamak hassasiyet
    cpc = db.Column(db.Numeric(10, 2), nullable=False)  # Para birimi 2 basamak
    spend = db.Column(db.Numeric(10, 2), nullable=False)  # Para birimi 2 basamak
    total_sales = db.Column(db.Numeric(10, 2), nullable=False)  # Para birimi 2 basamak
    acos = db.Column(db.Numeric(7, 4), nullable=False)  # 4 basamak hassasiyet
    total_orders = db.Column(db.Integer, nullable=False)
    total_units = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Numeric(7, 4), nullable=False)  # 4 basamak hassasiyet
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdvertisingReport {self.store_id}-{self.campaign_name}-{self.date}>'

    def to_dict(self):
        """Model verilerini sözlük olarak döndürür"""
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
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ReturnReport(db.Model):
    __tablename__ = 'return_report'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    order_id = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    asin = db.Column(db.String(20), nullable=False)
    title = db.Column(db.String(500), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    return_reason = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False)
    return_center = db.Column(db.String(200), nullable=False)
    return_carrier = db.Column(db.String(100), nullable=False)
    tracking_number = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ReturnReport {self.order_id}>'

    def to_dict(self):
        return {
            'id': self.id,
            'store_id': self.store_id,
            'return_date': self.return_date.strftime('%Y-%m-%d'),
            'order_id': self.order_id,
            'sku': self.sku,
            'asin': self.asin,
            'title': self.title,
            'quantity': self.quantity,
            'return_reason': self.return_reason,
            'status': self.status,
            'refund_amount': float(self.refund_amount),
            'return_center': self.return_center,
            'return_carrier': self.return_carrier,
            'tracking_number': self.tracking_number,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class InventoryReport(db.Model):
    __tablename__ = 'inventory_report'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sku = db.Column(db.String(50), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    condition = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    mfn_listing_exists = db.Column(db.Boolean, nullable=False)
    mfn_fulfillable_quantity = db.Column(db.Integer, nullable=False)
    afn_listing_exists = db.Column(db.Boolean, nullable=False)
    afn_warehouse_quantity = db.Column(db.Integer, nullable=False)
    afn_fulfillable_quantity = db.Column(db.Integer, nullable=False)
    afn_unsellable_quantity = db.Column(db.Integer, nullable=False)
    afn_reserved_quantity = db.Column(db.Integer, nullable=False)
    afn_total_quantity = db.Column(db.Integer, nullable=False)
    per_unit_volume = db.Column(db.Numeric(10, 2), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<InventoryReport {self.store_id} {self.date} {self.asin}>'

    def to_dict(self):
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
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
