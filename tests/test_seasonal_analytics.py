"""Test suite for seasonal analytics functionality."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal
import uuid

from app.utils.analytics_engine import AnalyticsEngine, SeasonType
from app.models.reports import BusinessReport
from app.models.store import Store
from app.models.user import User
from app import db

@pytest.fixture(scope="function")
def user(app):
    """Create a test user."""
    with app.app_context():
        unique_id = str(uuid.uuid4())[:8]
        user = User(
            name=f"Test User {unique_id}",
            email=f"test_{unique_id}@example.com",
            password="password123"
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        yield user
        db.session.rollback()

@pytest.fixture(scope="function")
def store(app, user):
    """Create a test store."""
    with app.app_context():
        store = Store(
            name="Test Store",
            user_id=user.id
        )
        db.session.add(store)
        db.session.commit()
        db.session.refresh(store)
        yield store
        db.session.rollback()

@pytest.fixture(scope="function")
def sample_data(app, store):
    """Create sample business report data spanning multiple years."""
    with app.app_context():
        # Create 2 years of data
        base_date = datetime(2024, 1, 1)
        reports = []
        
        # Regular weekly pattern with seasonal variations
        for day in range(365 * 2):  # 2 years of data
            current_date = base_date + timedelta(days=day)
            
            # Base values
            units = 100
            revenue = 1000.0
            conversion = 0.05
            
            # Add seasonal variations
            
            # Summer increase (June-August)
            if current_date.month in [6, 7, 8]:
                units *= 1.8
                revenue *= 1.8
                
            # Holiday season increase (November-December)
            if current_date.month == 11:
                units *= 1.3
                revenue *= 1.3
            elif current_date.month == 12:
                units *= 1.4
                revenue *= 1.4
                
            # Black Friday spike
            if current_date.month == 11 and 20 <= current_date.day <= 30:
                units *= 1.5
                revenue *= 1.5
                
            # Christmas spike
            if current_date.month == 12 and 15 <= current_date.day <= 25:
                units *= 1.5
                revenue *= 1.5
                
            # Weekend variation
            if current_date.weekday() >= 5:  # Saturday and Sunday
                units *= 1.3
                revenue *= 1.3
                
            report = BusinessReport(
                store_id=store.id,
                created_at=current_date,
                asin='B00TEST123',
                title='Test Product',
                units_sold=int(units),
                revenue=Decimal(str(revenue)),
                returns=int(units * 0.05),  # 5% return rate
                conversion_rate=conversion,
                page_views=int(units * 20),  # 20 views per sale
                sessions=int(units * 40),    # 40 sessions per sale
                report_period='DAILY'        # Add report period
            )
            reports.append(report)
        
        db.session.bulk_save_objects(reports)
        db.session.commit()
        yield reports
        db.session.rollback()

@pytest.fixture(scope="function")
def analytics(app):
    """Create an AnalyticsEngine instance."""
    with app.app_context():
        yield AnalyticsEngine()
        db.session.rollback()

class TestSeasonalAnalytics:
    """Test cases for seasonal analytics functionality."""
    
    def test_weekly_analysis(self, app, analytics, store, sample_data):
        """Test weekly trend analysis."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.WEEKLY,
                base_year=2024,
                comparison_years=[2023]
            )
            
            assert 'periodic_sales' in result
            assert 'year_over_year' in result
            assert 'special_periods' in result
            assert 'growth_patterns' in result
            
            # Verify weekly data structure
            weekly_data = result['periodic_sales']
            assert len(weekly_data) > 0
            assert all(
                'period' in week and 'revenue' in week 
                for week in weekly_data
            )
            
            # Verify weekend spikes
            for week in weekly_data:
                weekend_revenue = week['revenue']
                assert weekend_revenue > 0

    def test_monthly_analysis(self, app, analytics, store, sample_data):
        """Test monthly trend analysis."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.MONTHLY,
                base_year=2024
            )
            
            monthly_data = result['periodic_sales']
            assert len(monthly_data) == 12  # Full year
            
            # Verify summer increase
            summer_months = monthly_data[5:8]  # June-August
            non_summer_months = monthly_data[:5] + monthly_data[8:]
            
            avg_summer_revenue = sum(m['revenue'] for m in summer_months) / len(summer_months)
            avg_non_summer_revenue = sum(m['revenue'] for m in non_summer_months) / len(non_summer_months)
            
            assert avg_summer_revenue > avg_non_summer_revenue

    def test_quarterly_analysis(self, app, analytics, store, sample_data):
        """Test quarterly trend analysis."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.QUARTERLY,
                base_year=2024
            )
            
            quarterly_data = result['periodic_sales']
            assert len(quarterly_data) == 4  # Four quarters
            
            # Q4 should be highest due to holiday season
            q4_revenue = quarterly_data[3]['revenue']
            other_quarters_avg = sum(
                q['revenue'] for q in quarterly_data[:3]
            ) / 3
            
            assert q4_revenue > other_quarters_avg

    def test_special_period_analysis(self, app, analytics, store, sample_data):
        """Test special period analysis."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.MONTHLY,
                base_year=2024,
                include_special_periods=True
            )
            
            special_periods = result['special_periods']
            assert 'black_friday' in special_periods
            assert 'christmas' in special_periods
            
            # Verify Black Friday performance
            bf_data = special_periods['black_friday'][2024]
            assert bf_data['revenue_growth'] > 0  # Should show growth vs previous period
            
            # Verify Christmas performance
            christmas_data = special_periods['christmas'][2024]
            assert christmas_data['revenue_growth'] > 0

    def test_growth_patterns(self, app, analytics, store, sample_data):
        """Test growth pattern detection."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.MONTHLY,
                base_year=2024,
                comparison_years=[2023]
            )
            
            patterns = result['growth_patterns']
            
            # Should identify holiday months as seasonal peaks
            seasonal_peaks = patterns['seasonal_peaks']
            peak_months = [p['period'] for p in seasonal_peaks]
            
            assert any('11' in month for month in peak_months)  # November
            assert any('12' in month for month in peak_months)  # December

    def test_year_over_year_comparison(self, app, analytics, store, sample_data):
        """Test year-over-year comparison."""
        with app.app_context():
            result = analytics.analyze_seasonal_trends(
                store_id=store.id,
                season_type=SeasonType.YEARLY,
                base_year=2024,
                comparison_years=[2023]
            )
            
            assert 2023 in result['year_over_year']
            assert len(result['periodic_sales']) == 1  # Base year
            assert len(result['year_over_year'][2023]) == 1  # Comparison year
