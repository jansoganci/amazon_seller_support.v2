"""Analytics Engine for processing and analyzing seller data.

This module provides the core analytics functionality for the Amazon Seller Support application.
It processes various types of reports (business, inventory, etc.) and generates insights.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from decimal import Decimal
from enum import Enum
import calendar

from sqlalchemy import func, extract
from app.models.reports import BusinessReport, InventoryReport
from app.models.store import Store
from app.utils.data_validator import DataValidator
from app import db

class SeasonType(Enum):
    """Types of seasonal periods for analysis."""
    WEEKLY = 'weekly'
    MONTHLY = 'monthly'
    QUARTERLY = 'quarterly'
    YEARLY = 'yearly'
    CUSTOM = 'custom'

class AnalyticsEngine:
    """Core analytics engine for processing seller data and generating insights."""

    # Special periods (US holidays and shopping events)
    SPECIAL_PERIODS = {
        'black_friday': {
            'name': 'Black Friday',
            'month': 11,
            'day_start': 20,  # Week before Black Friday
            'day_end': 30     # Cyber Monday period
        },
        'christmas': {
            'name': 'Christmas',
            'month': 12,
            'day_start': 1,
            'day_end': 25
        },
        'prime_day': {
            'name': 'Prime Day',
            'month': 7,
            'day_start': 11,  # Typical Prime Day period
            'day_end': 12
        },
        'valentines': {
            'name': "Valentine's Day",
            'month': 2,
            'day_start': 1,
            'day_end': 14
        }
    }

    def __init__(self):
        """Initialize the analytics engine."""
        self.cache = {}  # Simple in-memory cache
        self.validator = DataValidator()

    def validate_analysis_request(
        self,
        store_id: int,
        date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[str]:
        """Validate analysis request parameters.
        
        Args:
            store_id: Store ID to analyze
            date_range: Optional date range for analysis
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Validate store exists
        store = Store.query.get(store_id)
        if not store:
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
        """Analyze sales trends for a specific store over a date range.

        Args:
            store_id (int): The ID of the store to analyze
            date_range (tuple): Start and end dates (start_date, end_date)

        Returns:
            dict: Sales trend analysis including:
                - daily_sales: List of daily sales totals
                - total_revenue: Total revenue for period
                - average_daily_sales: Average daily sales
                - growth_rate: Growth rate compared to previous period
                - conversion_rate: Average conversion rate
                
        Raises:
            ValueError: If validation fails
        """
        # Validate request
        errors = self.validate_analysis_request(store_id, date_range)
        if errors:
            raise ValueError(f"Invalid analysis request: {'; '.join(errors)}")
            
        start_date, end_date = date_range
        
        # Get sales data for the period
        sales_data = (
            db.session.query(
                BusinessReport.created_at.date().label('date'),
                func.sum(BusinessReport.units_sold).label('total_units'),
                func.sum(BusinessReport.revenue).label('total_revenue'),
                func.avg(BusinessReport.conversion_rate).label('avg_conversion')
            )
            .filter(
                BusinessReport.store_id == store_id,
                BusinessReport.created_at.between(start_date, end_date)
            )
            .group_by(BusinessReport.created_at.date())
            .order_by(BusinessReport.created_at.date())
            .all()
        )

        # Calculate previous period metrics for comparison
        period_length = (end_date - start_date).days
        previous_start = start_date - timedelta(days=period_length)
        previous_end = start_date - timedelta(days=1)

        previous_data = (
            db.session.query(
                func.sum(BusinessReport.units_sold).label('total_units'),
                func.sum(BusinessReport.revenue).label('total_revenue')
            )
            .filter(
                BusinessReport.store_id == store_id,
                BusinessReport.created_at.between(previous_start, previous_end)
            )
            .first()
        )

        # Process current period data
        daily_sales = [
            {
                'date': row.date.strftime('%Y-%m-%d'),
                'units': row.total_units,
                'revenue': float(row.total_revenue),
                'conversion_rate': float(row.avg_conversion)
            }
            for row in sales_data
        ]

        # Calculate total metrics
        total_revenue = sum(day['revenue'] for day in daily_sales) if daily_sales else 0
        total_units = sum(day['units'] for day in daily_sales) if daily_sales else 0
        avg_daily_sales = total_revenue / len(daily_sales) if daily_sales else 0
        avg_conversion = (
            sum(day['conversion_rate'] for day in daily_sales) / len(daily_sales)
            if daily_sales else 0
        )

        # Calculate growth rate
        previous_revenue = float(previous_data.total_revenue) if previous_data and previous_data.total_revenue else 0
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
        """Analyze inventory status for a specific store.

        Args:
            store_id (int): The ID of the store to analyze
            reorder_threshold (float): Threshold for reorder recommendations

        Returns:
            dict: Inventory analysis including:
                - total_inventory: Total units across all products
                - low_stock_items: List of items below reorder threshold
                - out_of_stock_items: List of items with zero inventory
                - inventory_value: Total value of current inventory
                - reorder_recommendations: List of items that need reordering
                
        Raises:
            ValueError: If validation fails
        """
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

        # Get current inventory data
        inventory_data = (
            db.session.query(InventoryReport)
            .filter(InventoryReport.store_id == store_id)
            .order_by(InventoryReport.created_at.desc())
            .all()
        )

        # Process inventory data
        items_status = []
        low_stock_items = []
        out_of_stock_items = []
        reorder_recommendations = []
        total_inventory = 0
        inventory_value = Decimal('0.0')

        for item in inventory_data:
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
                'total_items': len(inventory_data),
                'low_stock_count': len(low_stock_items),
                'out_of_stock_count': len(out_of_stock_items),
                'reorder_needed_count': len(reorder_recommendations)
            }
        }

    def analyze_seasonal_trends(
        self,
        store_id: int,
        season_type: SeasonType,
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
        if season_type == SeasonType.WEEKLY:
            periodic_data = self._analyze_weekly_trends(
                store_id, base_year_start, base_year_end
            )
        elif season_type == SeasonType.MONTHLY:
            periodic_data = self._analyze_monthly_trends(
                store_id, base_year_start, base_year_end
            )
        elif season_type == SeasonType.QUARTERLY:
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
            if season_type == SeasonType.WEEKLY:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                comparison_data[year] = self._analyze_weekly_trends(
                    store_id, year_start, year_end
                )
            elif season_type == SeasonType.MONTHLY:
                year_start = datetime(year, 1, 1)
                year_end = datetime(year, 12, 31)
                comparison_data[year] = self._analyze_monthly_trends(
                    store_id, year_start, year_end
                )
            elif season_type == SeasonType.QUARTERLY:
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
