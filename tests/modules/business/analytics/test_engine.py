"""Tests for BusinessAnalyticsEngine."""

from datetime import datetime, timedelta
import pytest
from unittest.mock import patch, MagicMock

from app.core.analytics.exceptions import (
    DataFetchError,
    InvalidDateRangeError
)
from app.modules.business.analytics.engine import BusinessAnalyticsEngine
from app.modules.business.analytics.constants import ALL_METRICS


@pytest.fixture
def engine():
    """Create an analytics engine instance."""
    return BusinessAnalyticsEngine(store_id=1)


@pytest.fixture
def sample_db_data():
    """Create sample database response data."""
    return [
        {
            "date": datetime(2024, 1, 1),
            "revenue": 1000.0,
            "orders": 10,
            "refunds": 1,
            "category_id": 1
        },
        {
            "date": datetime(2024, 1, 2),
            "revenue": 2000.0,
            "orders": 15,
            "refunds": 2,
            "category_id": 2
        }
    ]


def test_get_analytics_basic(engine, sample_db_data):
    """Test basic analytics retrieval."""
    with patch('app.modules.business.analytics.engine.db.session') as mock_db:
        # Mock database response
        mock_result = MagicMock()
        mock_result.__iter__.return_value = sample_db_data
        mock_db.execute.return_value = mock_result
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        result = engine.get_analytics(start_date, end_date)
        
        assert "current_period" in result
        assert "trends" in result
        assert len(result["trends"]) == 2  # Two days of data


def test_get_analytics_with_comparison(engine, sample_db_data):
    """Test analytics with previous period comparison."""
    with patch('app.modules.business.analytics.engine.db.session') as mock_db:
        # Mock database response
        mock_result = MagicMock()
        mock_result.__iter__.return_value = sample_db_data
        mock_db.execute.return_value = mock_result
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        result = engine.get_analytics(
            start_date,
            end_date,
            compare_previous=True
        )
        
        assert "current_period" in result
        assert "previous_period" in result
        assert "alerts" in result


def test_get_analytics_with_category(engine, sample_db_data):
    """Test analytics filtered by category."""
    with patch('app.modules.business.analytics.engine.db.session') as mock_db:
        # Mock database response
        mock_result = MagicMock()
        mock_result.__iter__.return_value = sample_db_data
        mock_db.execute.return_value = mock_result
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        result = engine.get_analytics(
            start_date,
            end_date,
            category_id=1
        )
        
        assert len(result["current_period"]) > 0


def test_get_analytics_invalid_dates(engine):
    """Test analytics with invalid date range."""
    end_date = datetime(2024, 1, 1)
    start_date = end_date + timedelta(days=1)
    
    with pytest.raises(InvalidDateRangeError):
        engine.get_analytics(start_date, end_date)


def test_get_analytics_db_error(engine):
    """Test handling of database errors."""
    with patch('app.modules.business.analytics.engine.db.session') as mock_db:
        mock_db.execute.side_effect = Exception("Database error")
        
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 2)
        
        with pytest.raises(DataFetchError):
            engine.get_analytics(start_date, end_date)


def test_get_category_metric_list(engine):
    """Test getting category metrics list."""
    metrics = engine.get_category_metric_list()
    assert metrics == ALL_METRICS
