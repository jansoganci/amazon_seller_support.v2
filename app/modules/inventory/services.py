from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.extensions import db
from app.modules.inventory.models import InventoryReport

class InventoryReportService:
    def get_inventory_data(self, store_id, start_date=None, end_date=None, asin=None, warehouse=None):
        """Get inventory data based on filters."""
        # Build base query
        query = InventoryReport.query.filter(InventoryReport.store_id == store_id)

        # Apply date filters
        if start_date:
            query = query.filter(InventoryReport.date >= start_date)
        if end_date:
            query = query.filter(InventoryReport.date <= end_date)

        # Apply ASIN and warehouse filters
        if asin:
            query = query.filter(InventoryReport.asin == asin)
        if warehouse:
            query = query.filter(InventoryReport.warehouse == warehouse)

        # Get reports
        reports = query.order_by(InventoryReport.date).all()

        # Process data for charts and metrics
        stock_levels = self._process_stock_levels(reports)
        stock_distribution = self._process_stock_distribution(reports)
        summary_metrics = self._calculate_summary_metrics(reports)
        inventory_items = self._process_inventory_items(reports)

        return {
            'stock_levels': stock_levels,
            'stock_distribution': stock_distribution,
            'summary': summary_metrics,
            'inventory_items': inventory_items
        }

    def get_asins(self, store_id):
        """Get list of unique ASINs for the store."""
        asins = db.session.query(
            InventoryReport.asin,
            InventoryReport.product_name,
            func.sum(InventoryReport.sellable).label('total_sellable')
        ).filter(
            InventoryReport.store_id == store_id
        ).group_by(
            InventoryReport.asin,
            InventoryReport.product_name
        ).all()

        return [{
            'asin': a.asin,
            'product_name': a.product_name,
            'total_sellable': a.total_sellable
        } for a in asins]

    def get_warehouses(self, store_id):
        """Get list of unique warehouses for the store."""
        warehouses = db.session.query(
            InventoryReport.warehouse,
            func.count(InventoryReport.id).label('item_count')
        ).filter(
            InventoryReport.store_id == store_id
        ).group_by(
            InventoryReport.warehouse
        ).all()

        return [{
            'name': w.warehouse,
            'item_count': w.item_count
        } for w in warehouses]

    def get_trends(self, store_id, start_date=None, end_date=None, asin=None):
        """Get inventory trends data."""
        # Build base query
        query = db.session.query(
            func.date(InventoryReport.date).label('date'),
            func.sum(InventoryReport.sellable).label('sellable'),
            func.sum(InventoryReport.unsellable).label('unsellable'),
            func.sum(InventoryReport.reserved).label('reserved')
        ).filter(InventoryReport.store_id == store_id)

        # Apply filters
        if start_date:
            query = query.filter(InventoryReport.date >= start_date)
        if end_date:
            query = query.filter(InventoryReport.date <= end_date)
        if asin:
            query = query.filter(InventoryReport.asin == asin)

        # Group by date and get results
        trends = query.group_by(func.date(InventoryReport.date)).order_by('date').all()

        # Process trends data
        return self._process_trends_data(trends)

    def _process_stock_levels(self, reports):
        """Process reports data for stock levels chart."""
        dates = []
        sellable_data = []
        reserved_data = []

        for report in reports:
            dates.append(report.date.strftime('%Y-%m-%d'))
            sellable_data.append(report.sellable)
            reserved_data.append(report.reserved)

        return {
            'labels': dates,
            'sellable': sellable_data,
            'reserved': reserved_data
        }

    def _process_stock_distribution(self, reports):
        """Process reports data for stock distribution chart."""
        total_sellable = sum(r.sellable for r in reports)
        total_unsellable = sum(r.unsellable for r in reports)
        total_reserved = sum(r.reserved for r in reports)

        return {
            'sellable': total_sellable,
            'unsellable': total_unsellable,
            'reserved': total_reserved
        }

    def _calculate_summary_metrics(self, reports):
        """Calculate summary metrics from reports."""
        total_stock = sum(r.sellable + r.unsellable + r.reserved for r in reports)
        reserved_stock = sum(r.reserved for r in reports)
        low_stock_items = sum(1 for r in reports if r.sellable < r.reorder_point) if hasattr(InventoryReport, 'reorder_point') else 0

        return {
            'total_stock': total_stock,
            'reserved_stock': reserved_stock,
            'low_stock_items': low_stock_items
        }

    def _process_inventory_items(self, reports):
        """Process reports data for inventory items table."""
        # Group reports by ASIN
        items = {}
        for report in reports:
            if report.asin not in items:
                items[report.asin] = {
                    'asin': report.asin,
                    'sku': report.sku,
                    'product_name': report.product_name,
                    'sellable': 0,
                    'unsellable': 0,
                    'reserved': 0,
                    'warehouse': report.warehouse
                }
            
            item = items[report.asin]
            item['sellable'] += report.sellable
            item['unsellable'] += report.unsellable
            item['reserved'] += report.reserved

        return list(items.values())

    def _process_trends_data(self, trends):
        """Process trends data."""
        dates = []
        sellable = []
        unsellable = []
        reserved = []
        total = []

        for trend in trends:
            dates.append(trend.date.strftime('%Y-%m-%d'))
            sellable.append(trend.sellable)
            unsellable.append(trend.unsellable)
            reserved.append(trend.reserved)
            total.append(trend.sellable + trend.unsellable + trend.reserved)

        return {
            'dates': dates,
            'sellable': sellable,
            'unsellable': unsellable,
            'reserved': reserved,
            'total': total
        }
