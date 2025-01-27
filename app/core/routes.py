"""Core module routes."""

from flask import Blueprint, jsonify, request, current_app, render_template
from flask_login import login_required, current_user
from app.models.user import User
from app.models.store import Store
from app.modules.upload_csv import CSVFile
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('core', __name__)  # Remove URL prefix for main routes

# Main routes
@bp.route('/')
@login_required
def index():
    """Render homepage."""
    return render_template('index.html')

@bp.route('/upload')
@login_required
def upload():
    """Render upload page."""
    return render_template('core/upload.html')

@bp.route('/uploaded-datas')
@login_required
def uploaded_datas():
    """Render uploaded datas page."""
    return render_template('core/uploaded_datas.html')

@bp.route('/settings')
@login_required
def settings():
    """Render settings page."""
    return render_template('core/settings.html')

# API routes
@bp.route('/api/upload-history', methods=['GET'])
@login_required
def get_upload_history():
    """Get upload history for current user."""
    try:
        history = UploadHistory.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': h.id,
            'filename': h.csv_file.filename,
            'file_type': h.csv_file.file_type,
            'status': h.status,
            'message': h.message,
            'created_at': h.created_at.isoformat()
        } for h in history])
    except Exception as e:
        current_app.logger.error(f"Error getting upload history: {str(e)}")
        return jsonify({'error': 'Failed to get upload history'}), 500

@bp.route('/api/stores', methods=['GET'])
@login_required
def get_stores():
    """Get stores for current user."""
    try:
        stores = Store.query.filter_by(user_id=current_user.id).all()
        return jsonify([{
            'id': s.id,
            'seller_id': s.seller_id,
            'marketplace': s.marketplace
        } for s in stores])
    except Exception as e:
        current_app.logger.error(f"Error getting stores: {str(e)}")
        return jsonify({'error': 'Failed to get stores'}), 500 