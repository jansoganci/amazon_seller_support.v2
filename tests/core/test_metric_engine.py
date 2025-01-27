"""Test cases for the metric engine."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.metrics.engine import metric_engine
from app.modules.business.metrics import BUSINESS_METRICS, register_metrics

@pytest.fixture
def setup_metric_engine():
    """Set up metric engine for testing."""
    metric_engine._metrics.clear()  # Clear existing metrics
    register_metrics()
    return metric_engine

@pytest.fixture
def sample_metric_data():
    """Create sample data for metric testing."""
    base_date = datetime.now().date()
    return [
        {
            'date': base_date - timedelta(days=i),
            'ordered_product_sales': Decimal('1000.00'),
            'units_ordered': 10,
            'sessions': 100,
            'page_views': 150,
            'category': 'Electronics'
        }
        for i in range(5)
    ]

def test_metric_registration(setup_metric_engine):
    """Test that metrics are properly registered."""
    for metric_id in BUSINESS_METRICS:
        assert metric_id in setup_metric_engine._metrics
        assert setup_metric_engine.get_metric_config(metric_id) == BUSINESS_METRICS[metric_id]

def test_metric_calculation(setup_metric_engine, sample_metric_data):
    """Test metric calculation functionality."""
    # Test total revenue calculation
    total_revenue = setup_metric_engine.calculate_metric(
        'total_revenue',
        sample_metric_data
    )
    assert total_revenue == '$5,000.00'  # 1000 * 5 days

    # Test conversion rate calculation
    conversion_rate = setup_metric_engine.calculate_metric(
        'conversion_rate',
        sample_metric_data
    )
    assert float(conversion_rate.replace('%', '')) == pytest.approx(10.0)  # (50 orders / 500 sessions) * 100

def test_metric_caching(setup_metric_engine, sample_metric_data):
    """Test metric caching functionality."""
    context = {'store_id': 1, 'date_range': '2024-01-01-2024-01-05'}
    
    # First calculation
    value1 = setup_metric_engine.calculate_metric(
        'total_revenue',
        sample_metric_data,
        context
    )
    
    # Modify data but use same cache key
    modified_data = sample_metric_data.copy()
    modified_data[0]['ordered_product_sales'] = Decimal('2000.00')
    
    # Second calculation should return cached value
    value2 = setup_metric_engine.calculate_metric(
        'total_revenue',
        modified_data,
        context
    )
    
    assert value1 == value2

def test_metric_threshold_evaluation(setup_metric_engine, sample_metric_data):
    """Test metric threshold evaluation."""
    # Test critical threshold
    critical_data = [{'ordered_product_sales': Decimal('100.00')}]
    total_revenue = setup_metric_engine.calculate_metric(
        'total_revenue',
        critical_data
    )
    assert setup_metric_engine.evaluate_thresholds(
        'total_revenue',
        float(total_revenue.replace('$', '').replace(',', ''))
    ) == 'critical'
    
    # Test warning threshold
    warning_data = [{'ordered_product_sales': Decimal('750.00')}]
    total_revenue = setup_metric_engine.calculate_metric(
        'total_revenue',
        warning_data
    )
    assert setup_metric_engine.evaluate_thresholds(
        'total_revenue',
        float(total_revenue.replace('$', '').replace(',', ''))
    ) == 'warning'
    
    # Test normal threshold
    normal_data = [{'ordered_product_sales': Decimal('2000.00')}]
    total_revenue = setup_metric_engine.calculate_metric(
        'total_revenue',
        normal_data
    )
    assert setup_metric_engine.evaluate_thresholds(
        'total_revenue',
        float(total_revenue.replace('$', '').replace(',', ''))
    ) == 'normal'

def test_metric_formula_evaluation(setup_metric_engine, sample_metric_data):
    """Test metric formula evaluation."""
    # Test simple sum formula
    total_sessions = setup_metric_engine.calculate_metric(
        'total_sessions',
        sample_metric_data
    )
    assert int(total_sessions.replace(',', '')) == 500  # 100 * 5 days
    
    # Test complex formula (average order value)
    aov = setup_metric_engine.calculate_metric(
        'average_order_value',
        sample_metric_data
    )
    assert float(aov.replace('$', '').replace(',', '')) == pytest.approx(100.0)  # 1000 / 10

def test_metric_visualization_format(setup_metric_engine, sample_metric_data):
    """Test metric value formatting based on visualization type."""
    # Test currency format
    revenue = setup_metric_engine.calculate_metric(
        'total_revenue',
        sample_metric_data
    )
    assert revenue.startswith('$') and ',' in revenue
    
    # Test percentage format
    conversion = setup_metric_engine.calculate_metric(
        'conversion_rate',
        sample_metric_data
    )
    assert conversion.endswith('%') and '.' in conversion
    
    # Test number format
    sessions = setup_metric_engine.calculate_metric(
        'total_sessions',
        sample_metric_data
    )
    assert ',' in sessions and not ('$' in sessions or '%' in sessions)

def test_empty_data_handling(setup_metric_engine):
    """Test metric calculation with empty data."""
    empty_data = []
    
    # Test all metrics with empty data
    for metric_id in BUSINESS_METRICS:
        value = setup_metric_engine.calculate_metric(metric_id, empty_data)
        config = BUSINESS_METRICS[metric_id]
        
        # Verify format based on visualization type
        if config['visualization']['type'] == 'currency':
            assert value == '$0.00'
        elif config['visualization']['type'] == 'percentage':
            assert value == '0.00%'
        else:
            assert value == '0'

def test_metric_error_handling(setup_metric_engine, sample_metric_data):
    """Test error handling in metric calculations."""
    # Test invalid metric ID
    with pytest.raises(ValueError):
        setup_metric_engine.calculate_metric('invalid_metric', sample_metric_data)
    
    # Test invalid formula
    invalid_metric = {
        'id': 'test_metric',
        'name': 'Test Metric',
        'formula': 'invalid_formula(x)',
        'category': 'test',
        'visualization': {'type': 'number'}
    }
    setup_metric_engine.register_metric(invalid_metric)
    
    with pytest.raises(ValueError):
        setup_metric_engine.calculate_metric('test_metric', sample_metric_data)

def test_concurrent_metric_calculation(setup_metric_engine, sample_metric_data):
    """Test concurrent metric calculations."""
    import concurrent.futures
    
    def calculate_metric():
        return setup_metric_engine.calculate_metric(
            'total_revenue',
            sample_metric_data,
            {'store_id': 1}
        )
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(lambda _: calculate_metric(), range(5)))
    
    # All results should be identical
    assert len(set(results)) == 1
