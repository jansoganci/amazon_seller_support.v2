from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from http import HTTPStatus
from app.models.store import Store  

class User(UserMixin, db.Model):
    """User model for storing user related details."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    active_store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    stores = db.relationship('Store', backref='owner', lazy=True)
    active_store = db.relationship('Store', foreign_keys=[active_store_id])

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Set password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check password."""
        return check_password_hash(self.password_hash, password)

    def has_store_access(self, store_id):
        """Check if user has access to a store."""
        return any(store.id == store_id for store in self.stores)


class BusinessReport(db.Model):
    """Business report model."""
    __tablename__ = 'business_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    sku = db.Column(db.String(50), nullable=True)
    asin = db.Column(db.String(10), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    sessions = db.Column(db.Integer, nullable=False)
    units_ordered = db.Column(db.Integer, nullable=False)
    ordered_product_sales = db.Column(db.Numeric(10, 2), nullable=False)
    total_order_items = db.Column(db.Integer, nullable=False)
    conversion_rate = db.Column(db.Numeric(5, 2), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<BusinessReport {self.id} - {self.date}>'


class AdvertisingReport(db.Model):
    """Advertising report model."""
    __tablename__ = 'advertising_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    total_spend = db.Column(db.Float, nullable=False)
    total_impressions = db.Column(db.Integer, nullable=False)
    total_clicks = db.Column(db.Integer, nullable=False)
    total_conversions = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<AdvertisingReport {self.date} ({self.store_id})>'


class InventoryReport(db.Model):
    """Inventory report model."""
    __tablename__ = 'inventory_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    total_items = db.Column(db.Integer, nullable=False)
    in_stock_items = db.Column(db.Integer, nullable=False)
    out_of_stock_items = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<InventoryReport {self.date} ({self.store_id})>'


class ReturnReport(db.Model):
    """Return report model."""
    __tablename__ = 'return_reports'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    total_returns = db.Column(db.Integer, nullable=False)
    return_rate = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<ReturnReport {self.date} ({self.store_id})>'