"""Inventory report services."""

from datetime import datetime, timedelta
from sqlalchemy import func, and_
from app.extensions import db
from app.modules.inventory.models.report import InventoryReport

class InventoryReportService:
    def __init__(self, store_id):
        """Initialize service with store_id."""
        self.store_id = store_id

    def get_data(self, start_date=None, end_date=None, sku=None, asin=None):
        """Get inventory data based on filters."""
        query = InventoryReport.query.filter(InventoryReport.store_id == self.store_id)
        
        if start_date:
            query = query.filter(InventoryReport.date >= start_date)
        if end_date:
            query = query.filter(InventoryReport.date <= end_date)
        if sku:
            query = query.filter(InventoryReport.sku == sku)
        if asin:
            query = query.filter(InventoryReport.asin == asin)
            
        return query.all()

    def get_skus(self):
        """Get list of SKUs for the store."""
        skus = db.session.query(
            InventoryReport.sku,
            InventoryReport.product_name
        ).filter(
            InventoryReport.store_id == self.store_id
        ).distinct().all()
        
        return [{'sku': s.sku, 'name': s.product_name} for s in skus]

    def get_trends(self, start_date=None, end_date=None, sku=None):
        """Get inventory trends data."""
        query = db.session.query(
            func.date(InventoryReport.date),
            func.sum(InventoryReport.afn_fulfillable_quantity + InventoryReport.mfn_fulfillable_quantity).label('sellable'),
            func.sum(InventoryReport.afn_unsellable_quantity).label('unsellable'),
            func.sum(InventoryReport.afn_reserved_quantity).label('reserved')
        ).filter(
            InventoryReport.store_id == self.store_id
        )

        if start_date:
            query = query.filter(InventoryReport.date >= start_date)
        if end_date:
            query = query.filter(InventoryReport.date <= end_date)
        if sku:
            query = query.filter(InventoryReport.sku == sku)

        query = query.group_by(func.date(InventoryReport.date))
        results = query.all()

        return [{
            'date': str(r[0]),
            'sellable': r[1],
            'unsellable': r[2],
            'reserved': r[3],
            'total': r[1] + r[2] + r[3]
        } for r in results]
