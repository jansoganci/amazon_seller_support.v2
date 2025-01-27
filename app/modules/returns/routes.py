"""Returns module routes."""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, current_app
from flask_login import login_required, current_user
from app.utils.analytics_engine import AnalyticsEngine
from app.core.models import Store
from app.modules.returns.models import ReturnReport
from app.utils.decorators import store_required
from app.modules.returns.services import ReturnReportService
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('returns', __name__, 
               url_prefix='/returns',
               template_folder='templates')

@bp.route('/')
@login_required
def index():
    """Returns report index page."""
    return render_template('returns/index.html')

@bp.route('/returns_report')
@login_required
@store_required
def returns_report():
    """Render returns report page."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Loading returns report for store_id: {store_id}")
        
        if not current_user.has_store_access(store_id):
            logger.warning(f"User {current_user.id} attempted to access store {store_id} without permission")
            flash('You do not have access to this store', 'error')
            return redirect(url_for('dashboard.index'))
            
        # Initialize service
        logger.debug("Initializing ReturnReportService")
        service = ReturnReportService(store_id)
        
        # Get initial data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        logger.debug(f"Fetching trends data from {start_date} to {end_date}")
        initial_data = service.get_trends(
            start_date=start_date,
            end_date=end_date
        )
        
        # Get filter options
        logger.debug("Fetching return reasons and ASINs")
        reasons = service.get_return_reasons()
        asins = service.get_asins()
        
        return render_template(
            'returns/return_report.html',
            store_id=store_id,
            initial_data=initial_data,
            reasons=reasons,
            asins=asins
        )
        
    except Exception as e:
        logger.exception(f"Error rendering returns report: {str(e)}")
        flash('An error occurred while loading the report', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/data')
@store_required
def get_returns_data():
    """Get returns data for the specified store."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Getting returns data for store_id: {store_id}")
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        reason = request.args.get('reason')
        asin = request.args.get('asin')
        
        # Initialize service
        service = ReturnReportService(store_id)
        
        # Get data
        data = service.get_data(
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            asin=asin
        )
        
        return jsonify(data)
        
    except Exception as e:
        logger.exception(f"Error getting returns data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/reasons')
@store_required
def get_return_reasons():
    """Get list of return reasons for the store."""
    try:
        store_id = current_user.active_store_id
        service = ReturnReportService(store_id)
        reasons = service.get_return_reasons()
        return jsonify(reasons)
    except Exception as e:
        logger.exception(f"Error getting return reasons: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/asins')
@store_required
def get_asins():
    """Get list of ASINs for a return reason."""
    try:
        store_id = current_user.active_store_id
        reason = request.args.get('reason')
        service = ReturnReportService(store_id)
        asins = service.get_asins(reason=reason)
        return jsonify(asins)
    except Exception as e:
        logger.exception(f"Error getting ASINs: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get returns trends data."""
    try:
        store_id = current_user.active_store_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        reason = request.args.get('reason')
        asin = request.args.get('asin')
        
        service = ReturnReportService(store_id)
        trends = service.get_trends(
            start_date=start_date,
            end_date=end_date,
            reason=reason,
            asin=asin
        )
        
        return jsonify(trends)
        
    except Exception as e:
        logger.exception(f"Error getting trends: {str(e)}")
        return jsonify({'error': str(e)}), 500
