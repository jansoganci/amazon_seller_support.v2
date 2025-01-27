"""Test cases for business services."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.business.models import BusinessReport
from app.modules.business.services import BusinessReportService
from app.modules.business.constants import (
    CSV_GROUPING_OPTIONS as GROUPING_OPTIONS,
    CSV_DEFAULT_GROUP_BY as DEFAULT_GROUP_BY,
    CSV_DEFAULT_PAGE_SIZE as DEFAULT_PAGE_SIZE,
    CSV_DEFAULT_SORT_ORDER as DEFAULT_SORT_ORDER
)

@pytest.fixture
def store_id():
    """Store ID fixture."""
    return 1

@pytest.fixture
def business_service(store_id):
    """Business service fixture."""
    return BusinessReportService(store_id)

@pytest.fixture
def sample_reports(store_id):
    """Sample business reports fixture."""
    reports = []
    base_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    for i in range(5):
        report = BusinessReport(
            store_id=store_id,
            date=base_date - timedelta(days=i),
            asin=f'B00000{i}',
            title=f'Product {i}',
            category='Electronics',
            subcategory='Accessories',
            ordered_product_sales=Decimal('100.00') * (i + 1),
            units_ordered=10 * (i + 1),
            sessions=100 * (i + 1),
            page_views=200 * (i + 1),
            buy_box_percentage=Decimal('90.00'),
            units_ordered_b2b=5 * (i + 1),
            ordered_product_sales_b2b=Decimal('50.00') * (i + 1)
        )
        reports.append(report)
    
    return reports

def test_get_reports_basic(business_service, sample_reports, db_session):
    """Test basic report retrieval."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    reports = business_service.get_reports(start_date, end_date)
    
    # Assert
    assert len(reports) == 5
    assert all(isinstance(report, dict) for report in reports)
    assert all(
        key in reports[0]
        for key in [
            'date', 'asin', 'title', 'category', 'subcategory',
            'ordered_product_sales', 'units_ordered'
        ]
    )

def test_get_reports_with_filters(business_service, sample_reports, db_session):
    """Test report retrieval with filters."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    reports = business_service.get_reports(
        start_date,
        end_date,
        category='Electronics',
        subcategory='Accessories',
        asin='B000000'
    )
    
    # Assert
    assert all(report['category'] == 'Electronics' for report in reports)
    assert all(report['subcategory'] == 'Accessories' for report in reports)

def test_get_reports_pagination(business_service, sample_reports, db_session):
    """Test report pagination."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    page_1 = business_service.get_reports(
        start_date, end_date, page=1, per_page=2
    )
    page_2 = business_service.get_reports(
        start_date, end_date, page=2, per_page=2
    )
    
    # Assert
    assert len(page_1) == 2
    assert len(page_2) == 2
    assert page_1[0]['asin'] != page_2[0]['asin']

def test_get_trends_daily(business_service, sample_reports, db_session):
    """Test daily trends calculation."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    trends = business_service.get_trends(
        start_date, end_date, group_by='daily'
    )
    
    # Assert
    assert len(trends) == 5
    assert all(isinstance(trend, dict) for trend in trends)
    assert all(
        key in trends[0]
        for key in ['date', 'ordered_product_sales', 'units_ordered']
    )

def test_get_trends_weekly(business_service, sample_reports, db_session):
    """Test weekly trends calculation."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    trends = business_service.get_trends(
        start_date, end_date, group_by='weekly'
    )
    
    # Assert
    assert len(trends) > 0
    assert all(isinstance(trend, dict) for trend in trends)
    assert all(
        key in trends[0]
        for key in ['date', 'ordered_product_sales', 'units_ordered']
    )

def test_get_trends_monthly(business_service, sample_reports, db_session):
    """Test monthly trends calculation."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute
    trends = business_service.get_trends(
        start_date, end_date, group_by='monthly'
    )
    
    # Assert
    assert len(trends) > 0
    assert all(isinstance(trend, dict) for trend in trends)
    assert all(
        key in trends[0]
        for key in ['date', 'ordered_product_sales', 'units_ordered']
    )

def test_get_trends_invalid_group(business_service):
    """Test trends with invalid grouping."""
    start_date = datetime.now() - timedelta(days=10)
    end_date = datetime.now()
    
    # Execute & Assert
    with pytest.raises(ValueError):
        business_service.get_trends(
            start_date, end_date, group_by='invalid'
        )

def test_get_categories(business_service, sample_reports, db_session):
    """Test category retrieval."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    # Execute
    categories = business_service.get_categories()
    
    # Assert
    assert len(categories) == 1
    assert 'Electronics' in categories

def test_get_asins(business_service, sample_reports, db_session):
    """Test ASIN retrieval."""
    # Setup
    for report in sample_reports:
        db_session.add(report)
    db_session.commit()
    
    # Execute
    asins = business_service.get_asins()
    
    # Assert
    assert len(asins) == 5
    assert all(asin.startswith('B00000') for asin in asins)

def test_calculate_growth_rate(business_service, sample_reports):
    """Test growth rate calculation."""
    # Execute
    growth_rate = business_service.calculate_growth_rate(sample_reports)
    
    # Assert
    assert isinstance(growth_rate, float)
    assert growth_rate != 0.0