"""Business report service module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.modules.business.models import BusinessReport

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class BusinessReportService:
    """Service class for business report operations."""
    
    def __init__(self, store_id: int):
        """Initialize service with store ID."""
        self.store_id = store_id
        logger.debug(f"Initialized BusinessReportService for store_id: {store_id}")
    
    def get_trends(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get business trends for the specified date range."""
        try:
            logger.debug(f"Fetching trends for store {self.store_id} from {start_date} to {end_date}")
            reports = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            ).all()
            logger.debug(f"Found {len(reports)} reports")
            
            if not reports:
                logger.warning(f"No reports found for store {self.store_id} in date range")
                return {}
            
            # Calculate metrics
            total_sales = sum(report.ordered_product_sales for report in reports)
            total_orders = sum(report.total_order_items for report in reports)
            total_sessions = sum(report.sessions for report in reports)
            total_units = sum(report.units_ordered for report in reports)
            
            # Calculate conversion rate
            avg_conversion = (total_units / total_sessions * 100) if total_sessions > 0 else 0
            
            # Calculate growth rates (comparing to previous period)
            prev_start = start_date - (end_date - start_date)
            prev_reports = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(prev_start, start_date)
            ).all()
            
            prev_sales = sum(report.ordered_product_sales for report in prev_reports) if prev_reports else 0
            prev_orders = sum(report.total_order_items for report in prev_reports) if prev_reports else 0
            prev_sessions = sum(report.sessions for report in prev_reports) if prev_reports else 0
            prev_units = sum(report.units_ordered for report in prev_reports) if prev_reports else 0
            
            # Calculate growth rates
            sales_growth = ((total_sales - prev_sales) / prev_sales * 100) if prev_sales > 0 else 0
            orders_growth = ((total_orders - prev_orders) / prev_orders * 100) if prev_orders > 0 else 0
            sessions_growth = ((total_sessions - prev_sessions) / prev_sessions * 100) if prev_sessions > 0 else 0
            conversion_growth = (avg_conversion - (prev_units / prev_sessions * 100 if prev_sessions > 0 else 0)) if prev_sessions > 0 else 0
            
            result = {
                'ordered_product_sales': total_sales,
                'ordered_product_sales_growth': sales_growth,
                'total_order_items': total_orders,
                'total_order_items_growth': orders_growth,
                'sessions': total_sessions,
                'sessions_growth': sessions_growth,
                'conversion_rate': avg_conversion,
                'conversion_rate_growth': conversion_growth
            }
            
            logger.debug(f"Calculated metrics: {result}")
            return result
            
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
            result = sorted(list(asin_dict.values()), key=lambda x: x['asin'])
            logger.debug(f"Found {len(result)} unique ASINs")
            return result
        except Exception as e:
            logger.exception(f"Error getting ASINs: {str(e)}")
            return []
    
    def get_report_data(self, start_date: datetime, end_date: datetime, 
                       category: Optional[str] = None, asin: Optional[str] = None) -> List[Dict]:
        """Get report data with optional filters."""
        try:
            logger.debug(f"Fetching report data for store {self.store_id} from {start_date} to {end_date}")
            query = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            )
            
            if category:
                query = query.filter(BusinessReport.category == category)
            if asin:
                query = query.filter(BusinessReport.asin == asin)
                
            reports = query.order_by(BusinessReport.date).all()
            logger.debug(f"Found {len(reports)} reports")
            
            return [{
                'date': report.date.strftime('%Y-%m-%d'),
                'ordered_product_sales': report.ordered_product_sales,
                'total_order_items': report.total_order_items,
                'sessions': report.sessions,
                'units_ordered': report.units_ordered,
                'conversion_rate': report.conversion_rate
            } for report in reports]
            
        except Exception as e:
            logger.exception(f"Error getting report data: {str(e)}")
            return []
