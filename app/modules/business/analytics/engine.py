"""Business analytics engine implementation."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from sqlalchemy import text
from app.core.analytics.base import BaseAnalyticsEngine
from app.core.analytics.mixins import CategoryAwareMixin
from app.core.analytics.exceptions import (
    DataFetchError,
    InvalidDateRangeError
)
from app.core.analytics.utils import (
    validate_date_range,
    group_data_by_period
)
from app.extensions import db

from .calculator import BusinessMetricCalculator
from .constants import (
    ALL_METRICS,
    DEFAULT_COMPARISON_PERIODS,
    REVENUE_QUERY
)


class BusinessAnalyticsEngine(CategoryAwareMixin, BaseAnalyticsEngine):
    """Analytics engine for business metrics.
    
    This engine handles:
    - Revenue analytics
    - Order metrics
    - Performance indicators
    - Category-based analysis
    """
    
    def __init__(self, store_id: int):
        """Initialize the business analytics engine.
        
        Args:
            store_id: ID of the store to analyze
        """
        super().__init__(store_id)
        self.calculator = BusinessMetricCalculator()
        
    def get_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        metrics: Optional[List[str]] = None,
        category_id: Optional[int] = None,
        compare_previous: bool = False,
        group_by: str = 'daily'
    ) -> Dict:
        """Get business analytics for the specified period.
        
        Args:
            start_date: Start date for analysis
            end_date: End date for analysis
            metrics: List of metrics to calculate (default: all)
            category_id: Optional category ID to filter by
            compare_previous: Whether to include previous period comparison
            group_by: How to group the data (daily/weekly/monthly)
            
        Returns:
            Dict containing:
            - current_period: Current period metrics
            - previous_period: Previous period metrics (if requested)
            - trends: Trend data grouped by specified period
            - alerts: Any detected anomalies
        """
        # Validate dates
        validate_date_range(start_date, end_date)
        
        # Get current period data
        current_data = self._get_data(start_date, end_date)
        
        # Apply category filter if needed
        if category_id:
            current_data = self.filter_by_category(current_data, category_id)
        
        # Calculate current period metrics
        current_metrics = self.calculator.calculate_metrics(
            current_data,
            metrics
        )
        
        result = {
            "current_period": current_metrics,
            "trends": self._process_trends(current_data, group_by)
        }
        
        # Add previous period comparison if requested
        if compare_previous:
            period_days = (end_date - start_date).days
            previous_start = start_date - timedelta(days=period_days)
            previous_end = start_date - timedelta(days=1)
            
            previous_data = self._get_data(previous_start, previous_end)
            if category_id:
                previous_data = self.filter_by_category(
                    previous_data,
                    category_id
                )
            
            previous_metrics = self.calculator.calculate_metrics(
                previous_data,
                metrics
            )
            
            result["previous_period"] = previous_metrics
            result["alerts"] = self.calculator.detect_anomalies(
                current_metrics,
                previous_metrics
            )
        
        return result
    
    def _get_data(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get raw business data for analysis.
        
        Args:
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            List of data points with revenue and order information
            
        Raises:
            DataFetchError: If data fetch fails
        """
        try:
            result = db.session.execute(
                text(REVENUE_QUERY),
                {
                    "store_id": self.store_id,
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            return [dict(row) for row in result]
            
        except Exception as e:
            raise DataFetchError(
                "Failed to fetch business data",
                details={"error": str(e)}
            )
    
    def _process_trends(
        self,
        data: List[Dict],
        group_by: str = 'daily'
    ) -> Dict:
        """Process raw data into trends.
        
        Args:
            data: Raw data points
            group_by: How to group the data
            
        Returns:
            Dict containing trend data grouped by period
        """
        grouped_data = group_data_by_period(data, 'date', group_by)
        
        trends = {}
        for period, period_data in grouped_data.items():
            trends[period] = self.calculator.calculate_metrics(
                period_data,
                ALL_METRICS
            )
            
        return trends
    
    def get_category_metric_list(self) -> List[str]:
        """Get list of metrics to calculate for categories.
        
        Returns:
            List of metric IDs relevant for category analysis
        """
        return ALL_METRICS
