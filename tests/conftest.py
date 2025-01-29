"""Test configuration and shared fixtures."""

import os
import pytest
import tempfile
import pandas as pd
from datetime import datetime, UTC, timedelta
from decimal import Decimal
from pathlib import Path
from sqlalchemy import text

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.store import Store
from app.modules.business.models import BusinessReport
from app.modules.inventory.models import InventoryReport
from app.modules.returns.models import ReturnReport
from app.modules.advertising.models import AdvertisingReport
from app.modules.category.models.category import Category, ASINCategory

@pytest.fixture(scope='session')
def app():
    """Create a Flask application for testing."""
    from app.config import TestingConfig
    
    app = create_app(TestingConfig)
    
    with app.app_context():
        db.create_all()  # Create all tables
        yield app
        db.session.remove()
        db.drop_all()  # Drop all tables after tests

@pytest.fixture
def database(app):
    """Create a fresh database for each test."""
    with app.app_context():
        db.session.begin_nested()  # Create savepoint
        yield db
        db.session.rollback()  # Rollback to savepoint
        db.session.execute(text('DELETE FROM users'))  # Clear users table
        db.session.execute(text('DELETE FROM categories'))  # Clear categories table
        db.session.execute(text('DELETE FROM asin_categories'))  # Clear ASIN categories
        db.session.execute(text('DELETE FROM business_reports'))  # Clear business reports table
        db.session.execute(text('DELETE FROM inventory_reports'))  # Clear inventory reports table
        db.session.execute(text('DELETE FROM return_reports'))  # Clear return reports table
        db.session.execute(text('DELETE FROM advertising_reports'))  # Clear advertising reports table
        db.session.commit()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def test_user(database):
    """Create a test user."""
    user = User(
        email='test@example.com',
        password=bcrypt.generate_password_hash('password').decode('utf-8'),
        role='admin'
    )
    database.session.add(user)
    database.session.commit()
    return user

@pytest.fixture
def test_store(test_user, database):
    """Create a test store."""
    store = Store(
        name='Test Store',
        marketplace='US',
        seller_id='A1B2C3D4E5',
        auth_token='test_token',
        refresh_token='test_refresh_token',
        owner_id=test_user.id
    )
    database.session.add(store)
    database.session.commit()
    return store

@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test user."""
    response = client.post('/auth/login', json={
        'email': test_user.email,
        'password': 'password'
    })
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_business_data():
    """Create sample business report data."""
    return {
        'date': datetime.now(UTC).date(),
        'ordered_product_sales': Decimal('100.00'),
        'units_ordered': 10,
        'total_order_items': 10,
        'average_selling_price': Decimal('10.00'),
        'units_refunded': 1,
        'refund_rate': Decimal('0.10'),
        'claims_granted': 0,
        'orders': 8,
        'average_units_per_order': Decimal('1.25'),
        'average_order_value': Decimal('12.50'),
        'sessions': 100,
        'session_percentage': Decimal('0.10'),
        'page_views': 200,
        'page_views_percentage': Decimal('0.20'),
        'buy_box_percentage': Decimal('0.95'),
        'unit_session_percentage': Decimal('0.10')
    }

@pytest.fixture
def sample_business_df(sample_business_data):
    """Create a sample business report DataFrame."""
    return pd.DataFrame([sample_business_data])

@pytest.fixture
def sample_business_report(database, test_store):
    """Create a sample business report."""
    report = BusinessReport(
        store_id=test_store.id,
        date=datetime.now(UTC).date(),
        ordered_product_sales=Decimal('100.00'),
        units_ordered=10,
        total_order_items=10,
        average_selling_price=Decimal('10.00'),
        units_refunded=1,
        refund_rate=Decimal('0.10'),
        claims_granted=0,
        orders=8,
        average_units_per_order=Decimal('1.25'),
        average_order_value=Decimal('12.50'),
        sessions=100,
        session_percentage=Decimal('0.10'),
        page_views=200,
        page_views_percentage=Decimal('0.20'),
        buy_box_percentage=Decimal('0.95'),
        unit_session_percentage=Decimal('0.10')
    )
    database.session.add(report)
    database.session.commit()
    return report

@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file for testing."""
    # Create a temporary file
    temp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
    
    # Sample data
    data = {
        'date': ['2024-01-01', '2024-01-02'],
        'ordered_product_sales': ['100.00', '200.00'],
        'units_ordered': ['10', '20'],
        'total_order_items': ['10', '20'],
        'average_selling_price': ['10.00', '10.00'],
        'units_refunded': ['1', '2'],
        'refund_rate': ['0.10', '0.10'],
        'claims_granted': ['0', '0'],
        'orders': ['8', '16'],
        'average_units_per_order': ['1.25', '1.25'],
        'average_order_value': ['12.50', '12.50'],
        'sessions': ['100', '200'],
        'session_percentage': ['0.10', '0.10'],
        'page_views': ['200', '400'],
        'page_views_percentage': ['0.20', '0.20'],
        'buy_box_percentage': ['0.95', '0.95'],
        'unit_session_percentage': ['0.10', '0.10']
    }
    
    df = pd.DataFrame(data)
    df.to_csv(temp.name, index=False)
    
    return temp.name

@pytest.fixture
def test_data_dir():
    """Get the test data directory path."""
    return Path(__file__).parent / 'data'

def pytest_configure(config):
    """Configure pytest for our tests."""
    config.addinivalue_line(
        "markers", "slow: mark test as slow to run"
    )