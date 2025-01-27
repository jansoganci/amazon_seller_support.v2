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
from . import bp  # Import bp from __init__.py instead of redefining it

logger = logging.getLogger(__name__)

bp = Blueprint('advertising', __name__, template_folder='templates')

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

@bp.route('/report')
@login_required
@store_required
def advertising_report():
    """Render the advertising report page."""
    return render_template('advertising/advertising_report.html')

@bp.route('/data')
@store_required
def get_advertising_data():
    """Get advertising data based on filters."""
    try:
        # Get filter parameters
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        campaign = request.args.get('campaign', type=str)
        ad_group = request.args.get('ad_group', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # Get data from service
        service = AdvertisingReportService()
        data = service.get_advertising_data(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            campaign=campaign,
            ad_group=ad_group
        )

        return jsonify(data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/campaigns')
@store_required
def get_campaigns():
    """Get list of campaigns for the store."""
    try:
        store_id = request.args.get('store_id', type=int)
        service = AdvertisingReportService()
        campaigns = service.get_campaigns(store_id)
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/ad-groups')
@store_required
def get_ad_groups():
    """Get list of ad groups for a campaign."""
    try:
        store_id = request.args.get('store_id', type=int)
        campaign = request.args.get('campaign', type=str)
        service = AdvertisingReportService()
        ad_groups = service.get_ad_groups(store_id, campaign)
        return jsonify(ad_groups)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get advertising trends data."""
    try:
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        campaign = request.args.get('campaign', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        service = AdvertisingReportService()
        trends = service.get_trends(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            campaign=campaign
        )
        return jsonify(trends)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500 