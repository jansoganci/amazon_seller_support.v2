from app import db
from datetime import datetime

class BusinessReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    units_sold = db.Column(db.Integer, default=0)
    sales = db.Column(db.Float, default=0.0)
    conversion_rate = db.Column(db.Float, default=0.0)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class AdvertisingReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    campaign_name = db.Column(db.String(255), nullable=False)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    cost = db.Column(db.Float, default=0.0)
    sales = db.Column(db.Float, default=0.0)
    acos = db.Column(db.Float, default=0.0)
    roas = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ReturnReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    return_reason = db.Column(db.String(255))
    return_rate = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class InventoryReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    asin = db.Column(db.String(10), nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    restock_level = db.Column(db.Integer)
    days_of_supply = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
