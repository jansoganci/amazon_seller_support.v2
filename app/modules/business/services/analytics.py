"""Business analytics engine for processing business report data."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_
from app.core.analytics.base import BaseAnalyticsEngine
from app.core.analytics.mixins import CategoryAwareMixin
from app.modules.business.models import BusinessReport

class BusinessAnalytics(CategoryAwareMixin, BaseAnalyticsEngine):
    """Analytics engine for business reports.
    
    This class provides business-specific analytics functionality including:
    - Sales metrics calculation
    - Revenue analysis
    - Conversion rate tracking
    - Category-based performance analysis
    """
    
    def _get_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get business report data for analysis.
        
        Args:
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            List of business report data points
        """
        reports = BusinessReport.query.filter(
            and_(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            )
        ).all()
        
        return [report.to_dict() for report in reports]
    
    def get_category_metric_list(self) -> List[str]:
        """Get list of business metrics for category analysis.
        
        Returns:
            List of metric IDs relevant for category analysis
        """
        return [
            "total_revenue",
            "total_orders",
            "conversion_rate",
            "average_order_value"
        ]
    
    def get_sales_metrics(
        self,
        start_date: datetime,
        end_date: datetime,
        category_id: Optional[int] = None
    ) -> Dict:
        """Calculate sales-specific metrics.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            category_id: Optional category ID for filtering
            
        Returns:
            Dict containing sales metrics
        """
        data = self._get_data(start_date, end_date)
        
        if category_id:
            data = self.filter_by_category(data, category_id=category_id)
            
        return self.calculate_base_metrics(data, [
            "total_revenue",
            "total_orders",
            "total_units",
            "conversion_rate",
            "average_order_value"
        ])
    
    def get_performance_comparison(
        self,
        current_start: datetime,
        current_end: datetime,
        previous_start: datetime,
        previous_end: datetime,
        category_id: Optional[int] = None
    ) -> Dict:
        """Compare performance between two time periods.
        
        Args:
            current_start: Start date for current period
            current_end: End date for current period
            previous_start: Start date for previous period
            previous_end: End date for previous period
            category_id: Optional category ID for filtering
            
        Returns:
            Dict containing performance comparison
        """
        current_metrics = self.get_sales_metrics(
            current_start,
            current_end,
            category_id
        )
        previous_metrics = self.get_sales_metrics(
            previous_start,
            previous_end,
            category_id
        )
        
        return {
            "current": current_metrics,
            "previous": previous_metrics,
            "growth": self._calculate_growth(current_metrics, previous_metrics)
        }
    
    def _calculate_growth(self, current: Dict, previous: Dict) -> Dict:
        """Calculate growth rates between two periods.
        
        Args:
            current: Current period metrics
            previous: Previous period metrics
            
        Returns:
            Dict containing growth rates
        """
        growth = {}
        for metric in current:
            if metric in previous and previous[metric] != 0:
                growth[metric] = (
                    (current[metric] - previous[metric]) / previous[metric]
                ) * 100
            else:
                growth[metric] = 0
                
        return growth
