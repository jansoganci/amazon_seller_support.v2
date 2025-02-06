"""
Business Report Metrics Configuration
"""
from typing import Dict, Any
from collections import defaultdict
from functools import reduce

from app.core.metrics.engine import metric_engine

BUSINESS_METRICS: Dict[str, Dict[str, Any]] = {
    'total_revenue': {
        'id': 'total_revenue',
        'name': 'Total Revenue',
        'description': 'Total revenue from all orders',
        'formula': lambda data, _: sum(float(d.get('ordered_product_sales', 0)) for d in data),
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
        'formula': lambda data, _: sum(int(d.get('units_ordered', 0)) for d in data),
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
        'formula': lambda data, _: sum(int(d.get('sessions', 0)) for d in data),
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
        'formula': lambda data, _: (
            sum(int(d.get('units_ordered', 0)) for d in data) / 
            sum(int(d.get('sessions', 0)) for d in data) * 100
            if sum(int(d.get('sessions', 0)) for d in data) > 0 else 0
        ),
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
        'formula': lambda data, _: (
            sum(float(d.get('ordered_product_sales', 0)) for d in data) / 
            sum(int(d.get('units_ordered', 0)) for d in data)
            if sum(int(d.get('units_ordered', 0)) for d in data) > 0 else 0
        ),
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
        'formula': lambda data, context: dict(
            reduce(
                lambda acc, d: acc.update({d.get('date'): acc.get(d.get('date'), 0) + float(d.get('ordered_product_sales', 0))}) or acc,
                [d for d in data if d.get('date')],
                defaultdict(float)
            )
        ),
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
        'formula': lambda data, context: dict(
            reduce(
                lambda acc, item: acc.update({item[0]: acc.get(item[0], 0) + item[1]}) or acc,
                [(cat.get('name', 'Uncategorized'), float(d.get('ordered_product_sales', 0)))
                 for d in data
                 for cat in d.get('categories', [])],
                defaultdict(float)
            )
        ),
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
        'formula': lambda data, context: dict(
            sorted(
                reduce(
                    lambda acc, d: acc.update({d.get('asin'): acc.get(d.get('asin'), 0) + float(d.get('ordered_product_sales', 0))}) or acc,
                    [d for d in data if d.get('asin')],
                    defaultdict(float)
                ).items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
        ),
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
    for metric_id, metric_config in BUSINESS_METRICS.items():
        metric_engine.register_metric(metric_config)

# Register metrics when module is imported
register_metrics()
