"""Tests for BusinessAnalytics."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock

from app.modules.business.services.analytics import BusinessAnalytics
from app.modules.business.models import BusinessReport

@pytest.fixture
def analytics():
    """Create BusinessAnalytics instance for testing."""
    return BusinessAnalytics(store_id=1)

@pytest.fixture
def sample_data():
    """Create sample business report data."""
    return [
        {
            "date": datetime.now(),
            "category_id": 1,
            "total_revenue": 1000,
            "total_orders": 10,
            "total_units": 15,
            "conversion_rate": 2.5
        },
        {
            "date": datetime.now(),
            "category_id": 2,
            "total_revenue": 2000,
            "total_orders": 20,
            "total_units": 25,
            "conversion_rate": 3.0
        }
    ]

def test_get_data(analytics, sample_data):
    """Test _get_data method."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    with patch('app.modules.business.models.BusinessReport.query') as mock_query:
        mock_query.filter.return_value.all.return_value = [
            MagicMock(to_dict=lambda: data)
            for data in sample_data
        ]
        
        data = analytics._get_data(start_date, end_date)
        assert len(data) == 2
        assert data[0]["total_revenue"] == 1000
        assert data[1]["total_revenue"] == 2000

def test_get_category_metric_list(analytics):
    """Test category metric list."""
    metrics = analytics.get_category_metric_list()
    assert "total_revenue" in metrics
    assert "conversion_rate" in metrics
    assert "average_order_value" in metrics

def test_get_sales_metrics(analytics, sample_data):
    """Test sales metrics calculation."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    with patch.object(analytics, '_get_data', return_value=sample_data):
        # Test without category filter
        metrics = analytics.get_sales_metrics(start_date, end_date)
        assert isinstance(metrics, dict)
        
        # Test with category filter
        metrics = analytics.get_sales_metrics(start_date, end_date, category_id=1)
        assert isinstance(metrics, dict)

def test_get_performance_comparison(analytics, sample_data):
    """Test performance comparison between periods."""
    current_start = datetime.now()
    current_end = current_start + timedelta(days=1)
    previous_start = current_start - timedelta(days=1)
    previous_end = current_start
    
    with patch.object(analytics, '_get_data', return_value=sample_data):
        comparison = analytics.get_performance_comparison(
            current_start,
            current_end,
            previous_start,
            previous_end
        )
        
        assert "current" in comparison
        assert "previous" in comparison
        assert "growth" in comparison

def test_calculate_growth(analytics):
    """Test growth rate calculations."""
    current = {"metric1": 200, "metric2": 150}
    previous = {"metric1": 100, "metric2": 50}
    
    growth = analytics._calculate_growth(current, previous)
    assert growth["metric1"] == 100.0  # (200-100)/100 * 100
    assert growth["metric2"] == 200.0  # (150-50)/50 * 100
