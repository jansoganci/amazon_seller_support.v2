"""CSV upload routes."""
from typing import List, Dict, Any
from datetime import datetime, UTC

from flask import Blueprint, render_template, request, jsonify, current_app, flash
from flask_login import login_required, current_user
from sqlalchemy import select
import os
import logging

from app.extensions import db
from .models.csv_file import CSVFile
from .models.upload_history import UploadHistory
from .processors.business import BusinessCSVProcessor
from .processors.advertising import AdvertisingCSVProcessor
from .processors.inventory import InventoryCSVProcessor
from .processors.returns import ReturnCSVProcessor
from .utils import create_upload_folders

logger = logging.getLogger(__name__)

bp = Blueprint('upload_csv', __name__, template_folder='templates')

# Map report types to their processors
PROCESSORS = {
    'business_report': BusinessCSVProcessor,
    'advertising_report': AdvertisingCSVProcessor,
    'inventory_report': InventoryCSVProcessor,
    'return_report': ReturnCSVProcessor
}

@bp.route('/')
@login_required
def index() -> str:
    """Upload CSV index page."""
    # Get last 10 uploads for current user
    upload_history = UploadHistory.query.filter_by(user_id=current_user.id).order_by(UploadHistory.created_at.desc()).limit(10).all()

    return render_template(
        'upload_csv/upload.html',
        uploads=upload_history
    )

@bp.route('/upload')
@login_required
def upload_page() -> str:
    """CSV upload page."""
    report_types: List[str] = list(PROCESSORS.keys())
    
    # Get upload history for current user using SQLAlchemy 2.0 syntax
    stmt = (
        select(CSVFile, UploadHistory)
        .join(UploadHistory, CSVFile.id == UploadHistory.csv_file_id)
        .where(CSVFile.user_id == current_user.id)
        .order_by(CSVFile.created_at.desc())
        .limit(10)  # Show last 10 uploads
    )
    uploads = db.session.execute(stmt).all()
    
    # Format upload history data
    upload_history: List[Dict[str, Any]] = []
    for csv_file, history in uploads:
        upload_history.append({
            'filename': csv_file.filename,
            'file_type': csv_file.file_type,
            'upload_date': csv_file.created_at,
            'status': history.status,
            'error_message': history.error_message if history.status == 'failed' else None,
            'rows_processed': history.rows_processed
        })
    
    return render_template(
        'upload_csv/upload.html',
        report_types=report_types,
        uploads=upload_history
    )

@bp.route('/upload', methods=['POST'])
@login_required
def upload() -> tuple[Any, int]:
    """Upload and process CSV file."""
    try:
        # Debug: Log current user
        logger.info(f"Current user: ID={current_user.id}, Username={current_user.username}")
        logger.info(f"User's stores: {[store.id for store in current_user.stores]}")
        
        # Validate request
        if 'file' not in request.files:
            logger.error("No file in request")
            return jsonify({'error': 'No file was selected. Please choose a CSV file to upload.'}), 400
            
        file = request.files['file']
        if file.filename == '':
            logger.error("Empty filename")
            return jsonify({'error': 'No file was selected. The filename is empty.'}), 400
            
        report_type = request.form.get('report_type')
        if not report_type:
            logger.error("No report type specified")
            return jsonify({'error': 'Report type is required. Please select a valid report type.'}), 400
            
        if report_type not in PROCESSORS:
            logger.error(f"Invalid report type: {report_type}")
            return jsonify({
                'error': f"Invalid report type: '{report_type}'. Valid report types are: {', '.join(PROCESSORS.keys())}"
            }), 400
            
        # Get appropriate processor
        processor_class = PROCESSORS[report_type]
        processor = processor_class()
        
        # Process file
        logger.info(f"Processing file: {file.filename} for report type: {report_type}")
        success, message = processor.process_file(file, current_user.id)
        
        if success:
            logger.info(f"File processed successfully: {file.filename}")
            return jsonify({
                'message': 'File processed successfully.',
                'status': 'success',
                'report_type': report_type
            }), 200
        else:
            # More specific error messages based on the failure
            logger.error(f"File processing failed: {message}")
            if "missing columns" in str(message).lower():
                error_msg = f"Required columns are missing in the CSV file: {message}"
            elif "invalid data" in str(message).lower():
                error_msg = f"The CSV file contains invalid data: {message}"
            elif "store not found" in str(message).lower():
                error_msg = f"Store not found or access denied: {message}"
            else:
                error_msg = f"Processing failed: {message}"
            
            return jsonify({
                'error': error_msg,
                'status': 'error',
                'report_type': report_type
            }), 400
            
    except Exception as e:
        logger.exception(f"Upload error: {str(e)}")
        return jsonify({
            'error': f"Server error occurred while processing the file: {str(e)}",
            'status': 'error',
            'report_type': request.form.get('report_type', 'unknown')
        }), 500