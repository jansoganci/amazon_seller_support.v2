"""Constants for business analytics calculations."""

from typing import Dict, List

# Metric IDs
REVENUE = "revenue"
ORDERS = "orders"
CONVERSION_RATE = "conversion_rate"
AVERAGE_ORDER_VALUE = "average_order_value"
REFUND_RATE = "refund_rate"

# Metric Groups
BASIC_METRICS = [REVENUE, ORDERS]
PERFORMANCE_METRICS = [CONVERSION_RATE, AVERAGE_ORDER_VALUE]
ALL_METRICS = BASIC_METRICS + PERFORMANCE_METRICS

# Default time periods for comparisons (in days)
DEFAULT_COMPARISON_PERIODS: Dict[str, int] = {
    "daily": 1,
    "weekly": 7,
    "monthly": 30,
    "quarterly": 90
}

# Thresholds for alerts
ALERT_THRESHOLDS: Dict[str, Dict[str, float]] = {
    REVENUE: {
        "critical_drop": -30.0,  # 30% drop
        "warning_drop": -15.0,   # 15% drop
    },
    CONVERSION_RATE: {
        "critical_drop": -20.0,  # 20% drop
        "warning_drop": -10.0,   # 10% drop
    }
}

# SQL Query Templates
REVENUE_QUERY = """
    SELECT 
        DATE(created_at) as date,
        SUM(total_amount) as revenue,
        COUNT(DISTINCT order_id) as orders,
        COUNT(DISTINCT CASE WHEN status = 'refunded' THEN order_id END) as refunds
    FROM business_orders
    WHERE store_id = :store_id
    AND created_at BETWEEN :start_date AND :end_date
    GROUP BY DATE(created_at)
    ORDER BY date
"""
