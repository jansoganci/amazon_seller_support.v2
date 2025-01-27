from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.extensions import db
from app.modules.returns.models import ReturnReport

class ReturnReportService:
    def __init__(self, store_id):
        """Initialize service with store_id."""
        self.store_id = store_id

    def get_return_data(self, start_date=None, end_date=None, asin=None, return_reason=None):
        """Get return data based on filters."""
        # Build base query
        query = ReturnReport.query.filter(ReturnReport.store_id == self.store_id)

        # Apply date filters
        if start_date:
            query = query.filter(ReturnReport.return_date >= start_date)
        if end_date:
            query = query.filter(ReturnReport.return_date <= end_date)

        # Apply ASIN and return reason filters
        if asin:
            query = query.filter(ReturnReport.asin == asin)
        if return_reason:
            query = query.filter(ReturnReport.return_reason == return_reason)

        # Get reports
        reports = query.order_by(ReturnReport.return_date).all()

        # Process data for charts and metrics
        return_rate = self._process_return_rate(reports)
        return_reasons = self._process_return_reasons(reports)
        summary_metrics = self._calculate_summary_metrics(reports)
        return_items = self._process_return_items(reports)

        return {
            'return_rate': return_rate,
            'return_reasons': return_reasons,
            'summary': summary_metrics,
            'return_items': return_items
        }

    def get_asins(self):
        """Get list of unique ASINs for the store."""
        asins = db.session.query(
            ReturnReport.asin,
            ReturnReport.title,
            func.count(ReturnReport.id).label('return_count')
        ).filter(
            ReturnReport.store_id == self.store_id
        ).group_by(
            ReturnReport.asin,
            ReturnReport.title
        ).all()

        return [{
            'asin': a.asin,
            'title': a.title,
            'return_count': a.return_count
        } for a in asins]

    def get_return_reasons(self):
        """Get list of unique return reasons for the store."""
        reasons = db.session.query(
            ReturnReport.return_reason,
            func.count(ReturnReport.id).label('count')
        ).filter(
            ReturnReport.store_id == self.store_id
        ).group_by(
            ReturnReport.return_reason
        ).all()

        return [{
            'reason': r.return_reason,
            'count': r.count
        } for r in reasons]

    def get_trends(self, start_date=None, end_date=None, asin=None):
        """Get return trends data."""
        # Build base query
        query = db.session.query(
            func.date(ReturnReport.return_date).label('date'),
            func.count(ReturnReport.id).label('returns'),
            func.sum(ReturnReport.quantity).label('quantity'),
            func.sum(ReturnReport.refund_amount).label('refund_amount')
        ).filter(ReturnReport.store_id == self.store_id)

        # Apply filters
        if start_date:
            query = query.filter(ReturnReport.return_date >= start_date)
        if end_date:
            query = query.filter(ReturnReport.return_date <= end_date)
        if asin:
            query = query.filter(ReturnReport.asin == asin)

        # Group by date and get results
        trends = query.group_by(func.date(ReturnReport.return_date)).order_by('date').all()

        # Process trends data
        return self._process_trends_data(trends)

    def _process_return_rate(self, reports):
        """Process reports data for return rate chart."""
        dates = []
        rates = []

        # Group reports by date
        daily_returns = {}
        for report in reports:
            date_str = report.return_date.strftime('%Y-%m-%d')
            if date_str not in daily_returns:
                daily_returns[date_str] = {
                    'returns': 0,
                    'total_orders': report.total_orders if hasattr(report, 'total_orders') else 100  # Fallback value
                }
            daily_returns[date_str]['returns'] += report.quantity

        # Calculate daily return rates
        for date_str, data in sorted(daily_returns.items()):
            dates.append(date_str)
            rate = (data['returns'] / data['total_orders'] * 100) if data['total_orders'] > 0 else 0
            rates.append(round(rate, 2))

        return {
            'labels': dates,
            'rates': rates
        }

    def _process_return_reasons(self, reports):
        """Process reports data for return reasons chart."""
        reason_counts = {}
        for report in reports:
            if report.return_reason not in reason_counts:
                reason_counts[report.return_reason] = 0
            reason_counts[report.return_reason] += report.quantity

        return {
            'reasons': list(reason_counts.keys()),
            'counts': list(reason_counts.values())
        }

    def _calculate_summary_metrics(self, reports):
        """Calculate summary metrics from reports."""
        total_returns = sum(r.quantity for r in reports)
        total_refund = sum(r.refund_amount for r in reports)
        total_orders = sum(r.total_orders if hasattr(r, 'total_orders') else 100 for r in reports)  # Fallback value
        return_rate = (total_returns / total_orders * 100) if total_orders > 0 else 0

        return {
            'total_returns': total_returns,
            'total_refund': round(total_refund, 2),
            'return_rate': round(return_rate, 2)
        }

    def _process_return_items(self, reports):
        """Process reports data for return items table."""
        return [{
            'return_date': report.return_date.strftime('%Y-%m-%d'),
            'order_id': report.order_id,
            'asin': report.asin,
            'title': report.title,
            'quantity': report.quantity,
            'return_reason': report.return_reason,
            'refund_amount': round(report.refund_amount, 2),
            'status': report.status
        } for report in reports]

    def _process_trends_data(self, trends):
        """Process trends data."""
        dates = []
        returns = []
        quantities = []
        refund_amounts = []
        daily_rates = []

        for trend in trends:
            dates.append(trend.date.strftime('%Y-%m-%d'))
            returns.append(trend.returns)
            quantities.append(trend.quantity)
            refund_amounts.append(round(trend.refund_amount, 2))
            
            # Calculate daily return rate (assuming we have total orders data)
            total_orders = 100  # Fallback value if we don't have actual data
            rate = (trend.quantity / total_orders * 100) if total_orders > 0 else 0
            daily_rates.append(round(rate, 2))

        return {
            'dates': dates,
            'returns': returns,
            'quantities': quantities,
            'refund_amounts': refund_amounts,
            'daily_rates': daily_rates
        }
