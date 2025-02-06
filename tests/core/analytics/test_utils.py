"""Tests for analytics utility functions."""

from datetime import datetime, timedelta
import pytest

from app.core.analytics.utils import (
    validate_date_range,
    group_data_by_period,
    calculate_percentage_change
)
from app.core.analytics.exceptions import InvalidDateRangeError


def test_validate_date_range_valid():
    """Test date range validation with valid dates."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)
    
    # Should not raise an exception
    validate_date_range(start_date, end_date)
    validate_date_range(start_date, end_date, max_range_days=31)


def test_validate_date_range_invalid():
    """Test date range validation with invalid dates."""
    start_date = datetime(2024, 1, 31)
    end_date = datetime(2024, 1, 1)
    
    with pytest.raises(InvalidDateRangeError):
        validate_date_range(start_date, end_date)


def test_validate_date_range_max_days():
    """Test date range validation with max days limit."""
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 2, 1)
    
    with pytest.raises(InvalidDateRangeError):
        validate_date_range(start_date, end_date, max_range_days=30)


def test_group_data_by_period_daily():
    """Test grouping data by daily periods."""
    data = [
        {"date": "2024-01-01", "value": 1},
        {"date": "2024-01-01", "value": 2},
        {"date": "2024-01-02", "value": 3}
    ]
    
    grouped = group_data_by_period(data, "date", "daily")
    
    assert len(grouped) == 2
    assert len(grouped["2024-01-01"]) == 2
    assert len(grouped["2024-01-02"]) == 1


def test_calculate_percentage_change():
    """Test percentage change calculation."""
    assert calculate_percentage_change(110, 100) == 10.0
    assert calculate_percentage_change(90, 100) == -10.0
    assert calculate_percentage_change(100, 0) == 100.0
    assert calculate_percentage_change(0, 0) == 0.0
