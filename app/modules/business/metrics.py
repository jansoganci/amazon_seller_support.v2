"""
Business Report Metrics Configuration
"""
from typing import Dict, Any

BUSINESS_METRICS: Dict[str, Dict[str, Any]] = {
    'total_revenue': {
        'id': 'total_revenue',
        'name': 'Total Revenue',
        'description': 'Total revenue from all orders',
        'formula': 'sum(ordered_product_sales)',
        'category': 'sales',
        'visualization': {
            'type': 'currency',
            'format': '$0,0.00',
            'chartType': 'line',
            'options': {
                'compareWithPrevious': True,
                'stacked': False
            }
        },
        'thresholds': {
            'warning': 1000,
            'critical': 500,
            'direction': 'desc'
        },
        'caching': {
            'duration': 300,  # 5 minutes
            'key': ['store_id', 'date_range']
        }
    },
    'total_orders': {
        'id': 'total_orders',
        'name': 'Total Orders',
        'description': 'Total number of orders',
        'formula': 'sum(units_ordered)',
        'category': 'sales',
        'visualization': {
            'type': 'number',
            'format': '0,0',
            'chartType': 'line',
            'options': {
                'compareWithPrevious': True
            }
        },
        'caching': {
            'duration': 300,
            'key': ['store_id', 'date_range']
        }
    },
    'total_sessions': {
        'id': 'total_sessions',
        'name': 'Total Sessions',
        'description': 'Total number of customer sessions',
        'formula': 'sum(sessions)',
        'category': 'customer',
        'visualization': {
            'type': 'number',
            'format': '0,0',
            'chartType': 'line',
            'options': {
                'compareWithPrevious': True
            }
        }
    },
    'conversion_rate': {
        'id': 'conversion_rate',
        'name': 'Conversion Rate',
        'description': 'Percentage of sessions resulting in orders',
        'formula': '(sum(units_ordered) / sum(sessions)) * 100',
        'category': 'sales',
        'visualization': {
            'type': 'percentage',
            'format': '0.00%',
            'chartType': 'line'
        },
        'thresholds': {
            'warning': 2,
            'critical': 1,
            'direction': 'desc'
        }
    },
    'average_order_value': {
        'id': 'average_order_value',
        'name': 'Average Order Value',
        'description': 'Average revenue per order',
        'formula': 'sum(ordered_product_sales) / sum(units_ordered)',
        'category': 'sales',
        'visualization': {
            'type': 'currency',
            'format': '$0,0.00',
            'chartType': 'line'
        }
    },
    'daily_sales_trend': {
        'id': 'daily_sales_trend',
        'name': 'Daily Sales Trend',
        'description': 'Daily revenue trend over time',
        'formula': 'sum(ordered_product_sales)',
        'category': 'sales',
        'visualization': {
            'type': 'currency',
            'format': '$0,0.00',
            'chartType': 'line',
            'options': {
                'compareWithPrevious': True,
                'cumulative': False
            }
        },
        'groupBy': 'date'
    },
    'category_distribution': {
        'id': 'category_distribution',
        'name': 'Sales by Category',
        'description': 'Revenue distribution across categories',
        'formula': 'sum(ordered_product_sales)',
        'category': 'sales',
        'visualization': {
            'type': 'currency',
            'format': '$0,0.00',
            'chartType': 'pie'
        },
        'groupBy': 'category'
    },
    'top_products': {
        'id': 'top_products',
        'name': 'Top Products',
        'description': 'Best performing products by revenue',
        'formula': 'sum(ordered_product_sales)',
        'category': 'sales',
        'visualization': {
            'type': 'currency',
            'format': '$0,0.00',
            'chartType': 'bar',
            'options': {
                'limit': 10,
                'sort': 'desc'
            }
        },
        'groupBy': 'asin'
    }
}

def register_metrics():
    """Register all business metrics with the metric engine."""
    from app.core.metrics.engine import metric_engine
    
    for metric_id, metric_config in BUSINESS_METRICS.items():
        try:
            metric_engine.get_metric_config(metric_id)
        except ValueError:
            # Metric not registered yet, register it
            metric_engine.register_metric(metric_config)
