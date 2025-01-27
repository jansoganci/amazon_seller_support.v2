"""Inventory module routes."""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.utils.analytics_engine import AnalyticsEngine
from app.core.models import Store
from app.modules.inventory.models import InventoryReport
from app.utils.decorators import store_required
from app.modules.inventory.services import InventoryReportService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('inventory', __name__, 
               url_prefix='/inventory',
               template_folder='templates')

@bp.route('/')
@login_required
def index():
    """Inventory report index page."""
    return render_template('inventory/index.html')

@bp.route('/inventory_report')
@login_required
@store_required
def inventory_report():
    """Render the inventory report page."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Loading inventory report for store_id: {store_id}")
        
        if not current_user.has_store_access(store_id):
            logger.warning(f"User {current_user.id} attempted to access store {store_id} without permission")
            flash('You do not have access to this store', 'error')
            return redirect(url_for('dashboard.index'))
            
        # Initialize service
        logger.debug("Initializing InventoryReportService")
        service = InventoryReportService(store_id)
        
        # Get date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        
        # Get trends data
        logger.debug("Fetching trends data from %s to %s", start_date, end_date)
        trends_data = service.get_trends(start_date, end_date)
        
        # Get SKUs for filtering
        logger.debug("Fetching SKUs")
        skus = service.get_skus()
        
        return render_template(
            'inventory/inventory_report.html',
            trends_data=trends_data,
            skus=skus
        )
        
    except Exception as e:
        logger.exception(f"Error rendering inventory report: {str(e)}")
        flash('An error occurred while loading the report', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/data')
@store_required
def get_inventory_data():
    """Get inventory data for the specified store."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Getting inventory data for store_id: {store_id}")
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        asin = request.args.get('asin')
        
        # Initialize service
        service = InventoryReportService(store_id)
        
        # Get data
        data = service.get_data(
            start_date=start_date,
            end_date=end_date,
            category=category,
            asin=asin
        )
        
        return jsonify(data)
        
    except Exception as e:
        logger.exception(f"Error getting inventory data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/asins')
@store_required
def get_asins():
    """Get list of ASINs for a category."""
    try:
        store_id = current_user.active_store_id
        category = request.args.get('category')
        service = InventoryReportService(store_id)
        asins = service.get_asins(category=category)
        return jsonify(asins)
    except Exception as e:
        logger.exception(f"Error getting ASINs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get inventory trends data."""
    try:
        store_id = current_user.active_store_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        category = request.args.get('category')
        asin = request.args.get('asin')
        
        service = InventoryReportService(store_id)
        trends = service.get_trends(
            start_date=start_date,
            end_date=end_date,
            category=category,
            asin=asin
        )
        
        return jsonify(trends)
        
    except Exception as e:
        logger.exception(f"Error getting trends: {str(e)}")
        return jsonify({'error': str(e)}), 500
