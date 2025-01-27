"""CSV upload routes."""
from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
import os
import logging

# Import processors directly from their modules
from .processors.business import BusinessCSVProcessor
from .processors.advertising import AdvertisingCSVProcessor
from .processors.inventory import InventoryCSVProcessor
from .processors.returns import ReturnCSVProcessor

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
def index():
    """Dashboard page."""
    return render_template('upload_csv/dashboard.html')

@bp.route('/upload')
@login_required
def upload_page():
    """CSV upload page."""
    report_types = list(PROCESSORS.keys())
    return render_template('upload_csv/upload.html', report_types=report_types)

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload and process CSV file."""
    try:
        # Validate request
        if 'file' not in request.files:
            return jsonify({'error': 'Lütfen bir dosya seçin.'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Dosya seçilmedi.'}), 400
            
        report_type = request.form.get('report_type')
        if not report_type:
            return jsonify({'error': 'Rapor türü belirtilmedi.'}), 400
            
        if report_type not in PROCESSORS:
            return jsonify({'error': f"Geçersiz rapor türü: {report_type}"}), 400
            
        # Get appropriate processor
        processor_class = PROCESSORS[report_type]
        processor = processor_class()
        
        # Process file
        success, message = processor.process_file(file, current_user.id)
        
        if success:
            return jsonify({
                'message': message,
                'status': 'success',
                'report_type': report_type
            }), 200
        else:
            # More specific error messages based on the failure
            if "missing columns" in message.lower():
                error_msg = f"Eksik sütunlar: {message}"
            elif "invalid data" in message.lower():
                error_msg = f"Geçersiz veri: {message}"
            elif "store not found" in message.lower():
                error_msg = f"Mağaza bulunamadı: {message}"
            else:
                error_msg = f"İşlem başarısız: {message}"
            
            return jsonify({
                'error': error_msg,
                'status': 'error',
                'report_type': report_type
            }), 400
            
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        return jsonify({
            'error': f"Sunucu hatası: {str(e)}",
            'status': 'error',
            'report_type': request.form.get('report_type', 'unknown')
        }), 500