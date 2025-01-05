"""Test suite for the Analytics Engine."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.utils.analytics_engine import AnalyticsEngine
from app.models.reports import BusinessReport, InventoryReport
from app.models.store import Store

@pytest.fixture
def analytics_engine():
    """Create an instance of AnalyticsEngine for testing."""
    return AnalyticsEngine()

@pytest.fixture
def sample_store(db_session):
    """Create a sample store for testing."""
    store = Store(
        name="Test Store",
        seller_id="TEST123",
        marketplace="US"
    )
    db_session.add(store)
    db_session.commit()
    return store

@pytest.fixture
def sample_business_data(db_session, sample_store):
    """Create sample business report data."""
    today = datetime.utcnow()
    
    # Create 7 days of business data
    reports = []
    for i in range(7):
        report = BusinessReport(
            store_id=sample_store.id,
            asin=f"B00TEST{i}",
            title=f"Test Product {i}",
            units_sold=100 + i * 10,
            revenue=Decimal(str(1000.00 + i * 100)),
            returns=5,
            conversion_rate=Decimal('0.05'),
            page_views=2000,
            sessions=1500,
            created_at=today - timedelta(days=i),
            report_period='Daily'
        )
        reports.append(report)
    
    db_session.bulk_save_objects(reports)
    db_session.commit()
    return reports

@pytest.fixture
def sample_inventory_data(db_session, sample_store):
    """Create sample inventory report data."""
    reports = []
    for i in range(5):
        report = InventoryReport(
            store_id=sample_store.id,
            asin=f"B00TEST{i}",
            title=f"Test Product {i}",
            units_available=100 - i * 20,  # Decreasing availability
            units_inbound=50,
            units_reserved=10,
            reorder_required=(i >= 3),  # Last two items need reorder
            created_at=datetime.utcnow()
        )
        reports.append(report)
    
    db_session.bulk_save_objects(reports)
    db_session.commit()
    return reports

def test_analyze_sales_trends(analytics_engine, sample_store, sample_business_data):
    """Test sales trend analysis functionality."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    results = analytics_engine.analyze_sales_trends(
        sample_store.id,
        (start_date, end_date)
    )
    
    assert 'daily_sales' in results
    assert 'total_revenue' in results
    assert 'total_units' in results
    assert 'average_daily_sales' in results
    assert 'growth_rate' in results
    assert 'conversion_rate' in results
    
    assert len(results['daily_sales']) > 0
    assert results['total_revenue'] > 0
    assert results['total_units'] > 0
    assert results['average_daily_sales'] > 0
    assert isinstance(results['growth_rate'], float)
    assert 0 <= results['conversion_rate'] <= 1

def test_analyze_inventory_status(analytics_engine, sample_store, sample_inventory_data):
    """Test inventory status analysis functionality."""
    results = analytics_engine.analyze_inventory_status(sample_store.id)
    
    assert 'total_inventory' in results
    assert 'items_status' in results
    assert 'low_stock_items' in results
    assert 'out_of_stock_items' in results
    assert 'reorder_recommendations' in results
    assert 'inventory_summary' in results
    
    # Check inventory summary
    summary = results['inventory_summary']
    assert summary['total_items'] == 5
    assert summary['low_stock_count'] > 0
    assert summary['reorder_needed_count'] == 2  # Last two items need reorder
    
    # Check item details
    assert len(results['items_status']) == 5
    for item in results['items_status']:
        assert 'asin' in item
        assert 'title' in item
        assert 'units_available' in item
        assert 'units_inbound' in item
        assert 'units_reserved' in item
        assert 'total_units' in item

def test_analyze_sales_trends_empty_data(analytics_engine, sample_store):
    """Test sales trend analysis with no data."""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)
    
    results = analytics_engine.analyze_sales_trends(
        sample_store.id,
        (start_date, end_date)
    )
    
    assert results['total_revenue'] == 0
    assert results['total_units'] == 0
    assert results['average_daily_sales'] == 0
    assert results['growth_rate'] == 0
    assert results['conversion_rate'] == 0
    assert len(results['daily_sales']) == 0

def test_analyze_inventory_status_empty_data(analytics_engine, sample_store):
    """Test inventory status analysis with no data."""
    results = analytics_engine.analyze_inventory_status(sample_store.id)
    
    assert results['total_inventory'] == 0
    assert len(results['items_status']) == 0
    assert len(results['low_stock_items']) == 0
    assert len(results['out_of_stock_items']) == 0
    assert len(results['reorder_recommendations']) == 0
    assert results['inventory_summary']['total_items'] == 0
