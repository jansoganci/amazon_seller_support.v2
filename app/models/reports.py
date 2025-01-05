from app import db
from datetime import datetime

class BusinessReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    units_sold = db.Column(db.Integer, nullable=False)
    revenue = db.Column(db.Numeric(10, 2), nullable=False)  # 10 basamak, 2 ondalık
    returns = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Numeric(5, 4), nullable=False)  # Örn: 0.0543
    page_views = db.Column(db.Integer, nullable=False)
    sessions = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<BusinessReport {self.store_id}-{self.asin}>'

class AdvertisingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    campaign_name = db.Column(db.String(100), nullable=False)
    impressions = db.Column(db.Integer, nullable=False)
    clicks = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Numeric(10, 2), nullable=False)
    sales = db.Column(db.Numeric(10, 2), nullable=False)
    acos = db.Column(db.Numeric(6, 4), nullable=False)  # Advertising Cost of Sales
    roi = db.Column(db.Numeric(6, 4), nullable=False)  # Return on Investment
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<AdvertisingReport {self.store_id}-{self.campaign_name}>'

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

    def __repr__(self):
        return f'<ReturnReport {self.store_id}-{self.asin}>'

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

    def __repr__(self):
        return f'<InventoryReport {self.store_id}-{self.asin}>'
