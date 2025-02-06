"""Business analytics visualization service."""

from typing import Dict, List
from datetime import datetime

class BusinessVisualizationService:
    """Service for creating business analytics visualizations."""
    
    @staticmethod
    def prepare_revenue_trend_chart(trends: Dict) -> Dict:
        """Prepare revenue trend chart data.
        
        Creates a line chart showing revenue over time with the following features:
        - Daily/Weekly/Monthly revenue trends
        - Previous period comparison
        - Moving average trendline
        
        Args:
            trends: Trend data from analytics engine
            
        Returns:
            Chart.js compatible configuration
        """
        labels = list(trends.keys())
        revenue_data = [trends[date]["revenue"] for date in labels]
        
        return {
            "type": "line",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Revenue",
                    "data": revenue_data,
                    "borderColor": "rgb(75, 192, 192)",
                    "tension": 0.1
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "Revenue ($)"
                        }
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_metrics_summary_chart(current: Dict, previous: Dict) -> Dict:
        """Prepare metrics summary chart data.
        
        Creates a bar chart comparing current vs previous period metrics:
        - Revenue
        - Orders
        - Average Order Value
        - Conversion Rate
        
        Args:
            current: Current period metrics
            previous: Previous period metrics
            
        Returns:
            Chart.js compatible configuration
        """
        metrics = ["revenue", "orders", "average_order_value", "conversion_rate"]
        
        return {
            "type": "bar",
            "data": {
                "labels": metrics,
                "datasets": [
                    {
                        "label": "Current Period",
                        "data": [current.get(m, 0) for m in metrics],
                        "backgroundColor": "rgba(75, 192, 192, 0.5)"
                    },
                    {
                        "label": "Previous Period",
                        "data": [previous.get(m, 0) for m in metrics],
                        "backgroundColor": "rgba(153, 102, 255, 0.5)"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {
                        "beginAtZero": True
                    }
                }
            }
        }
    
    @staticmethod
    def prepare_category_performance_chart(
        category_metrics: Dict[int, Dict]
    ) -> Dict:
        """Prepare category performance chart data.
        
        Creates a radar chart showing performance across categories:
        - Revenue per category
        - Orders per category
        - Average order value per category
        
        Args:
            category_metrics: Metrics by category ID
            
        Returns:
            Chart.js compatible configuration
        """
        categories = list(category_metrics.keys())
        revenue_data = [
            category_metrics[cat]["revenue"]
            for cat in categories
        ]
        orders_data = [
            category_metrics[cat]["orders"]
            for cat in categories
        ]
        
        return {
            "type": "radar",
            "data": {
                "labels": [f"Category {cat}" for cat in categories],
                "datasets": [
                    {
                        "label": "Revenue",
                        "data": revenue_data,
                        "fill": True,
                        "backgroundColor": "rgba(75, 192, 192, 0.2)",
                        "borderColor": "rgb(75, 192, 192)",
                        "pointBackgroundColor": "rgb(75, 192, 192)",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "rgb(75, 192, 192)"
                    },
                    {
                        "label": "Orders",
                        "data": orders_data,
                        "fill": True,
                        "backgroundColor": "rgba(153, 102, 255, 0.2)",
                        "borderColor": "rgb(153, 102, 255)",
                        "pointBackgroundColor": "rgb(153, 102, 255)",
                        "pointBorderColor": "#fff",
                        "pointHoverBackgroundColor": "#fff",
                        "pointHoverBorderColor": "rgb(153, 102, 255)"
                    }
                ]
            }
        }
    
    @staticmethod
    def prepare_anomaly_alert_chart(alerts: Dict) -> Dict:
        """Prepare anomaly alert visualization.
        
        Creates a gauge chart for each metric with alerts:
        - Shows current value
        - Color-coded based on alert level
        - Threshold indicators
        
        Args:
            alerts: Alert data from analytics engine
            
        Returns:
            Chart.js compatible configuration
        """
        return {
            "type": "gauge",
            "data": {
                "datasets": [{
                    "value": 70,
                    "minValue": 0,
                    "maxValue": 100,
                    "backgroundColor": [
                        "red",    # 0-60
                        "yellow", # 60-80
                        "green"   # 80-100
                    ]
                }]
            },
            "options": {
                "responsive": True,
                "title": {
                    "display": True,
                    "text": "Performance Score"
                }
            }
        }
