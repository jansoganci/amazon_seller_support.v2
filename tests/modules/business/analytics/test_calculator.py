"""Tests for BusinessMetricCalculator."""

from datetime import datetime
import pytest

from app.core.analytics.exceptions import MetricCalculationError
from app.modules.business.analytics.calculator import BusinessMetricCalculator
from app.modules.business.analytics.constants import (
    REVENUE,
    ORDERS,
    AVERAGE_ORDER_VALUE,
    REFUND_RATE
)


@pytest.fixture
def calculator():
    """Create a calculator instance."""
    return BusinessMetricCalculator()


@pytest.fixture
def sample_data():
    """Create sample business data."""
    return [
        {
            "revenue": 1000.0,
            "orders": 10,
            "refunds": 1
        },
        {
            "revenue": 2000.0,
            "orders": 15,
            "refunds": 2
        }
    ]


def test_calculate_metrics_all(calculator, sample_data):
    """Test calculating all metrics."""
    metrics = calculator.calculate_metrics(sample_data)
    
    assert metrics[REVENUE] == 3000.0
    assert metrics[ORDERS] == 25
    assert metrics[AVERAGE_ORDER_VALUE] == 120.0  # 3000/25
    assert metrics[REFUND_RATE] == 12.0  # (3/25)*100


def test_calculate_metrics_subset(calculator, sample_data):
    """Test calculating specific metrics."""
    metrics = calculator.calculate_metrics(
        sample_data,
        metrics=[REVENUE, ORDERS]
    )
    
    assert len(metrics) == 2
    assert REVENUE in metrics
    assert ORDERS in metrics
    assert AVERAGE_ORDER_VALUE not in metrics


def test_calculate_metrics_empty_data(calculator):
    """Test calculating metrics with empty data."""
    metrics = calculator.calculate_metrics([])
    
    assert metrics[REVENUE] == 0
    assert metrics[ORDERS] == 0
    assert metrics[AVERAGE_ORDER_VALUE] == 0
    assert metrics[REFUND_RATE] == 0


def test_calculate_metrics_invalid_data(calculator):
    """Test calculating metrics with invalid data."""
    with pytest.raises(MetricCalculationError):
        calculator.calculate_metrics([{"invalid": "data"}])


def test_detect_anomalies(calculator):
    """Test anomaly detection."""
    current = {
        REVENUE: 800.0,
        ORDERS: 10
    }
    previous = {
        REVENUE: 1000.0,
        ORDERS: 12
    }
    
    alerts = calculator.detect_anomalies(current, previous)
    
    assert REVENUE in alerts
    assert "warning" in alerts[REVENUE]  # 20% drop
