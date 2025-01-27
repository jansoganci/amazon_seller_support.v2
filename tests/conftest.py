"""Test configuration and shared fixtures."""

import os
import pytest
import tempfile
import pandas as pd
from datetime import datetime, UTC, timedelta
from decimal import Decimal
from pathlib import Path

from app import create_app
from app.extensions import db, bcrypt
from app.models.user import User
from app.models.store import Store
from app.modules.business.models import BusinessReport
from app.modules.inventory.models import InventoryReport
from app.modules.returns.models import ReturnReport
from app.modules.advertising.models import AdvertisingReport

@pytest.fixture
def app():
    """Create a test app."""
    from app import create_app
    from app.config import TestingConfig
    app = create_app(TestingConfig)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SERVER_NAME'] = 'localhost'
    return app

@pytest.fixture
def db(app):
    """Create a fresh database for each test."""
    from app.extensions import db as _db
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create a test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def test_user(db):
    """Create a test user."""
    from app.models.user import User
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_store(test_user, db):
    """Create a test store."""
    store = Store(
        name='Test Store',
        marketplace='amazon.com',
        seller_id='ATVPDKIKX0DER',
        active=True,
        user_id=test_user.id  # Store'u user ile ilişkilendir
    )
    db.session.add(store)
    db.session.commit()
    
    # User'ın active_store_id'sini güncelle
    test_user.active_store_id = store.id
    db.session.commit()
    
    return store

@pytest.fixture
def auth_headers(client, test_user):
    """Get auth headers for test user."""
    response = client.post('/auth/login', json={
        'email': test_user.email,
        'password': 'password123'
    })
    assert response.status_code == 200
    token = response.json['access_token']
    return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def sample_business_data():
    """Create sample business report data."""
    base_date = datetime.now(UTC).date()
    return [
        {
            'date': base_date - timedelta(days=i),
            'asin': f'B00TEST{i%3 + 1}',
            'title': f'Test Product {i%3 + 1}',
            'category': 'Electronics' if i < 5 else 'Books',
            'subcategory': 'Gadgets' if i < 5 else 'Fiction',
            'ordered_product_sales': Decimal(str((i + 1) * 100)),
            'units_ordered': (i + 1) * 10,
            'sessions': (i + 1) * 100,
            'page_views': (i + 1) * 150,
            'buy_box_percentage': Decimal('95.00'),
            'units_ordered_b2b': (i + 1) * 2,
            'ordered_product_sales_b2b': Decimal(str((i + 1) * 20))
        }
        for i in range(10)
    ]

@pytest.fixture
def sample_business_df(sample_business_data):
    """Create a sample business report DataFrame."""
    return pd.DataFrame(sample_business_data)

@pytest.fixture
def sample_business_report(db, test_store):
    """Create a sample business report."""
    from app.modules.business.models import BusinessReport
    report = BusinessReport(
        store_id=test_store.id,
        sku='TEST-SKU-001',
        asin='B00TEST123',
        title='Test Product',
        ordered_product_sales=1000.00,
        total_order_items=50,
        sessions=200,
        units_ordered=60,
        conversion_rate=0.25,
        date=datetime.now().date()
    )
    db.session.add(report)
    db.session.commit()
    return report

@pytest.fixture
def mock_csv_file():
    """Create a mock CSV file for testing."""
    temp_dir = tempfile.mkdtemp()
    file_path = os.path.join(temp_dir, 'test.csv')
    
    df = pd.DataFrame({
        'Date': ['2024-01-01'],
        'ASIN': ['B00TEST1'],
        'Title': ['Test Product'],
        'Category': ['Electronics'],
        'Subcategory': ['Gadgets'],
        'Ordered Product Sales': [1000.00],
        'Units Ordered': [10],
        'Sessions': [100],
        'Page Views': [150],
        'Buy Box Percentage': [95.00],
        'Units Ordered - B2B': [2],
        'Ordered Product Sales - B2B': [200.00]
    })
    
    df.to_csv(file_path, index=False)
    yield file_path
    
    # Cleanup
    os.unlink(file_path)
    os.rmdir(temp_dir)

@pytest.fixture
def test_data_dir():
    """Get the test data directory path."""
    return Path(__file__).parent / 'data'

def pytest_configure(config):
    """Configure pytest for our tests."""
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    ) 