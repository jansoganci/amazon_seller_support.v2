"""Advertising module routes."""

from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from app.utils.analytics_engine import AnalyticsEngine
from app.core.models import Store
from app.modules.advertising.models import AdvertisingReport
from app.utils.constants import get_category_by_asin, ASIN_CATEGORIES
from app.modules.upload_csv.processors.advertising import AdvertisingCSVProcessor
import logging
import os
import pandas as pd
from app.modules.advertising.constants import ERROR_MESSAGES
from app.modules.upload_csv.exceptions import CSVError
from app.utils.decorators import store_required
from app.modules.advertising.services import AdvertisingReportService

logger = logging.getLogger(__name__)

bp = Blueprint('advertising', __name__, 
               url_prefix='/advertising',
               template_folder='templates')

@bp.route('/')
@login_required
def index():
    """Advertising report index page."""
    return render_template('advertising/index.html')

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload advertising report."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Process advertising report
    return jsonify({'message': 'File uploaded successfully'}), 200

@bp.route('/process-csv', methods=['POST'])
@login_required
@store_required
def process_csv():
    """Advertising report CSV processing endpoint."""
    try:
        # Get DataFrame from request
        df = pd.DataFrame(request.json['data'])
        
        # Process CSV
        processor = AdvertisingCSVProcessor()
        processor.user_id = current_user.id
        success, message, metadata = processor.process_data(df)

        if not success:
            return jsonify({'success': False, 'message': message}), 400

        return jsonify({
            'success': True,
            'message': message,
            'metadata': metadata
        })

    except CSVError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"CSV processing error: {str(e)}")
        return jsonify({'success': False, 'message': ERROR_MESSAGES['UNKNOWN_ERROR']}), 500

@bp.route('/advertising_report')
@login_required
@store_required
def advertising_report():
    """Render the advertising report page."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Loading advertising report for store_id: {store_id}")
        
        if not current_user.has_store_access(store_id):
            logger.warning(f"User {current_user.id} attempted to access store {store_id} without permission")
            flash('You do not have access to this store', 'error')
            return redirect(url_for('dashboard.index'))
            
        # Initialize service
        logger.debug("Initializing AdvertisingReportService")
        service = AdvertisingReportService(store_id)
        
        # Get initial data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        logger.debug(f"Fetching trends data from {start_date} to {end_date}")
        initial_data = service.get_trends(
            start_date=start_date,
            end_date=end_date
        )
        
        # Get filter options
        logger.debug("Fetching campaigns and ad groups")
        campaigns = service.get_campaigns()
        ad_groups = service.get_ad_groups()
        
        return render_template(
            'advertising/advertising_report.html',
            store_id=store_id,
            initial_data=initial_data,
            campaigns=campaigns,
            ad_groups=ad_groups
        )
        
    except Exception as e:
        logger.exception(f"Error rendering advertising report: {str(e)}")
        flash('An error occurred while loading the report', 'error')
        return redirect(url_for('dashboard.index'))

@bp.route('/data')
@store_required
def get_advertising_data():
    """Get advertising data for the specified store."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Getting advertising data for store_id: {store_id}")
        
        # Get query parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        campaign_id = request.args.get('campaign_id')
        ad_group_id = request.args.get('ad_group_id')
        
        # Initialize service
        service = AdvertisingReportService(store_id)
        
        # Get data
        data = service.get_data(
            start_date=start_date,
            end_date=end_date,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id
        )
        
        return jsonify(data)
        
    except Exception as e:
        logger.exception(f"Error getting advertising data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/campaigns')
@store_required
def get_campaigns():
    """Get list of campaigns for the store."""
    try:
        store_id = current_user.active_store_id
        service = AdvertisingReportService(store_id)
        campaigns = service.get_campaigns()
        return jsonify(campaigns)
    except Exception as e:
        logger.exception(f"Error getting campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/ad-groups')
@store_required
def get_ad_groups():
    """Get list of ad groups for a campaign."""
    try:
        store_id = current_user.active_store_id
        campaign_id = request.args.get('campaign_id')
        service = AdvertisingReportService(store_id)
        ad_groups = service.get_ad_groups(campaign_id=campaign_id)
        return jsonify(ad_groups)
    except Exception as e:
        logger.exception(f"Error getting ad groups: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get advertising trends data."""
    try:
        store_id = current_user.active_store_id
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        campaign_id = request.args.get('campaign_id')
        ad_group_id = request.args.get('ad_group_id')
        
        service = AdvertisingReportService(store_id)
        trends = service.get_trends(
            start_date=start_date,
            end_date=end_date,
            campaign_id=campaign_id,
            ad_group_id=ad_group_id
        )
        
        return jsonify(trends)
        
    except Exception as e:
        logger.exception(f"Error getting trends: {str(e)}")
        return jsonify({'error': str(e)}), 500