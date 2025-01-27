"""Fixtures for analytics tests."""

import pytest
from datetime import datetime, timezone
from app.models import User, Store, BusinessReport, AdvertisingReport, InventoryReport, ReturnReport
from app.extensions import db

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='test_user'
        )
        user.set_password('secure_password')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_store(app, test_user):
    """Create a test store."""
    with app.app_context():
        store = Store(
            name='Test Store',
            marketplace='US',
            user_id=test_user.id
        )
        db.session.add(store)
        db.session.commit()
        
        # Set as active store for the user
        test_user.active_store_id = store.id
        db.session.commit()
        return store

@pytest.fixture
def test_business_report(app, test_store):
    """Create a test business report."""
    with app.app_context():
        report = BusinessReport(
            store_id=test_store.id,
            date=datetime.now(timezone.utc),
            total_sales=1000.00,
            total_orders=50,
            average_order_value=20.00
        )
        db.session.add(report)
        db.session.commit()
        return report

@pytest.fixture
def test_advertising_report(app, test_store):
    """Create a test advertising report."""
    with app.app_context():
        report = AdvertisingReport(
            store_id=test_store.id,
            date=datetime.now(timezone.utc),
            total_spend=500.00,
            total_impressions=10000,
            total_clicks=200,
            total_conversions=20
        )
        db.session.add(report)
        db.session.commit()
        return report

@pytest.fixture
def test_inventory_report(app, test_store):
    """Create a test inventory report."""
    with app.app_context():
        report = InventoryReport(
            store_id=test_store.id,
            date=datetime.now(timezone.utc),
            total_items=1000,
            in_stock_items=800,
            out_of_stock_items=200
        )
        db.session.add(report)
        db.session.commit()
        return report

@pytest.fixture
def test_return_report(app, test_store):
    """Create a test return report."""
    with app.app_context():
        report = ReturnReport(
            store_id=test_store.id,
            date=datetime.now(timezone.utc),
            total_returns=50,
            return_rate=0.05
        )
        db.session.add(report)
        db.session.commit()
        return report

@pytest.fixture
def authenticated_client(app, client, test_user):
    """Create an authenticated client session."""
    with app.test_request_context():
        from flask_login import login_user
        login_user(test_user)
        return client
