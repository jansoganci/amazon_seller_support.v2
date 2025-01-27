"""Test cases for business metrics."""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.metrics.engine import metric_engine
from app.modules.business.metrics import BUSINESS_METRICS, register_metrics

@pytest.fixture
def sample_data():
    """Sample business report data for testing."""
    return [
        {
            'date': '2024-01-01',
            'ordered_product_sales': '100.00',
            'units_ordered': '10',
            'sessions': '100',
            'page_views': '200',
            'category': 'Electronics'
        },
        {
            'date': '2024-01-02',
            'ordered_product_sales': '200.00',
            'units_ordered': '20',
            'sessions': '150',
            'page_views': '300',
            'category': 'Electronics'
        }
    ]

@pytest.fixture
def setup_metrics():
    """Register metrics before tests."""
    register_metrics()
    return metric_engine

def test_total_revenue_calculation(setup_metrics, sample_data):
    """Test total revenue metric calculation."""
    metric = setup_metrics.calculate_metric('total_revenue', sample_data)
    assert metric == '$300.00'

def test_conversion_rate_calculation(setup_metrics, sample_data):
    """Test conversion rate metric calculation."""
    metric = setup_metrics.calculate_metric('conversion_rate', sample_data)
    assert float(metric.replace('%', '')) == pytest.approx(12.0)  # (30 orders / 250 sessions) * 100

def test_average_order_value_calculation(setup_metrics, sample_data):
    """Test average order value metric calculation."""
    metric = setup_metrics.calculate_metric('average_order_value', sample_data)
    assert metric == '$10.00'  # $300 / 30 orders

def test_empty_data_handling(setup_metrics):
    """Test metric calculation with empty data."""
    empty_data = []
    for metric_id in BUSINESS_METRICS:
        value = setup_metrics.calculate_metric(metric_id, empty_data)
        if BUSINESS_METRICS[metric_id]['visualization']['type'] == 'currency':
            assert value == '$0.00'
        elif BUSINESS_METRICS[metric_id]['visualization']['type'] == 'percentage':
            assert value == '0.00%'
        else:
            assert value == '0'

def test_metric_caching(setup_metrics, sample_data):
    """Test that metrics are properly cached."""
    metric_id = 'total_revenue'
    context = {'store_id': 1, 'date_range': '2024-01-01-2024-01-02'}
    
    # First calculation
    value1 = setup_metrics.calculate_metric(metric_id, sample_data, context)
    
    # Modify data but use same cache key
    modified_data = sample_data.copy()
    modified_data[0]['ordered_product_sales'] = '1000.00'
    
    # Second calculation should return cached value
    value2 = setup_metrics.calculate_metric(metric_id, modified_data, context)
    
    assert value1 == value2

def test_invalid_metric_id(setup_metrics, sample_data):
    """Test handling of invalid metric IDs."""
    with pytest.raises(ValueError):
        setup_metrics.calculate_metric('invalid_metric', sample_data)

def test_metric_visualization_types(setup_metrics):
    """Test that all metrics have valid visualization types."""
    valid_types = {'currency', 'percentage', 'number', 'custom'}
    for metric_id, config in BUSINESS_METRICS.items():
        assert config['visualization']['type'] in valid_types

def test_metric_dependencies():
    """Test that all metric dependencies are valid."""
    for metric_id, config in BUSINESS_METRICS.items():
        if 'dependencies' in config:
            for dep in config['dependencies']:
                assert dep in BUSINESS_METRICS

def test_metric_formulas():
    """Test that all metric formulas are valid."""
    for metric_id, config in BUSINESS_METRICS.items():
        assert isinstance(config['formula'], (str, callable))
        if isinstance(config['formula'], str):
            # Basic syntax check for string formulas
            assert '(' in config['formula'] and ')' in config['formula']
