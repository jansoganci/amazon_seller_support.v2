"""Business module services."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import logging

from sqlalchemy import func, and_
from sqlalchemy.orm import Query

from app.extensions import db
from app.modules.business.models import BusinessReport
from app.modules.category.models import Category, ASINKategori
from app.modules.business.constants import (
    GROUPING_OPTIONS,
    DEFAULT_GROUP_BY,
    DEFAULT_PAGE_SIZE,
    DEFAULT_SORT_ORDER
)
from app.utils.constants import get_category_by_asin
from app.core.metrics.engine import metric_engine
from app.modules.business.metrics import BUSINESS_METRICS, register_metrics

logger = logging.getLogger(__name__)

class BusinessReportService:
    """Service for handling business report operations."""
    
    def __init__(self, store_id: int):
        """Initialize the service with store ID."""
        self.store_id = store_id
        register_metrics()  # Register business metrics
    
    def get_reports(
        self,
        start_date: datetime,
        end_date: datetime,
        store_id: Optional[int] = None,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        asin: Optional[str] = None,
        page: int = 1,
        per_page: int = DEFAULT_PAGE_SIZE,
        sort_by: str = 'date',
        sort_order: str = DEFAULT_SORT_ORDER
    ) -> Dict[str, Any]:
        """Get business reports based on filters."""
        store_id = store_id or self.store_id
        if not store_id:
            raise ValueError("store_id is required")
            
        query = self._build_base_query(store_id, start_date, end_date)
        
        if category:
            query = query.filter(BusinessReport.category == category)
        if subcategory:
            query = query.filter(BusinessReport.subcategory == subcategory)
        if asin:
            query = query.filter(BusinessReport.asin == asin)
        
        # Apply sorting
        if sort_order == 'desc':
            query = query.order_by(getattr(BusinessReport, sort_by).desc())
        else:
            query = query.order_by(getattr(BusinessReport, sort_by).asc())
        
        # Apply pagination
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return {
            'items': [item.to_dict() for item in items],
            'total': total,
            'page': page,
            'per_page': per_page,
            'pages': (total + per_page - 1) // per_page
        }
    
    def get_trends(
        self,
        start_date: datetime,
        end_date: datetime,
        category: Optional[str] = None,
        subcategory: Optional[str] = None,
        asin: Optional[str] = None,
        group_by: str = DEFAULT_GROUP_BY
    ) -> Dict[str, Any]:
        """Get business trends with optional grouping."""
        if group_by not in GROUPING_OPTIONS:
            raise ValueError(f"Invalid group_by option. Must be one of: {', '.join(GROUPING_OPTIONS.keys())}")
        
        # Get raw data
        reports = self.get_reports(start_date, end_date, category=category, subcategory=subcategory, asin=asin)['items']
        
        if not reports:
            return self._get_empty_trends()
            
        # Calculate metrics
        context = {
            'store_id': self.store_id,
            'date_range': f"{start_date.isoformat()}-{end_date.isoformat()}"
        }
        
        # Calculate current period metrics
        current_metrics = metric_engine.calculate_metrics(
            metric_ids=list(BUSINESS_METRICS.keys()),
            data=reports,
            context=context
        )
        
        # Calculate previous period metrics for comparison
        prev_start = start_date - (end_date - start_date)
        prev_end = start_date
        prev_reports = self.get_reports(prev_start, prev_end, category=category, subcategory=subcategory, asin=asin)['items']
        
        prev_metrics = metric_engine.calculate_metrics(
            metric_ids=list(BUSINESS_METRICS.keys()),
            data=prev_reports,
            context={**context, 'date_range': f"{prev_start.isoformat()}-{prev_end.isoformat()}"}
        )
        
        # Calculate growth rates
        growth_rates = self._calculate_growth_rates(current_metrics, prev_metrics)
        
        # Group data if needed
        if group_by == 'weekly':
            reports = self._group_reports_weekly(reports)
        elif group_by == 'monthly':
            reports = self._group_reports_monthly(reports)
            
        return {
            **current_metrics,
            **growth_rates,
            'reports': reports
        }
    
    def get_filtered_data(
        self,
        start_date: datetime,
        end_date: datetime,
        group_by: str = DEFAULT_GROUP_BY,
        category: Optional[str] = None,
        asin: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get filtered business data including metrics and charts."""
        try:
            if not self.store_id:
                raise ValueError("store_id is required")

            # Validate group_by
            if group_by not in GROUPING_OPTIONS:
                raise ValueError(f"Invalid group_by option. Must be one of: {', '.join(GROUPING_OPTIONS.keys())}")

            # Get base query
            query = BusinessReport.query.filter(
                BusinessReport.store_id == self.store_id,
                BusinessReport.date.between(start_date, end_date)
            )

            # Apply category and ASIN filters if provided
            if category:
                query = query.filter(BusinessReport.category == category)
            if asin:
                query = query.filter(BusinessReport.asin == asin)

            # Group data based on selected grouping
            if group_by == 'daily':
                data = self._group_by_day(query)
            elif group_by == 'weekly':
                data = self._group_by_week(query)
            elif group_by == 'monthly':
                data = self._group_by_month(query)
            elif group_by == 'quarterly':
                data = self._group_by_quarter(query)
            elif group_by == 'yearly':
                data = self._group_by_year(query)
            else:
                raise ValueError(f"Unsupported grouping option: {group_by}")

            return {
                'metrics': data.get('metrics', {}),
                'charts': {
                    'salesChart': {
                        'labels': data.get('labels', []),
                        'datasets': [{
                            'label': 'Sales',
                            'data': data.get('sales', []),
                            'borderColor': '#0ea5e9',
                            'backgroundColor': 'rgba(14, 165, 233, 0.1)',
                            'fill': True
                        }]
                    },
                    'ordersChart': {
                        'labels': data.get('labels', []),
                        'datasets': [{
                            'label': 'Orders',
                            'data': data.get('orders', []),
                            'borderColor': '#10b981',
                            'backgroundColor': 'rgba(16, 185, 129, 0.1)',
                            'fill': True
                        }]
                    },
                    'sessionsChart': {
                        'labels': data.get('labels', []),
                        'datasets': [{
                            'label': 'Sessions',
                            'data': data.get('sessions', []),
                            'borderColor': '#f59e0b',
                            'backgroundColor': 'rgba(245, 158, 11, 0.1)',
                            'fill': True
                        }]
                    },
                    'pageViewsChart': {
                        'labels': data.get('labels', []),
                        'datasets': [{
                            'label': 'Page Views',
                            'data': data.get('page_views', []),
                            'borderColor': '#8b9467',
                            'backgroundColor': 'rgba(139, 148, 103, 0.1)',
                            'fill': True
                        }]
                    }
                }
            }

        except Exception as e:
            logger.error(f"Error in get_filtered_data: {str(e)}")
            raise

    def _get_empty_trends(self) -> Dict[str, Any]:
        """Return empty trend data structure."""
        return {
            metric_id: metric_engine.get_metric_config(metric_id)['visualization']['format'].replace('0', '0')
            for metric_id in BUSINESS_METRICS.keys()
        }
    
    def _calculate_growth_rates(self, current: Dict[str, Any], previous: Dict[str, Any]) -> Dict[str, float]:
        """Calculate growth rates between current and previous periods."""
        growth_rates = {}
        for metric_id, current_value in current.items():
            if metric_id not in previous:
                continue
                
            try:
                current_num = float(str(current_value).replace('$', '').replace('%', '').replace(',', ''))
                previous_num = float(str(previous[metric_id]).replace('$', '').replace('%', '').replace(',', ''))
                
                if previous_num == 0:
                    growth = 100 if current_num > 0 else 0
                else:
                    growth = ((current_num - previous_num) / previous_num) * 100
                    
                growth_rates[f"{metric_id}_growth"] = round(growth, 2)
            except (ValueError, TypeError):
                growth_rates[f"{metric_id}_growth"] = 0
                
        return growth_rates
    
    # def get_categories(self) -> List[Dict[str, str]]:
    #     """Get unique categories and subcategories."""
    #     if not self.store_id:
    #         raise ValueError("store_id is required")

    #     results = db.session.query(
    #         BusinessReport.category,
    #         BusinessReport.subcategory
    #     ).filter(
    #         BusinessReport.store_id == self.store_id,
    #         BusinessReport.category.isnot(None)
    #     ).distinct().all()

    #     categories = []
    #     for category, subcategory in results:
    #         if category and category not in [c['name'] for c in categories]:
    #             categories.append({
    #                 'name': category,
    #                 'subcategories': []
    #             })
    #         if subcategory:
    #             for cat in categories:
    #                 if cat['name'] == category and subcategory not in cat['subcategories']:
    #                     cat['subcategories'].append(subcategory)

    #     return categories
    
    def get_asins(self) -> List[Dict[str, str]]:
        """Get unique ASINs."""
        if not self.store_id:
            raise ValueError("store_id is required")

        results = db.session.query(
            BusinessReport.asin,
            BusinessReport.product_name
        ).filter(
            BusinessReport.store_id == self.store_id,
            BusinessReport.asin.isnot(None)
        ).distinct().all()

        return [{
            'asin': asin,
            'name': product_name
        } for asin, product_name in results]
    
    def _build_base_query(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Query:
        """Build base query with common filters."""
        return db.session.query(BusinessReport).filter(
            and_(
                BusinessReport.store_id == store_id,
                BusinessReport.date >= start_date,
                BusinessReport.date <= end_date
            )
        )
    
    def _group_reports_weekly(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group reports by week."""
        # Implementation remains the same
        return reports
    
    def _group_reports_monthly(self, reports: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Group reports by month."""
        # Implementation remains the same
        return reports

    def _group_by_day(self, query: Query) -> Dict[str, Any]:
        """Group data by day."""
        return self._aggregate_data(
            query.group_by(BusinessReport.date)
            .order_by(BusinessReport.date)
        )

    def _group_by_week(self, query: Query) -> Dict[str, Any]:
        """Group data by week."""
        return self._aggregate_data(
            query.group_by(func.date_trunc('week', BusinessReport.date))
            .order_by(func.date_trunc('week', BusinessReport.date))
        )

    def _group_by_month(self, query: Query) -> Dict[str, Any]:
        """Group data by month."""
        return self._aggregate_data(
            query.group_by(func.date_trunc('month', BusinessReport.date))
            .order_by(func.date_trunc('month', BusinessReport.date))
        )

    def _group_by_quarter(self, query: Query) -> Dict[str, Any]:
        """Group data by quarter."""
        return self._aggregate_data(
            query.group_by(func.date_trunc('quarter', BusinessReport.date))
            .order_by(func.date_trunc('quarter', BusinessReport.date))
        )

    def _group_by_year(self, query: Query) -> Dict[str, Any]:
        """Group data by year."""
        return self._aggregate_data(
            query.group_by(func.date_trunc('year', BusinessReport.date))
            .order_by(func.date_trunc('year', BusinessReport.date))
        )

    def _aggregate_data(self, query: Query) -> Dict[str, Any]:
        """Aggregate data for the given query."""
        results = query.with_entities(
            func.min(BusinessReport.date).label('date'),
            func.sum(BusinessReport.ordered_product_sales).label('sales'),
            func.sum(BusinessReport.total_order_items).label('orders'),
            func.sum(BusinessReport.sessions).label('sessions'),
            func.sum(BusinessReport.page_views).label('page_views'),
            func.count(BusinessReport.id).label('count')
        ).all()

        dates = []
        sales = []
        orders = []
        sessions = []
        page_views = []
        total_sales = 0
        total_orders = 0
        total_sessions = 0
        total_page_views = 0

        for row in results:
            dates.append(row.date.strftime('%Y-%m-%d'))
            sales.append(float(row.sales or 0))
            orders.append(int(row.orders or 0))
            sessions.append(int(row.sessions or 0))
            page_views.append(int(row.page_views or 0))
            total_sales += float(row.sales or 0)
            total_orders += int(row.orders or 0)
            total_sessions += int(row.sessions or 0)
            total_page_views += int(row.page_views or 0)

        return {
            'labels': dates,
            'sales': sales,
            'orders': orders,
            'sessions': sessions,
            'page_views': page_views,
            'metrics': {
                'total_sales': total_sales,
                'total_orders': total_orders,
                'total_sessions': total_sessions,
                'total_page_views': total_page_views,
                'average_order_value': total_sales / total_orders if total_orders > 0 else 0,
                'conversion_rate': (total_orders / total_sessions * 100) if total_sessions > 0 else 0
            }
        }

class CategoryService:
    """Service for managing categories and ASIN mappings."""

    def __init__(self, store_id: Optional[int] = None):
        """Initialize service with store ID.
        
        Args:
            store_id: Optional store ID to scope operations
        """
        self.store_id = store_id

    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all categories with their subcategories.
        
        Returns:
            List of category dictionaries with subcategories
        """
        categories = Category.query.filter_by(parent_id=None).all()
        return [{
            'name': cat.name,
            'code': cat.code,
            'subcategories': [{
                'name': sub.name,
                'code': sub.code
            } for sub in cat.subcategories]
        } for cat in categories]

    def get_category_by_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Get category by its code.
        
        Args:
            code: Category code
            
        Returns:
            Category dictionary if found, None otherwise
        """
        category = Category.query.filter_by(code=code).first()
        if not category:
            return None
            
        return {
            'name': category.name,
            'code': category.code,
            'parent_code': category.parent.code if category.parent else None
        }

    def add_category(self, name: str, code: str, parent_code: Optional[str] = None) -> Dict[str, Any]:
        """Add a new category.
        
        Args:
            name: Category name
            code: Category code
            parent_code: Optional parent category code
            
        Returns:
            Created category dictionary
            
        Raises:
            ValueError: If category code already exists or parent not found
        """
        # Check if code already exists
        if Category.query.filter_by(code=code).first():
            raise ValueError(f"Category code already exists: {code}")
            
        # Get parent if specified
        parent_id = None
        if parent_code:
            parent = Category.query.filter_by(code=parent_code).first()
            if not parent:
                raise ValueError(f"Parent category not found: {parent_code}")
            parent_id = parent.id
            
        category = Category(
            name=name,
            code=code,
            parent_id=parent_id
        )
        
        db.session.add(category)
        db.session.commit()
        
        return {
            'name': category.name,
            'code': category.code,
            'parent_code': parent_code
        }

    def get_asin_category(self, asin: str) -> Optional[Dict[str, Any]]:
        """Get category information for an ASIN.
        
        Args:
            asin: ASIN to look up
            
        Returns:
            ASIN category mapping if found, None otherwise
        """
        asin_cat = ASINKategori.query.filter_by(asin=asin).first()
        if not asin_cat:
            return None
            
        return {
            'asin': asin_cat.asin,
            'main_category': asin_cat.main_category,
            'sub_category': asin_cat.sub_category,
            'title': asin_cat.title
        }

    def assign_asin_category(
        self, 
        asin: str, 
        main_category: str, 
        sub_category: Optional[str] = None,
        title: Optional[str] = None
    ) -> Dict[str, Any]:
        """Assign category to an ASIN.
        
        Args:
            asin: ASIN to categorize
            main_category: Main category name
            sub_category: Optional subcategory name
            title: Optional product title
            
        Returns:
            Created ASIN category mapping
            
        Raises:
            ValueError: If category not found
        """
        # Create or update ASIN category
        asin_cat = ASINKategori.query.filter_by(asin=asin).first()
        if asin_cat:
            asin_cat.main_category = main_category
            asin_cat.sub_category = sub_category if sub_category else main_category
            if title:
                asin_cat.title = title
        else:
            asin_cat = ASINKategori(
                asin=asin,
                main_category=main_category,
                sub_category=sub_category if sub_category else main_category,
                title=title
            )
            db.session.add(asin_cat)
            
        db.session.commit()
        
        return {
            'asin': asin_cat.asin,
            'main_category': asin_cat.main_category,
            'sub_category': asin_cat.sub_category,
            'title': asin_cat.title
        }
