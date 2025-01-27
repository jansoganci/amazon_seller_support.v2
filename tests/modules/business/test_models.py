"""Test business models."""

import pytest
from datetime import datetime, UTC
from decimal import Decimal

from app.modules.business.models import BusinessReport
from app.core.models.store import Store
from app.core.models.user import User
from app.extensions import db

@pytest.fixture
def test_user():
    """Create test user."""
    user = User(
        username='testuser',
        email='test@example.com'
    )
    user.set_password('password')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def test_store(test_user):
    """Create test store."""
    store = Store(
        name='Test Store',
        marketplace='US',
        seller_id='SELLER123',
        user_id=test_user.id
    )
    db.session.add(store)
    db.session.commit()
    return store

@pytest.fixture
def test_business_report(test_store):
    """Create test business report."""
    report = BusinessReport(
        store_id=test_store.id,
        date=datetime.now(UTC),
        total_sales=Decimal('1000.00'),
        total_orders=100,
        total_units=150,
        average_selling_price=Decimal('10.00'),
        gross_profit=Decimal('500.00'),
        profit_margin=Decimal('50.00')
    )
    db.session.add(report)
    db.session.commit()
    return report

def test_create_business_report(test_store):
    """Test creating a business report."""
    report = BusinessReport(
        store_id=test_store.id,
        date=datetime.now(UTC),
        total_sales=Decimal('1000.00'),
        total_orders=100,
        total_units=150,
        average_selling_price=Decimal('10.00'),
        gross_profit=Decimal('500.00'),
        profit_margin=Decimal('50.00')
    )
    db.session.add(report)
    db.session.commit()

    assert report.id is not None
    assert report.store_id == test_store.id
    assert report.total_sales == Decimal('1000.00')
    assert report.total_orders == 100
    assert report.total_units == 150
    assert report.average_selling_price == Decimal('10.00')
    assert report.gross_profit == Decimal('500.00')
    assert report.profit_margin == Decimal('50.00')
    assert report.created_at is not None
    assert report.updated_at is not None

def test_update_business_report(test_business_report):
    """Test updating a business report."""
    test_business_report.total_sales = Decimal('2000.00')
    test_business_report.total_orders = 200
    db.session.commit()

    updated_report = BusinessReport.query.get(test_business_report.id)
    assert updated_report.total_sales == Decimal('2000.00')
    assert updated_report.total_orders == 200

def test_delete_business_report(test_business_report):
    """Test deleting a business report."""
    report_id = test_business_report.id
    db.session.delete(test_business_report)
    db.session.commit()

    deleted_report = BusinessReport.query.get(report_id)
    assert deleted_report is None

def test_business_report_store_relationship(test_business_report, test_store):
    """Test business report to store relationship."""
    assert test_business_report.store == test_store
    assert test_business_report in test_store.reports

def test_business_report_validation():
    """Test business report validation."""
    report = BusinessReport()
    with pytest.raises(Exception):  # SQLAlchemy will raise an error for null store_id
        db.session.add(report)
        db.session.commit()

def test_business_report_repr(test_business_report):
    """Test business report string representation."""
    assert str(test_business_report) == f'<BusinessReport {test_business_report.id} for store {test_business_report.store_id}>'
