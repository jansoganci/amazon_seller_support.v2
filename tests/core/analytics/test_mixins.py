"""Tests for analytics mixins."""

from datetime import datetime, timedelta
import pytest
from typing import List

from app.core.analytics.base import BaseAnalyticsEngine
from app.core.analytics.mixins import CategoryAwareMixin

class TestAnalyticsEngine(CategoryAwareMixin, BaseAnalyticsEngine):
    """Test implementation of CategoryAwareMixin."""
    
    def _get_data(self, start_date: datetime, end_date: datetime) -> List[dict]:
        """Test implementation that returns sample data."""
        return [
            {
                "date": start_date,
                "category_id": 1,
                "subcategory_id": 10,
                "value": 100
            },
            {
                "date": start_date,
                "category_id": 2,
                "subcategory_id": 20,
                "value": 200
            }
        ]
    
    def get_category_metric_list(self) -> List[str]:
        """Test implementation of category metrics."""
        return ["total", "average"]

@pytest.fixture
def engine():
    """Create test engine instance."""
    return TestAnalyticsEngine(store_id=1)

def test_filter_by_category(engine):
    """Test category filtering."""
    data = engine._get_data(datetime.now(), datetime.now())
    
    # Test main category filter
    filtered = engine.filter_by_category(data, category_id=1)
    assert len(filtered) == 1
    assert filtered[0]["category_id"] == 1
    
    # Test subcategory filter
    filtered = engine.filter_by_category(data, subcategory_id=20)
    assert len(filtered) == 1
    assert filtered[0]["subcategory_id"] == 20
    
    # Test both filters
    filtered = engine.filter_by_category(data, category_id=1, subcategory_id=10)
    assert len(filtered) == 1
    assert filtered[0]["category_id"] == 1
    assert filtered[0]["subcategory_id"] == 10

def test_get_category_metrics(engine):
    """Test category metrics calculation."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    # Test metrics for specific category
    metrics = engine.get_category_metrics(start_date, end_date, category_id=1)
    assert isinstance(metrics, dict)
    
    # Test metrics for all categories
    metrics = engine.get_category_metrics(start_date, end_date)
    assert isinstance(metrics, dict)

def test_compare_categories(engine):
    """Test category comparison."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    comparison = engine.compare_categories(start_date, end_date, [1, 2])
    assert isinstance(comparison, dict)
    assert 1 in comparison
    assert 2 in comparison
