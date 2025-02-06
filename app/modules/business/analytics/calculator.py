"""Business metrics calculator."""

from typing import Dict, List, Optional
from datetime import datetime

from app.core.analytics.exceptions import MetricCalculationError
from .constants import (
    REVENUE,
    ORDERS,
    CONVERSION_RATE,
    AVERAGE_ORDER_VALUE,
    REFUND_RATE,
    ALERT_THRESHOLDS
)


class BusinessMetricCalculator:
    """Calculator for business-specific metrics."""
    
    def calculate_metrics(
        self,
        data: List[Dict],
        metrics: Optional[List[str]] = None
    ) -> Dict[str, float]:
        """Calculate requested business metrics.
        
        Args:
            data: List of data points with revenue and order information
            metrics: List of metrics to calculate, calculates all if None
            
        Returns:
            Dictionary of calculated metrics
            
        Raises:
            MetricCalculationError: If calculation fails
        """
        try:
            result = {}
            
            # Calculate base metrics
            total_revenue = sum(item.get('revenue', 0) for item in data)
            total_orders = sum(item.get('orders', 0) for item in data)
            total_refunds = sum(item.get('refunds', 0) for item in data)
            
            # Calculate each requested metric
            if not metrics or REVENUE in metrics:
                result[REVENUE] = total_revenue
                
            if not metrics or ORDERS in metrics:
                result[ORDERS] = total_orders
                
            if not metrics or AVERAGE_ORDER_VALUE in metrics:
                result[AVERAGE_ORDER_VALUE] = (
                    total_revenue / total_orders if total_orders > 0 else 0
                )
                
            if not metrics or REFUND_RATE in metrics:
                result[REFUND_RATE] = (
                    (total_refunds / total_orders * 100)
                    if total_orders > 0 else 0
                )
                
            return result
            
        except Exception as e:
            raise MetricCalculationError(
                "Failed to calculate business metrics",
                details={"error": str(e)}
            )
    
    def detect_anomalies(
        self,
        current_metrics: Dict[str, float],
        previous_metrics: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """Detect anomalies in metrics by comparing with previous period.
        
        Args:
            current_metrics: Current period metrics
            previous_metrics: Previous period metrics
            
        Returns:
            Dictionary of metric IDs and their alert levels
        """
        alerts = {}
        
        for metric, thresholds in ALERT_THRESHOLDS.items():
            if metric not in current_metrics or metric not in previous_metrics:
                continue
                
            current_value = current_metrics[metric]
            previous_value = previous_metrics[metric]
            
            if previous_value == 0:
                continue
                
            change_percent = (
                (current_value - previous_value) / previous_value * 100
            )
            
            metric_alerts = []
            if change_percent <= thresholds['critical_drop']:
                metric_alerts.append('critical')
            elif change_percent <= thresholds['warning_drop']:
                metric_alerts.append('warning')
                
            if metric_alerts:
                alerts[metric] = metric_alerts
                
        return alerts
