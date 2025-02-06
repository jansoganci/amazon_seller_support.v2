"""Business report service module."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from decimal import Decimal
import logging
import json

from sqlalchemy import text
from app.extensions import db
from app.modules.business.models import BusinessReport
from app.modules.business.services.analytics import BusinessAnalytics
from app.core.metrics.engine import metric_engine
from app.modules.business.metrics import BUSINESS_METRICS

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
            
        Raises:
            ValueError: If dates are invalid or in the future
        """
        # Validate dates
        now = datetime.utcnow()
        if end_date > now:
            logger.warning(f"End date {end_date} is in the future, adjusting to current time")
            end_date = now
            start_date = end_date - (end_date - start_date)
            
        if start_date > end_date:
            raise ValueError("Start date cannot be after end date")
            
        try:
            logger.debug(f"Fetching trends for store {self.store_id} from {start_date} to {end_date}")
            
            # Get current period data
            query = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            )
            
            if category_id:
                query = query.join(BusinessReport.categories)\
                    .filter(BusinessReport.categories.any(id=category_id))
            
            current_data = [report.to_dict() for report in query.all()]
            
            # Get previous period data
            prev_start = start_date - (end_date - start_date)
            prev_end = start_date
            
            prev_query = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(prev_start, prev_end)
            )
            
            if category_id:
                prev_query = prev_query.join(BusinessReport.categories)\
                    .filter(BusinessReport.categories.any(id=category_id))
            
            previous_data = [report.to_dict() for report in prev_query.all()]
            
            # Calculate metrics for both periods
            result = {}
            context = {
                'store_id': self.store_id,
                'start_date': start_date,
                'end_date': end_date,
                'category_id': category_id
            }
            
            for metric_id in BUSINESS_METRICS:
                try:
                    # Calculate current period metric
                    current_value = metric_engine.calculate_metric(
                        metric_id,
                        current_data,
                        context=context
                    )
                    result[metric_id] = current_value
                    
                    # Calculate previous period metric for growth rate
                    prev_context = {
                        'store_id': self.store_id,
                        'start_date': prev_start,
                        'end_date': prev_end,
                        'category_id': category_id
                    }
                    prev_value = metric_engine.calculate_metric(
                        metric_id,
                        previous_data,
                        context=prev_context
                    )
                    
                    # Calculate growth rate
                    try:
                        if isinstance(current_value, (int, float, Decimal)):
                            current_float = float(current_value)
                        else:
                            current_float = float(str(current_value).replace('$', '').replace('%', '').replace(',', ''))
                            
                        if isinstance(prev_value, (int, float, Decimal)):
                            prev_float = float(prev_value)
                        else:
                            prev_float = float(str(prev_value).replace('$', '').replace('%', '').replace(',', ''))
                        
                        if prev_float != 0:
                            growth = ((current_float - prev_float) / prev_float) * 100
                        else:
                            growth = 0 if current_float == 0 else 100
                    except (ValueError, TypeError):
                        growth = 0
                        
                    result[f"{metric_id}_growth"] = growth
                    
                except Exception as e:
                    logger.error(f"Error calculating metric {metric_id}: {str(e)}")
                    result[metric_id] = "N/A"
                    result[f"{metric_id}_growth"] = 0
            
            logger.debug(f"Calculated metrics: {result}")
            return result
            
        except Exception as e:
            logger.exception(f"Error getting business trends: {str(e)}")
            # Return empty metrics on error
            return {metric_id: "N/A" for metric_id in BUSINESS_METRICS}
    
    def get_categories(self) -> List[Dict[str, str]]:
        """Get unique categories and subcategories from reports."""
        try:
            logger.debug(f"Fetching categories for store {self.store_id}")
            
            # Query categories with proper joins using SQLAlchemy Table objects
            asin_categories = db.Table('asin_categories', db.metadata, autoload_with=db.engine)
            categories = db.Table('categories', db.metadata, autoload_with=db.engine)
            
            stmt = db.select(categories.c.name.label('category'))\
                .select_from(BusinessReport)\
                .join(asin_categories, BusinessReport.asin == asin_categories.c.asin)\
                .join(categories, asin_categories.c.category_id == categories.c.id)\
                .where(BusinessReport.store_id == self.store_id)\
                .distinct()\
                .order_by(categories.c.name)
            
            result = [{'category': c[0]} for c in db.session.execute(stmt).all()]
            logger.debug(f"Found categories: {result}")
            return result
            
        except Exception as e:
            logger.exception(f"Error getting categories: {str(e)}")
            return []
    
    def get_asins(self) -> List[Dict]:
        """Get unique ASINs with titles and categories."""
        try:
            logger.debug(f"Fetching ASINs for store {self.store_id}")
            
            # Query ASINs with category information using SQLAlchemy Table objects
            asin_categories = db.Table('asin_categories', db.metadata, autoload_with=db.engine)
            categories = db.Table('categories', db.metadata, autoload_with=db.engine)
            
            stmt = db.select(
                BusinessReport.asin,
                BusinessReport.title,
                categories.c.name.label('category')
            ).distinct()\
            .select_from(BusinessReport)\
            .outerjoin(asin_categories, BusinessReport.asin == asin_categories.c.asin)\
            .outerjoin(categories, asin_categories.c.category_id == categories.c.id)\
            .where(BusinessReport.store_id == self.store_id)\
            .order_by(BusinessReport.asin)
            
            results = db.session.execute(stmt).all()
            
            asin_dict = {}
            for result in results:
                if result.asin and result.asin not in asin_dict:
                    asin_dict[result.asin] = {
                        'asin': result.asin,
                        'title': result.title,
                        'category': result.category
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
            
    def get_revenue_chart_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get revenue trend chart data."""
        try:
            # Get trends data which includes daily_sales_trend
            trends_data = self.get_trends(start_date, end_date)
            daily_trend_str = trends_data.get('daily_sales_trend', '{}')
            daily_trend = json.loads(daily_trend_str) if isinstance(daily_trend_str, str) else daily_trend_str
            
            # Sort dates for proper timeline
            sorted_dates = sorted(daily_trend.keys())
            dates = [datetime.fromisoformat(d).strftime('%Y-%m-%d') for d in sorted_dates]
            revenue = [float(daily_trend[d]) if isinstance(daily_trend[d], (int, float, str)) else 0.0 for d in sorted_dates]
            
            return {
                'type': 'line',
                'data': {
                    'labels': dates,
                    'datasets': [{
                        'label': 'Daily Revenue',
                        'data': revenue,
                        'borderColor': '#3b82f6',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'fill': True
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return "$" + value.toLocaleString(); }'
                            }
                        }
                    },
                    'plugins': {
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return "$" + context.parsed.y.toLocaleString(); }'
                            }
                        }
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting revenue chart data: {str(e)}")
            return self._get_empty_chart_data()
    
    def get_metrics_chart_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get metrics summary chart data."""
        try:
            current_metrics = self.get_trends(start_date, end_date)
            prev_start = start_date - (end_date - start_date)
            prev_metrics = self.get_trends(prev_start, start_date)
            
            metrics = [
                'total_revenue', 'total_orders', 'total_units',
                'conversion_rate', 'average_order_value'
            ]
            
            def safe_float(value):
                if isinstance(value, (int, float, Decimal)):
                    return float(value)
                if isinstance(value, str):
                    if value == 'N/A':
                        return 0.0
                    return float(value.replace('$', '').replace('%', '').replace(',', ''))
                return 0.0
            
            current_values = [safe_float(current_metrics.get(m, 0)) for m in metrics]
            prev_values = [safe_float(prev_metrics.get(m, 0)) for m in metrics]
            
            return {
                'type': 'bar',
                'data': {
                    'labels': ['Revenue', 'Orders', 'Units', 'Conversion Rate', 'AOV'],
                    'datasets': [
                        {
                            'label': 'Current Period',
                            'data': current_values,
                            'backgroundColor': '#3b82f6'
                        },
                        {
                            'label': 'Previous Period',
                            'data': prev_values,
                            'backgroundColor': '#93c5fd'
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return value.toLocaleString(); }'
                            }
                        }
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting metrics chart data: {str(e)}")
            return self._get_empty_chart_data()
    
    def get_category_chart_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get category performance chart data."""
        try:
            trends_data = self.get_trends(start_date, end_date)
            category_data_str = trends_data.get('category_distribution', '{}')
            category_data = json.loads(category_data_str) if isinstance(category_data_str, str) else category_data_str
            
            # Convert values to float and sort categories by revenue 
            category_data = {k: float(v) if isinstance(v, (int, float, str)) else 0.0 for k, v in category_data.items()}
            sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
            categories = [cat[0] for cat in sorted_categories]
            values = [cat[1] for cat in sorted_categories]
            
            # Generate colors for each category
            colors = [
                '#3b82f6', '#ef4444', '#10b981', '#f59e0b', '#6366f1',
                '#ec4899', '#8b5cf6', '#14b8a6', '#f97316', '#06b6d4'
            ]
            
            return {
                'type': 'pie',
                'data': {
                    'labels': categories,
                    'datasets': [{
                        'data': values,
                        'backgroundColor': colors[:len(categories)],
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'tooltip': {
                            'callbacks': {
                                'label': 'function(context) { return context.label + ": $" + context.parsed.toLocaleString(); }'
                            }
                        },
                        'legend': {
                            'position': 'right',
                            'align': 'center'
                        }
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting category chart data: {str(e)}")
            return self._get_empty_chart_data()
    
    def get_alert_chart_data(self, start_date: datetime, end_date: datetime) -> Dict:
        """Get anomaly detection chart data."""
        try:
            reports = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            ).order_by(BusinessReport.date).all()
            
            dates = []
            conversion_rates = []
            
            current_date = start_date
            while current_date <= end_date:
                daily_reports = [r for r in reports if r.date.date() == current_date.date()]
                if daily_reports:
                    avg_conversion = sum(float(r.conversion_rate) for r in daily_reports) / len(daily_reports)
                else:
                    avg_conversion = 0
                
                dates.append(current_date.strftime('%Y-%m-%d'))
                conversion_rates.append(avg_conversion)
                current_date += timedelta(days=1)
            
            return {
                'type': 'line',
                'data': {
                    'labels': dates,
                    'datasets': [{
                        'label': 'Conversion Rate',
                        'data': conversion_rates,
                        'borderColor': '#3b82f6',
                        'backgroundColor': 'rgba(59, 130, 246, 0.1)',
                        'fill': True
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'ticks': {
                                'callback': 'function(value) { return value.toFixed(2) + "%"; }'
                            }
                        }
                    }
                }
            }
        except Exception as e:
            logger.error(f"Error getting alert chart data: {str(e)}")
            return self._get_empty_chart_data()
    
    def _get_empty_chart_data(self) -> Dict:
        """Get empty chart data structure."""
        return {
            'type': 'line',
            'data': {
                'labels': [],
                'datasets': [{
                    'label': 'No Data',
                    'data': []
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False
            }
        }
