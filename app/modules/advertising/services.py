"""Advertising module services."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from sqlalchemy import func, and_
from app.modules.advertising.models import AdvertisingReport
import pandas as pd

from app.extensions import db
from .constants import ERROR_MESSAGES

def get_advertising_trends(
    store_id: int,
    start_date: str,
    end_date: str,
    group_by: str = 'daily',
    campaign_id: str = None
) -> dict:
    """Get advertising trends for the specified period."""
    try:
        # Convert dates to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

        # Build base query
        query = AdvertisingReport.query.filter(
            AdvertisingReport.store_id == store_id,
            AdvertisingReport.date.between(start_date, end_date)
        )

        # Apply campaign filter if provided
        if campaign_id:
            query = query.filter(AdvertisingReport.campaign_id == campaign_id)

        # Execute query
        reports = query.order_by(AdvertisingReport.date).all()

        if not reports:
            return _get_empty_trend_data()

        # Group data by date
        data = {}
        for report in reports:
            date_key = report.date.strftime('%Y-%m-%d')
            if date_key not in data:
                data[date_key] = {
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0,
                    'sales': 0,
                    'orders': 0,
                    'units': 0
                }
            data[date_key]['impressions'] += report.impressions
            data[date_key]['clicks'] += report.clicks
            data[date_key]['spend'] += float(report.spend)
            data[date_key]['sales'] += float(report.sales)
            data[date_key]['orders'] += report.orders
            data[date_key]['units'] += report.units

        # Calculate metrics
        labels = sorted(data.keys())
        impressions = [data[date]['impressions'] for date in labels]
        clicks = [data[date]['clicks'] for date in labels]
        spend = [data[date]['spend'] for date in labels]
        sales = [data[date]['sales'] for date in labels]
        orders = [data[date]['orders'] for date in labels]
        units = [data[date]['units'] for date in labels]
        
        # Calculate derived metrics
        ctr = [
            (clicks[i] / impressions[i] * 100) if impressions[i] > 0 else 0 
            for i in range(len(labels))
        ]
        acos = [
            (spend[i] / sales[i] * 100) if sales[i] > 0 else 0 
            for i in range(len(labels))
        ]
        roas = [
            (sales[i] / spend[i]) if spend[i] > 0 else 0 
            for i in range(len(labels))
        ]

        total_spend = sum(spend)
        total_sales = sum(sales)
        total_orders = sum(orders)
        total_units = sum(units)
        total_impressions = sum(impressions)
        total_clicks = sum(clicks)

        # Calculate previous period metrics
        period_length = (end_date - start_date).days
        prev_start = start_date - timedelta(days=period_length)
        prev_end = start_date - timedelta(days=1)

        prev_query = AdvertisingReport.query.filter(
            AdvertisingReport.store_id == store_id,
            AdvertisingReport.date.between(prev_start, prev_end)
        )

        if campaign_id:
            prev_query = prev_query.filter(AdvertisingReport.campaign_id == campaign_id)

        prev_reports = prev_query.all()
        previous_spend = sum(float(r.spend) for r in prev_reports)
        previous_sales = sum(float(r.sales) for r in prev_reports)

        spend_growth = ((total_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        sales_growth = ((total_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0

        return {
            'labels': labels,
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'sales': sales,
            'orders': orders,
            'units': units,
            'ctr': ctr,
            'acos': acos,
            'roas': roas,
            'total_spend': total_spend,
            'total_sales': total_sales,
            'total_orders': total_orders,
            'total_units': total_units,
            'total_impressions': total_impressions,
            'total_clicks': total_clicks,
            'spend_growth': spend_growth,
            'sales_growth': sales_growth,
            'previous_spend': previous_spend,
            'previous_sales': previous_sales
        }

    except Exception as e:
        print(f"Error in get_advertising_trends: {str(e)}")
        return _get_empty_trend_data()

def get_campaigns(store_id: int) -> List[Dict]:
    """Get available campaigns for the store."""
    try:
        # Get all campaigns and their IDs for the store
        campaigns = AdvertisingReport.query.with_entities(
            AdvertisingReport.campaign_id,
            AdvertisingReport.campaign_name
        ).distinct().filter_by(store_id=store_id).all()
        
        return [{'id': cid, 'name': name} for cid, name in campaigns]
    except Exception as e:
        print(f"Error in get_campaigns: {str(e)}")
        return []

def _get_empty_trend_data() -> Dict:
    """Return empty trend data structure."""
    return {
        'labels': [],
        'impressions': [],
        'clicks': [],
        'spend': [],
        'sales': [],
        'orders': [],
        'units': [],
        'ctr': [],
        'acos': [],
        'roas': [],
        'total_spend': 0,
        'total_sales': 0,
        'total_orders': 0,
        'total_units': 0,
        'total_impressions': 0,
        'total_clicks': 0,
        'spend_growth': 0,
        'sales_growth': 0,
        'previous_spend': 0,
        'previous_sales': 0
    }

class AdvertisingReportService:
    """Service class for advertising report operations."""

    def get_advertising_data(self, store_id, start_date=None, end_date=None, campaign=None, ad_group=None):
        """Get advertising data based on filters."""
        # Build base query
        query = AdvertisingReport.query.filter(AdvertisingReport.store_id == store_id)

        # Apply date filters
        if start_date:
            query = query.filter(AdvertisingReport.date >= start_date)
        if end_date:
            query = query.filter(AdvertisingReport.date <= end_date)

        # Apply campaign and ad group filters
        if campaign:
            query = query.filter(AdvertisingReport.campaign_name == campaign)
        if ad_group:
            query = query.filter(AdvertisingReport.ad_group_name == ad_group)

        # Get reports
        reports = query.order_by(AdvertisingReport.date).all()

        # Process data for charts and metrics
        performance_data = self._process_performance_data(reports)
        metrics_data = self._process_metrics_data(reports)
        summary_metrics = self._calculate_summary_metrics(reports)
        campaigns_data = self._process_campaigns_data(reports)

        return {
            'performance': performance_data,
            'metrics': metrics_data,
            'summary': summary_metrics,
            'campaigns': campaigns_data
        }

    def get_campaigns(self, store_id):
        """Get list of unique campaign names for the store."""
        campaigns = db.session.query(
            AdvertisingReport.campaign_name,
            func.count(AdvertisingReport.id).label('ad_count')
        ).filter(
            AdvertisingReport.store_id == store_id
        ).group_by(
            AdvertisingReport.campaign_name
        ).all()

        return [{'name': c.campaign_name, 'ad_count': c.ad_count} for c in campaigns]

    def get_ad_groups(self, store_id, campaign=None):
        """Get list of unique ad group names for the store and campaign."""
        query = db.session.query(
            AdvertisingReport.ad_group_name,
            func.count(AdvertisingReport.id).label('ad_count')
        ).filter(AdvertisingReport.store_id == store_id)

        if campaign:
            query = query.filter(AdvertisingReport.campaign_name == campaign)

        ad_groups = query.group_by(AdvertisingReport.ad_group_name).all()

        return [{'name': g.ad_group_name, 'ad_count': g.ad_count} for g in ad_groups]

    def get_trends(self, store_id, start_date=None, end_date=None, campaign=None):
        """Get advertising trends data."""
        # Build base query
        query = db.session.query(
            func.date(AdvertisingReport.date).label('date'),
            func.sum(AdvertisingReport.impressions).label('impressions'),
            func.sum(AdvertisingReport.clicks).label('clicks'),
            func.sum(AdvertisingReport.spend).label('spend'),
            func.sum(AdvertisingReport.sales).label('sales')
        ).filter(AdvertisingReport.store_id == store_id)

        # Apply filters
        if start_date:
            query = query.filter(AdvertisingReport.date >= start_date)
        if end_date:
            query = query.filter(AdvertisingReport.date <= end_date)
        if campaign:
            query = query.filter(AdvertisingReport.campaign_name == campaign)

        # Group by date and get results
        trends = query.group_by(func.date(AdvertisingReport.date)).order_by('date').all()

        # Process trends data
        return self._process_trends_data(trends)

    def _process_performance_data(self, reports):
        """Process reports data for performance chart."""
        dates = []
        acos_data = []
        spend_data = []

        for report in reports:
            dates.append(report.date.strftime('%Y-%m-%d'))
            acos = (report.spend / report.sales * 100) if report.sales > 0 else 0
            acos_data.append(round(acos, 2))
            spend_data.append(round(report.spend, 2))

        return {
            'labels': dates,
            'acos': acos_data,
            'spend': spend_data
        }

    def _process_metrics_data(self, reports):
        """Process reports data for metrics chart."""
        dates = []
        impressions_data = []
        clicks_data = []

        for report in reports:
            dates.append(report.date.strftime('%Y-%m-%d'))
            impressions_data.append(report.impressions)
            clicks_data.append(report.clicks)

        return {
            'labels': dates,
            'impressions': impressions_data,
            'clicks': clicks_data
        }

    def _calculate_summary_metrics(self, reports):
        """Calculate summary metrics from reports."""
        total_spend = sum(r.spend for r in reports)
        total_sales = sum(r.sales for r in reports)
        total_impressions = sum(r.impressions for r in reports)
        total_clicks = sum(r.clicks for r in reports)

        acos = (total_spend / total_sales * 100) if total_sales > 0 else 0
        roas = total_sales / total_spend if total_spend > 0 else 0
        ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0

        return {
            'total_spend': round(total_spend, 2),
            'total_sales': round(total_sales, 2),
            'acos': round(acos, 2),
            'roas': round(roas, 2),
            'impressions': total_impressions,
            'clicks': total_clicks,
            'ctr': round(ctr, 2)
        }

    def _process_campaigns_data(self, reports):
        """Process reports data for campaigns table."""
        # Group reports by campaign
        campaigns = {}
        for report in reports:
            if report.campaign_name not in campaigns:
                campaigns[report.campaign_name] = {
                    'name': report.campaign_name,
                    'status': report.campaign_status,
                    'impressions': 0,
                    'clicks': 0,
                    'spend': 0,
                    'sales': 0
                }
            
            camp = campaigns[report.campaign_name]
            camp['impressions'] += report.impressions
            camp['clicks'] += report.clicks
            camp['spend'] += report.spend
            camp['sales'] += report.sales

        # Calculate metrics for each campaign
        for camp in campaigns.values():
            camp['ctr'] = round((camp['clicks'] / camp['impressions'] * 100), 2) if camp['impressions'] > 0 else 0
            camp['acos'] = round((camp['spend'] / camp['sales'] * 100), 2) if camp['sales'] > 0 else 0
            camp['spend'] = round(camp['spend'], 2)
            camp['sales'] = round(camp['sales'], 2)

        return list(campaigns.values())

    def _process_trends_data(self, trends):
        """Process trends data."""
        dates = []
        impressions = []
        clicks = []
        spend = []
        sales = []
        acos = []
        ctr = []

        for trend in trends:
            dates.append(trend.date.strftime('%Y-%m-%d'))
            impressions.append(trend.impressions)
            clicks.append(trend.clicks)
            spend.append(round(trend.spend, 2))
            sales.append(round(trend.sales, 2))
            
            # Calculate derived metrics
            current_acos = (trend.spend / trend.sales * 100) if trend.sales > 0 else 0
            current_ctr = (trend.clicks / trend.impressions * 100) if trend.impressions > 0 else 0
            
            acos.append(round(current_acos, 2))
            ctr.append(round(current_ctr, 2))

        return {
            'dates': dates,
            'impressions': impressions,
            'clicks': clicks,
            'spend': spend,
            'sales': sales,
            'acos': acos,
            'ctr': ctr
        }

    @staticmethod
    def get_performance_metrics(store_id: int, days: int = 30) -> Dict:
        """Get key performance metrics for the dashboard.
        
        Args:
            store_id: Store ID to get metrics for
            days: Number of days to look back
            
        Returns:
            Dict containing performance metrics
        """
        try:
            # Get date range
            end_date = datetime.now()
            start_date = end_date - pd.Timedelta(days=days)

            # Get data
            reports = AdvertisingReport.query.filter(
                AdvertisingReport.store_id == store_id,
                AdvertisingReport.date.between(start_date, end_date)
            ).all()

            if not reports:
                return {'error': ERROR_MESSAGES['NO_DATA']}

            # Convert to DataFrame
            df = pd.DataFrame([r.to_dict() for r in reports])

            # Calculate metrics
            total_spend = float(df['spend'].sum())
            total_sales = float(df['sales'].sum())
            total_impressions = int(df['impressions'].sum())
            total_clicks = int(df['clicks'].sum())

            return {
                'total_spend': total_spend,
                'total_sales': total_sales,
                'total_impressions': total_impressions,
                'total_clicks': total_clicks,
                'roas': float(total_sales / total_spend) if total_spend > 0 else 0,
                'acos': float((total_spend / total_sales) * 100) if total_sales > 0 else 0,
                'ctr': float((total_clicks / total_impressions) * 100) if total_impressions > 0 else 0,
                'cpc': float(total_spend / total_clicks) if total_clicks > 0 else 0
            }

        except Exception as e:
            return {'error': str(e)} 