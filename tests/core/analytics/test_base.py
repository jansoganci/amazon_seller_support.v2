"""Tests for BaseAnalyticsEngine."""

from datetime import datetime, timedelta
import pytest
from typing import List, Dict

from app.core.analytics.base import BaseAnalyticsEngine

class TestAnalyticsEngine(BaseAnalyticsEngine):
    """Test implementation of BaseAnalyticsEngine."""
    
    def _get_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Test implementation of _get_data."""
        return [
            {"date": start_date, "value": 100},
            {"date": start_date + timedelta(days=1), "value": 200}
        ]

@pytest.fixture
def analytics_engine():
    """Create a test analytics engine instance."""
    return TestAnalyticsEngine(store_id=1)

def test_init():
    """Test analytics engine initialization."""
    engine = TestAnalyticsEngine(store_id=1)
    assert engine.store_id == 1
    assert engine.metric_engine is not None

def test_calculate_base_metrics(analytics_engine):
    """Test base metric calculations."""
    data = [
        {"value": 100},
        {"value": 200}
    ]
    metrics = ["sum", "average"]
    
    result = analytics_engine.calculate_base_metrics(data, metrics)
    assert isinstance(result, dict)

def test_get_trends(analytics_engine):
    """Test trend analysis."""
    start_date = datetime.now()
    end_date = start_date + timedelta(days=1)
    
    trends = analytics_engine.get_trends(start_date, end_date)
    assert isinstance(trends, dict)

def test_process_trends(analytics_engine):
    """Test trend data processing."""
    data = [
        {"date": datetime.now(), "value": 100},
        {"date": datetime.now() + timedelta(days=1), "value": 200}
    ]
    
    trends = analytics_engine._process_trends(data, "daily")
    assert isinstance(trends, dict)
