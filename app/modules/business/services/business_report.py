"""Business report service module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.modules.business.models import BusinessReport
from app.modules.business.services.analytics import BusinessAnalytics

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BusinessReportService:
    """Service class for business report operations."""
    
    def __init__(self, store_id: int):
        """Initialize service with store ID."""
        self.store_id = store_id
        self.analytics = BusinessAnalytics(store_id)
        logger.debug(f"Initialized BusinessReportService for store_id: {store_id}")
    
    def get_trends(
        self,
        start_date: datetime,
        end_date: datetime,
        category_id: Optional[int] = None
    ) -> Dict:
        """Get business trends for the specified date range.
        
        Args:
            start_date: Start date for trend analysis
            end_date: End date for trend analysis
            category_id: Optional category ID for filtering
            
        Returns:
            Dict containing trend data and growth rates
        """
        try:
            logger.debug(f"Fetching trends for store {self.store_id} from {start_date} to {end_date}")
            
            # Get current period performance
            current_metrics = self.analytics.get_sales_metrics(
                start_date,
                end_date,
                category_id
            )
            
            # Get previous period for comparison
            prev_start = start_date - (end_date - start_date)
            prev_end = start_date
            
            # Get performance comparison
            comparison = self.analytics.get_performance_comparison(
                start_date,
                end_date,
                prev_start,
                prev_end,
                category_id
            )
            
            logger.debug(f"Calculated metrics: {comparison}")
            return comparison
            
        except Exception as e:
            logger.exception(f"Error getting business trends: {str(e)}")
            return {}
    
    def get_categories(self) -> List[str]:
        """Get unique categories from reports."""
        try:
            logger.debug(f"Fetching categories for store {self.store_id}")
            reports = BusinessReport.query.filter_by(store_id=self.store_id).all()
            categories = sorted(list(set(report.category for report in reports if report.category)))
            logger.debug(f"Found categories: {categories}")
            return categories
        except Exception as e:
            logger.exception(f"Error getting categories: {str(e)}")
            return []
    
    def get_asins(self) -> List[Dict]:
        """Get unique ASINs with titles."""
        try:
            logger.debug(f"Fetching ASINs for store {self.store_id}")
            reports = BusinessReport.query.filter_by(store_id=self.store_id).all()
            asin_dict = {}
            for report in reports:
                if report.asin and report.asin not in asin_dict:
                    asin_dict[report.asin] = {
                        'asin': report.asin,
                        'title': report.title
                    }
            return list(asin_dict.values())
        except Exception as e:
            logger.exception(f"Error getting ASINs: {str(e)}")
            return []
    
    def get_category_comparison(
        self,
        start_date: datetime,
        end_date: datetime,
        category_ids: List[int]
    ) -> Dict:
        """Compare performance across different categories.
        
        Args:
            start_date: Start date for comparison
            end_date: End date for comparison
            category_ids: List of category IDs to compare
            
        Returns:
            Dict containing category comparison data
        """
        try:
            logger.debug(f"Comparing categories {category_ids}")
            return self.analytics.compare_categories(
                start_date,
                end_date,
                category_ids
            )
        except Exception as e:
            logger.exception(f"Error comparing categories: {str(e)}")
            return {}
