"""Business analytics engine for processing business report data."""

from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import and_
from app.extensions import db
from app.core.analytics.base import BaseAnalyticsEngine
from app.core.analytics.mixins import CategoryAwareMixin
from app.core.metrics.engine import metric_engine
from app.modules.business.models import BusinessReport
from app.modules.business.metrics import BUSINESS_METRICS

class BusinessAnalytics(CategoryAwareMixin, BaseAnalyticsEngine):
    """Analytics engine for business reports.
    
    This class provides business-specific analytics functionality including:
    - Sales metrics calculation
    - Revenue analysis
    - Conversion rate tracking
    - Category-based performance analysis
    """
    
    def _get_data(self, start_date: datetime, end_date: datetime, category_id: Optional[int] = None) -> List[Dict]:
        """Get business report data for analysis.
        
        Args:
            start_date: Start date for data fetch
            end_date: End date for data fetch
            category_id: Optional category ID for filtering
            
        Returns:
            List of business report data points
        """
        query = BusinessReport.query.filter(
            and_(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            )
        )
        
        if category_id:
            # Load tables dynamically
            asin_categories = db.Table('asin_categories', db.metadata, autoload_with=db.engine)
            categories = db.Table('categories', db.metadata, autoload_with=db.engine)
            
            query = query.join(
                asin_categories,
                BusinessReport.asin == asin_categories.c.asin
            ).join(
                categories,
                asin_categories.c.category_id == categories.c.id
            ).filter(categories.c.id == category_id)
        
        reports = query.all()
        return [report.to_dict() for report in reports]
    
    def get_category_metric_list(self) -> List[str]:
        """Get list of business metrics for category analysis.
        
        Returns:
            List of metric IDs relevant for category analysis
        """
        return [
            {"id": "total_revenue", "name": "Total Revenue"},
            {"id": "total_orders", "name": "Total Orders"},
            {"id": "conversion_rate", "name": "Conversion Rate"},
            {"id": "average_order_value", "name": "Average Order Value"}
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
        data = self._get_data(start_date, end_date, category_id)
        
        metrics = list(BUSINESS_METRICS.keys())
        
        return self.calculate_base_metrics(data, [m["id"] for m in metrics])
    
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
