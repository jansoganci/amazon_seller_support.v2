"""Base analytics engine for all report types."""

from datetime import datetime
from typing import Dict, List, Optional, Union
from abc import ABC, abstractmethod

from app.core.metrics.engine import MetricEngine
from app.extensions import db

class BaseAnalyticsEngine(ABC):
    """Base analytics engine that all module-specific analytics engines should inherit from.
    
    This class provides common analytics functionality such as:
    - Basic metric calculations
    - Trend analysis
    - Data processing
    - Caching support
    
    Each module should extend this class and implement module-specific analytics.
    """
    
    def __init__(self, store_id: int):
        """Initialize analytics engine.
        
        Args:
            store_id: ID of the store to analyze
        """
        self.store_id = store_id
        self.metric_engine = MetricEngine()
        
    def calculate_base_metrics(self, data: List[Dict], metrics: List[str]) -> Dict:
        """Calculate base metrics using the metric engine.
        
        Args:
            data: List of data points to calculate metrics from
            metrics: List of metric IDs to calculate
            
        Returns:
            Dict containing calculated metrics
        """
        return self.metric_engine.calculate_metrics(data, metrics)
    
    def get_trends(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = 'daily'
    ) -> Dict:
        """Get trends for the specified period.
        
        Args:
            start_date: Start date for trend analysis
            end_date: End date for trend analysis
            group_by: How to group the data (daily/weekly/monthly)
            
        Returns:
            Dict containing trend data
        """
        return self._process_trends(
            self._get_data(start_date, end_date),
            group_by
        )
    
    @abstractmethod
    def _get_data(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Get raw data for analysis.
        
        This method should be implemented by each module to fetch its specific data.
        
        Args:
            start_date: Start date for data fetch
            end_date: End date for data fetch
            
        Returns:
            List of data points for analysis
        """
        pass
    
    def _process_trends(self, data: List[Dict], group_by: str) -> Dict:
        """Process raw data into trends.
        
        Args:
            data: Raw data points
            group_by: How to group the data
            
        Returns:
            Dict containing processed trend data
        """
        # Implement common trend processing logic here
        # Each module can override this if needed
        return {}
