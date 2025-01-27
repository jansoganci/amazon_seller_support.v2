import os
import tempfile
import pytest
from datetime import datetime
from decimal import Decimal
import pandas as pd
from pathlib import Path

from app import create_app
from app.extensions import db, bcrypt
from app.models import User, Store

@pytest.fixture
def app():
    uploads_path = tempfile.mkdtemp()
    app = create_app({
        'TESTING': True,
        'SECRET_KEY': 'test-key',
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'UPLOAD_FOLDER': uploads_path
    })

    with app.app_context():
        db.create_all()  # Create all database tables
        yield app
        db.session.remove()
        db.drop_all()  # Drop all tables after tests
        os.rmdir(uploads_path)

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_users(app):
    with app.app_context():
        user = User(
            username='test_user_0',
            email='test0@example.com',
            is_active=True
        )
        user.set_password('test_password')
        db.session.add(user)
        db.session.commit()  # Commit to get user.id

        store = Store(
            name='Test Store',
            marketplace='amazon.com',
            user_id=user.id
        )
        db.session.add(store)
        db.session.commit()

        return {'user': user, 'store': store}

@pytest.fixture
def auth_headers(test_users):
    return {'Authorization': f'Bearer test_token'}

@pytest.fixture
def sample_business_data():
    return {
        'date': '2024-01-20',
        'asin': 'B00TEST123',
        'title': 'Test Product',
        'category': 'Electronics',
        'subcategory': 'Gadgets',
        'units_ordered': 10,
        'units_ordered_b2b': 5,
        'ordered_product_sales': '100.00',
        'ordered_product_sales_b2b': '50.00',
        'total_order_items': 15,
        'browser_sessions': 100,
        'mobile_app_sessions': 50,
        'browser_session_percentage': '66.67',
        'mobile_app_session_percentage': '33.33',
        'browser_page_views': 300,
        'mobile_app_page_views': 150,
        'browser_page_views_percentage': '66.67',
        'mobile_app_page_views_percentage': '33.33'
    } 