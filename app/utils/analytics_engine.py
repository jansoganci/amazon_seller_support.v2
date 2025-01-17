"""Analytics Engine for processing and analyzing seller data.

This module provides the core analytics functionality for the Amazon Seller Support application.
It processes various types of reports (business, inventory, etc.) and generates insights.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from decimal import Decimal
from enum import Enum
import calendar
import pandas as pd

from sqlalchemy import func, extract, and_, text
from app.models.reports import BusinessReport, InventoryReport
from app.models.store import Store
from app.utils.data_validator import DataValidator
from app import db

class TimeGrouping(Enum):
    """Zaman bazlı gruplandırma seçenekleri."""
    DAILY = 'daily'
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'

class AnalyticsEngine:
    """Core analytics engine for processing seller data and generating insights."""

    def __init__(self):
        """Initialize the analytics engine."""
        self.cache = {}  # Simple in-memory cache
        self.validator = DataValidator()

    def get_revenue_trends(
        self,
        store_id: int,
        start_date: str,
        end_date: str,
        group_by: str,
        category: str = None,
        asin: str = None
    ) -> dict:
        """Get revenue trends for the specified period."""
        try:
            print(f"store_id: {store_id}, start_date: {start_date}, end_date: {end_date}, group_by: {group_by}, category: {category}, asin: {asin}")
            # Convert group_by string to TimeGrouping enum
            try:
                group_by = TimeGrouping(group_by)
            except ValueError:
                group_by = TimeGrouping.DAILY  # Default to daily if invalid

            # Format dates for SQLite query
            start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d 00:00:00')
            end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d 23:59:59')
            
            # Get SQLite connection directly
            import sqlite3
            conn = sqlite3.connect('instance/app.db')
            
            # If category is selected, first get ASINs for that category
            if category:
                from app.utils.constants import get_category_by_asin
                category_asins_query = """
                    SELECT DISTINCT asin 
                    FROM business_report 
                    WHERE store_id = ?
                """
                df_asins = pd.read_sql(category_asins_query, conn, params=(store_id,))
                category_asins = [
                    asin for asin in df_asins['asin'] 
                    if get_category_by_asin(asin)[0] == category
                ]
                if not category_asins:
                    return {
                        'labels': [],
                        'values': [],
                        'units': [],
                        'sessions': [],
                        'conversion_rates': [],
                        'total_revenue': 0,
                        'total_units': 0,
                        'total_sessions': 0,
                        'average_order_value': 0,
                        'growth_rate': 0,
                        'previous_period': 0
                    }
                
                # Base query for revenue trends with category filter
                query = """
                    SELECT 
                        DATE(created_at) as date,
                        SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                        SUM(units_ordered) as units,
                        SUM(sessions) as sessions,
                        CAST(SUM(units_ordered) AS FLOAT) / NULLIF(SUM(sessions), 0) * 100 as conversion_rate
                    FROM business_report 
                    WHERE store_id = ?
                    AND created_at >= ?
                    AND created_at <= ?
                    AND asin IN ({})
                    GROUP BY DATE(created_at)
                    ORDER BY created_at
                """.format(','.join(['?'] * len(category_asins)))
                
                params = [store_id, start_date, end_date] + category_asins
                
            else:
                # Base query for revenue trends without category filter
                query = """
                    SELECT 
                        DATE(created_at) as date,
                        SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                        SUM(units_ordered) as units,
                        SUM(sessions) as sessions,
                        CAST(SUM(units_ordered) AS FLOAT) / NULLIF(SUM(sessions), 0) * 100 as conversion_rate
                    FROM business_report 
                    WHERE store_id = ?
                    AND created_at >= ?
                    AND created_at <= ?
                    AND (? IS NULL OR asin = ?)
                    GROUP BY DATE(created_at)
                    ORDER BY created_at
                """
                params = (store_id, start_date, end_date, asin, asin)
            
            # Execute query and convert to DataFrame
            df = pd.read_sql(query, conn, params=params)
            
            if df.empty:
                return {
                    'labels': [],
                    'values': [],
                    'units': [],
                    'sessions': [],
                    'conversion_rates': [],
                    'total_revenue': 0,
                    'total_units': 0,
                    'total_sessions': 0,
                    'average_order_value': 0,
                    'growth_rate': 0,
                    'previous_period': 0
                }
            
            # Convert date to datetime for grouping
            df['date'] = pd.to_datetime(df['date'])
            
            # Group by the specified time period
            if group_by == TimeGrouping.DAILY:
                df['date_group'] = df['date'].dt.strftime('%Y-%m-%d')
            elif group_by == TimeGrouping.WEEKLY:
                df['date_group'] = df['date'].dt.to_period('W').dt.strftime('%Y-W%V')
            elif group_by == TimeGrouping.MONTHLY:
                df['date_group'] = df['date'].dt.strftime('%Y-%m')
            elif group_by == TimeGrouping.QUARTERLY:
                df['date_group'] = df['date'].dt.strftime('%Y-Q%q')
            else:  # YEARLY
                df['date_group'] = df['date'].dt.strftime('%Y')
            
            # Group metrics by date_group
            grouped = df.groupby('date_group').agg({
                'revenue': 'sum',
                'units': 'sum',
                'sessions': 'sum'
            }).reset_index()
            
            # Calculate conversion rate after grouping
            grouped['conversion_rate'] = (grouped['units'] / grouped['sessions'] * 100).fillna(0)
            
            # Calculate total metrics
            total_revenue = float(grouped['revenue'].sum())
            total_units = int(grouped['units'].sum())
            total_sessions = int(grouped['sessions'].sum())
            average_order_value = total_revenue / total_units if total_units > 0 else 0
            
            # Get previous period revenue for growth rate
            previous_revenue = self._get_previous_period_revenue(
                store_id, start_date, end_date, category, asin
            )
            growth_rate = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            # Close connection
            conn.close()
            
            return {
                'labels': grouped['date_group'].tolist(),
                'values': grouped['revenue'].tolist(),
                'units': grouped['units'].tolist(),
                'sessions': grouped['sessions'].tolist(),
                'conversion_rates': grouped['conversion_rate'].tolist(),
                'total_revenue': total_revenue,
                'total_units': total_units,
                'total_sessions': total_sessions,
                'average_order_value': average_order_value,
                'growth_rate': growth_rate,
                'previous_period': previous_revenue
            }
        except Exception as e:
            print(f"Error in get_revenue_trends: {str(e)}")
            return {
                'labels': [],
                'values': [],
                'units': [],
                'sessions': [],
                'conversion_rates': [],
                'total_revenue': 0,
                'total_units': 0,
                'total_sessions': 0,
                'average_order_value': 0,
                'growth_rate': 0,
                'previous_period': 0
            }

    def _get_previous_period_revenue(
        self,
        store_id: int,
        start_date: Union[str, datetime],
        end_date: Union[str, datetime],
        category: Optional[str] = None,
        asin: Optional[str] = None
    ) -> float:
        """Calculate revenue for the previous period."""
        try:
            # Convert dates to datetime objects if they are strings
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')

            # Calculate previous period dates
            period_length = (end_date - start_date).days
            prev_start = start_date - timedelta(days=period_length)
            prev_end = start_date - timedelta(days=1)

            # Format dates for SQLite query
            prev_start_str = prev_start.strftime('%Y-%m-%d')
            prev_end_str = prev_end.strftime('%Y-%m-%d')

            # Using raw SQL string instead of SQLAlchemy text
            sql = """
                SELECT ordered_product_sales, asin
                FROM business_report
                WHERE store_id = ?
                AND created_at >= ?
                AND created_at < ?
                AND (? IS NULL OR asin = ?)
            """
            
            # Get SQLite connection directly
            import sqlite3
            conn = sqlite3.connect('instance/app.db')
            
            df = pd.read_sql(
                sql,
                conn,
                params=(store_id, prev_start_str, prev_end_str, asin, asin)
            )
            
            if category:
                from app.utils.constants import get_category_by_asin
                df['category'] = df['asin'].apply(lambda x: get_category_by_asin(x)[0])
                df = df[df['category'] == category]

            result = df['ordered_product_sales'].sum()
            
            # Close connection
            conn.close()
            
            return float(result) if result else 0.0
        except Exception as e:
            print(f"Error in _get_previous_period_revenue: {str(e)}")
            return 0.0

    def validate_analysis_request(
        self,
        store_id: int,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[str]:
        """Validate analysis request parameters."""
        errors = []
        
        # Validate store exists using raw SQL
        sql = text("SELECT id FROM store WHERE id = :store_id")
        result = db.session.execute(sql, {'store_id': store_id}).first()
        
        if not result:
            errors.append(f"Store with ID {store_id} not found")
            
        # Validate date range if provided
        if date_range:
            is_valid, error = self.validator.validate_date_range(*date_range)
            if not is_valid:
                errors.append(error)
                
        return errors

    def analyze_sales_trends(
        self, 
        store_id: int, 
        date_range: Tuple[datetime, datetime]
    ) -> Dict:
        """Analyze sales trends for a specific store over a date range."""
        # Validate request
        errors = self.validate_analysis_request(store_id, date_range)
        if errors:
            raise ValueError(f"Invalid analysis request: {'; '.join(errors)}")
            
        start_date, end_date = date_range
        
        # Get sales data for the period using raw SQL
        sql = text("""
            SELECT 
                DATE(created_at) as date,
                SUM(units_sold) as total_units,
                SUM(revenue) as total_revenue,
                AVG(conversion_rate) as avg_conversion
            FROM business_report
            WHERE store_id = :store_id
            AND created_at BETWEEN :start_date AND :end_date
            GROUP BY DATE(created_at)
            ORDER BY DATE(created_at)
        """)
        
        result = db.session.execute(
            sql,
            {
                'store_id': store_id,
                'start_date': start_date,
                'end_date': end_date
            }
        )

        # Process current period data
        daily_sales = []
        total_revenue = 0
        total_units = 0
        total_conversion = 0
        days_count = 0

        for row in result:
            daily_data = {
                'date': row.date.strftime('%Y-%m-%d'),
                'units': row.total_units,
                'revenue': float(row.total_revenue),
                'conversion_rate': float(row.avg_conversion)
            }
            daily_sales.append(daily_data)
            total_revenue += daily_data['revenue']
            total_units += daily_data['units']
            total_conversion += daily_data['conversion_rate']
            days_count += 1

        # Calculate averages
        avg_daily_sales = total_revenue / days_count if days_count > 0 else 0
        avg_conversion = total_conversion / days_count if days_count > 0 else 0

        # Calculate previous period metrics
        period_length = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_length)
        previous_end = start_date - timedelta(days=1)

        prev_sql = text("""
            SELECT 
                SUM(units_sold) as total_units,
                SUM(revenue) as total_revenue
            FROM business_report
            WHERE store_id = :store_id
            AND created_at BETWEEN :start_date AND :end_date
        """)

        prev_result = db.session.execute(
            prev_sql,
            {
                'store_id': store_id,
                'start_date': previous_start,
                'end_date': previous_end
            }
        ).first()

        # Calculate growth rate
        previous_revenue = float(prev_result.total_revenue) if prev_result and prev_result.total_revenue else 0
        growth_rate = (
            ((total_revenue - previous_revenue) / previous_revenue * 100)
            if previous_revenue > 0 else 0
        )

        return {
            'daily_sales': daily_sales,
            'total_revenue': total_revenue,
            'total_units': total_units,
            'average_daily_sales': avg_daily_sales,
            'growth_rate': growth_rate,
            'conversion_rate': avg_conversion
        }

    def analyze_inventory_status(
        self, 
        store_id: int,
        reorder_threshold: float = 0.2  # 20% of total inventory
    ) -> Dict:
        """Analyze inventory status for a specific store."""
        # Validate request
        errors = self.validate_analysis_request(store_id)
        if errors:
            raise ValueError(f"Invalid analysis request: {'; '.join(errors)}")
            
        # Validate threshold
        is_valid, error = self.validator.validate_numeric_value(
            reorder_threshold, 0, 1, 'reorder_threshold'
        )
        if not is_valid:
            raise ValueError(error)

        # Get current inventory data using raw SQL
        sql = text("""
            SELECT 
                asin,
                title,
                units_available,
                units_inbound,
                units_reserved,
                reorder_required
            FROM inventory_report
            WHERE store_id = :store_id
            ORDER BY created_at DESC
        """)
        
        result = db.session.execute(sql, {'store_id': store_id})
        
        # Process inventory data
        items_status = []
        low_stock_items = []
        out_of_stock_items = []
        reorder_recommendations = []
        total_inventory = 0
        inventory_value = Decimal('0.0')

        for item in result:
            total_units = (
                item.units_available + 
                item.units_inbound + 
                item.units_reserved
            )
            
            available_ratio = (
                item.units_available / total_units 
                if total_units > 0 else 0
            )

            status = {
                'asin': item.asin,
                'title': item.title,
                'units_available': item.units_available,
                'units_inbound': item.units_inbound,
                'units_reserved': item.units_reserved,
                'total_units': total_units
            }

            items_status.append(status)
            total_inventory += total_units

            # Check for low stock and out of stock items
            if item.units_available == 0:
                out_of_stock_items.append(status)
            elif available_ratio < reorder_threshold:
                low_stock_items.append(status)

            # Generate reorder recommendations
            if item.reorder_required or available_ratio < reorder_threshold:
                reorder_recommendations.append({
                    **status,
                    'reason': 'Low stock' if available_ratio < reorder_threshold else 'Reorder flag set'
                })

        return {
            'total_inventory': total_inventory,
            'items_status': items_status,
            'low_stock_items': low_stock_items,
            'out_of_stock_items': out_of_stock_items,
            'reorder_recommendations': reorder_recommendations,
            'inventory_summary': {
                'total_items': len(items_status),
                'low_stock_count': len(low_stock_items),
                'out_of_stock_count': len(out_of_stock_items),
                'reorder_needed_count': len(reorder_recommendations)
            }
        }

    def analyze_seasonal_trends(
        self,
        store_id: int,
        season_type: TimeGrouping,
        base_year: int,
        comparison_years: Optional[List[int]] = None,
        include_special_periods: bool = True
    ) -> Dict:
        """Analyze seasonal trends and patterns."""
        # Initialize comparison years if not provided
        if comparison_years is None:
            comparison_years = [base_year - 1]

        # Get base year data
        base_year_start = datetime(base_year, 1, 1)
        base_year_end = datetime(base_year, 12, 31)

        # Analyze based on season type
        if season_type == TimeGrouping.WEEKLY:
            periodic_data = self._analyze_weekly_trends(
                store_id, base_year_start, base_year_end
            )
        elif season_type == TimeGrouping.MONTHLY:
            periodic_data = self._analyze_monthly_trends(
                store_id, base_year_start, base_year_end
            )
        elif season_type == TimeGrouping.QUARTERLY:
            periodic_data = self._analyze_quarterly_trends(
                store_id, base_year_start, base_year_end
            )
        else:  # YEARLY
            periodic_data = self._analyze_yearly_trends(
                store_id, base_year, []  # No nested comparisons
            )

        # Get comparison data for each year
        comparison_data = {}
        for year in comparison_years:
            if season_type == TimeGrouping.WEEKLY:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                comparison_data[year] = self._analyze_weekly_trends(
                    store_id, year_start, year_end
                )
            elif season_type == TimeGrouping.MONTHLY:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                comparison_data[year] = self._analyze_monthly_trends(
                    store_id, year_start, year_end
                )
            elif season_type == TimeGrouping.QUARTERLY:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                comparison_data[year] = self._analyze_quarterly_trends(
                    store_id, year_start, year_end
                )
            else:  # YEARLY
                comparison_data[year] = self._analyze_yearly_trends(
                    store_id, year, []  # No nested comparisons
                )

        # Analyze special periods if requested
        special_period_analysis = {}
        if include_special_periods:
            for period_key, period_info in self.SPECIAL_PERIODS.items():
                special_period_analysis[period_key] = self._analyze_special_period(
                    store_id,
                    base_year,
                    period_info,
                    comparison_years
                )

        # Calculate growth patterns
        growth_patterns = self._calculate_growth_patterns(
            periodic_data,
            comparison_data
        )

        return {
            'periodic_sales': periodic_data,
            'year_over_year': comparison_data,
            'special_periods': special_period_analysis if include_special_periods else None,
            'growth_patterns': growth_patterns
        }

    def _analyze_special_period(
        self,
        store_id: int,
        year: int,
        period_info: Dict,
        comparison_years: List[int]
    ) -> Dict:
        """Analyze sales during a special period (holiday/event)."""
        all_years = [year] + comparison_years
        results = {}

        for analysis_year in all_years:
            start_date = datetime(
                analysis_year,
                period_info['month'],
                period_info['day_start']
            )
            end_date = datetime(
                analysis_year,
                period_info['month'],
                period_info['day_end']
            )

            # Get period data
            period_data = (
                db.session.query(
                    func.sum(BusinessReport.units_sold).label('total_units'),
                    func.sum(BusinessReport.revenue).label('total_revenue'),
                    func.avg(BusinessReport.conversion_rate).label('avg_conversion')
                )
                .filter(
                    BusinessReport.store_id == store_id,
                    BusinessReport.created_at.between(start_date, end_date)
                )
                .first()
            )

            # Get comparison period (same period from previous year)
            comparison_year = analysis_year - 1
            comparison_start = datetime(
                comparison_year,
                period_info['month'],
                period_info['day_start']
            )
            comparison_end = datetime(
                comparison_year,
                period_info['month'],
                period_info['day_end']
            )

            comparison_data = (
                db.session.query(
                    func.sum(BusinessReport.units_sold).label('total_units'),
                    func.sum(BusinessReport.revenue).label('total_revenue')
                )
                .filter(
                    BusinessReport.store_id == store_id,
                    BusinessReport.created_at.between(comparison_start, comparison_end)
                )
                .first()
            )

            # Calculate growth rates
            period_revenue = float(period_data.total_revenue) if period_data.total_revenue else 0
            comparison_revenue = float(comparison_data.total_revenue) if comparison_data.total_revenue else 0
            
            revenue_growth = (
                ((period_revenue - comparison_revenue) / comparison_revenue * 100)
                if comparison_revenue > 0 else 100  # If no comparison data, assume 100% growth
            )

            results[analysis_year] = {
                'period_name': period_info['name'],
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'units_sold': period_data.total_units,
                'revenue': period_revenue,
                'conversion_rate': float(period_data.avg_conversion) if period_data.avg_conversion else 0,
                'revenue_growth': revenue_growth
            }

        return results

    def _calculate_growth_patterns(
        self,
        current_data: List[Dict],
        comparison_data: Dict[int, List[Dict]]
    ) -> Dict:
        """Calculate growth patterns from periodic data."""
        patterns = {
            'consistent_growth': [],
            'seasonal_peaks': [],
            'declining_periods': []
        }

        # First, calculate the overall average revenue
        all_revenues = [p['revenue'] for p in current_data]
        avg_revenue = sum(all_revenues) / len(all_revenues) if all_revenues else 0

        # Analyze each period
        for i, current_period in enumerate(current_data):
            period_comparisons = []
            
            # Get same period from comparison years
            for year, year_data in comparison_data.items():
                if i < len(year_data):
                    period_comparisons.append(year_data[i])

            if period_comparisons:
                # Calculate average growth
                current_revenue = current_period['revenue']
                comparison_revenues = [p['revenue'] for p in period_comparisons]
                avg_comparison = sum(comparison_revenues) / len(comparison_revenues)
                
                growth_rate = (
                    ((current_revenue - avg_comparison) / avg_comparison * 100)
                    if avg_comparison > 0 else 0
                )

                # Categorize the pattern
                if growth_rate > 10:  # More than 10% growth
                    patterns['consistent_growth'].append({
                        'period': current_period['period'],
                        'growth_rate': growth_rate
                    })
                elif growth_rate < -10:  # More than 10% decline
                    patterns['declining_periods'].append({
                        'period': current_period['period'],
                        'decline_rate': abs(growth_rate)
                    })

            # Check for seasonal peaks by comparing with previous and next month
            current_revenue = current_period['revenue']
            
            # Get previous month's revenue
            prev_revenue = (
                current_data[i - 1]['revenue']
                if i > 0 else current_revenue
            )
            
            # Get next month's revenue
            next_revenue = (
                current_data[i + 1]['revenue']
                if i < len(current_data) - 1 else current_revenue
            )
            
            # A month is a peak if it's higher than both neighbors
            is_local_peak = (
                current_revenue > prev_revenue * 1.1 and  # 10% higher than previous
                current_revenue > next_revenue * 1.1      # 10% higher than next
            )
            
            # Also check if it's significantly above the yearly average
            is_significant = current_revenue > avg_revenue * 1.1  # 10% higher than average
            
            if is_local_peak or is_significant:  # Changed to OR for holiday months
                patterns['seasonal_peaks'].append({
                    'period': current_period['period'],
                    'revenue': current_revenue
                })

        return patterns

    def _analyze_weekly_trends(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Analyze weekly sales trends."""
        weekly_data = (
            db.session.query(
                # Use strftime for SQLite-compatible week grouping
                func.strftime('%Y-%W', BusinessReport.created_at).label('week'),
                func.sum(BusinessReport.units_sold).label('total_units'),
                func.sum(BusinessReport.revenue).label('total_revenue'),
                func.avg(BusinessReport.conversion_rate).label('avg_conversion')
            )
            .filter(
                BusinessReport.store_id == store_id,
                BusinessReport.created_at.between(start_date, end_date)
            )
            .group_by('week')
            .order_by('week')
            .all()
        )

        return [
            {
                'period': row.week,  # Already formatted as YYYY-WW
                'units': row.total_units,
                'revenue': float(row.total_revenue),
                'conversion_rate': float(row.avg_conversion)
            }
            for row in weekly_data
        ]

    def _analyze_monthly_trends(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Analyze monthly sales trends."""
        monthly_data = (
            db.session.query(
                extract('year', BusinessReport.created_at).label('year'),
                extract('month', BusinessReport.created_at).label('month'),
                func.sum(BusinessReport.units_sold).label('total_units'),
                func.sum(BusinessReport.revenue).label('total_revenue'),
                func.avg(BusinessReport.conversion_rate).label('avg_conversion')
            )
            .filter(
                BusinessReport.store_id == store_id,
                BusinessReport.created_at.between(start_date, end_date)
            )
            .group_by('year', 'month')
            .order_by('year', 'month')
            .all()
        )

        return [
            {
                'period': f"{int(row.year)}-{int(row.month):02d}",
                'units': row.total_units,
                'revenue': float(row.total_revenue),
                'conversion_rate': float(row.avg_conversion)
            }
            for row in monthly_data
        ]

    def _analyze_quarterly_trends(
        self,
        store_id: int,
        start_date: datetime,
        end_date: datetime
    ) -> Dict:
        """Analyze quarterly sales trends."""
        quarterly_data = (
            db.session.query(
                extract('year', BusinessReport.created_at).label('year'),
                func.ceil(extract('month', BusinessReport.created_at) / 3).label('quarter'),
                func.sum(BusinessReport.units_sold).label('total_units'),
                func.sum(BusinessReport.revenue).label('total_revenue'),
                func.avg(BusinessReport.conversion_rate).label('avg_conversion')
            )
            .filter(
                BusinessReport.store_id == store_id,
                BusinessReport.created_at.between(start_date, end_date)
            )
            .group_by('year', 'quarter')
            .order_by('year', 'quarter')
            .all()
        )

        return [
            {
                'period': f"{int(row.year)}-Q{int(row.quarter)}",
                'units': row.total_units,
                'revenue': float(row.total_revenue),
                'conversion_rate': float(row.avg_conversion)
            }
            for row in quarterly_data
        ]

    def _analyze_yearly_trends(
        self,
        store_id: int,
        year: int,
        comparison_years: List[int]
    ) -> List[Dict]:
        """Analyze yearly sales trends."""
        try:
            yearly_data = (
                db.session.query(
                    func.coalesce(func.sum(BusinessReport.units_sold), 0).label('total_units'),
                    func.coalesce(func.sum(BusinessReport.revenue), 0).label('total_revenue'),
                    func.coalesce(func.avg(BusinessReport.conversion_rate), 0).label('avg_conversion')
                )
                .filter(
                    BusinessReport.store_id == store_id,
                    extract('year', BusinessReport.created_at) == year
                )
                .first()
            )

            return [{
                'period': str(year),
                'units': yearly_data.total_units,
                'revenue': float(yearly_data.total_revenue),
                'conversion_rate': float(yearly_data.avg_conversion)
            }]
        except Exception as e:
            print(f"Error in _analyze_yearly_trends for year {year}: {str(e)}")
            return []

    def get_available_categories(self, store_id: int) -> List[str]:
        """Get available categories for the store using ASIN mapping."""
        # Get all ASINs for the store using raw SQL
        sql = text("""
            SELECT DISTINCT asin 
            FROM business_report 
            WHERE store_id = :store_id
        """)
        
        result = db.session.execute(sql, {'store_id': store_id})
        
        # Get categories using get_category_by_asin
        from app.utils.constants import get_category_by_asin
        categories = set()  # Using set to avoid duplicates
        for row in result:
            main_category, _ = get_category_by_asin(row.asin)
            if main_category:
                categories.add(main_category)
        
        return sorted(list(categories))

    def get_available_asins(self, store_id: int) -> List[Dict[str, str]]:
        """Get available ASINs for the store."""
        sql = text("""
            SELECT DISTINCT asin, title
            FROM business_report 
            WHERE store_id = :store_id
            ORDER BY asin
        """)
        
        result = db.session.execute(sql, {'store_id': store_id})
        
        return [
            {'asin': row.asin, 'title': row.title}
            for row in result
        ]
