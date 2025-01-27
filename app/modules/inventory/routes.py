"""Inventory routes."""
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime
import os
from app.modules.inventory.models import InventoryReport
from app.modules.inventory.services import InventoryReportService
from app.utils.decorators import store_required

bp = Blueprint('inventory', __name__, 
               url_prefix='/inventory',
               template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@bp.route('/')
@login_required
def index():
    """Inventory report index page."""
    return render_template('inventory/index.html')

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload inventory report."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Process inventory report
    return jsonify({'message': 'File uploaded successfully'}), 200

@bp.route('/report')
@store_required
def inventory_report():
    """Render the inventory report page."""
    template_path = os.path.join('inventory', 'inventory_report.html')
    return render_template(template_path)

@bp.route('/data')
@store_required
def get_inventory_data():
    """Get inventory data based on filters."""
    try:
        # Get filter parameters
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        asin = request.args.get('asin', type=str)
        warehouse = request.args.get('warehouse', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # Get data from service
        service = InventoryReportService()
        data = service.get_inventory_data(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            asin=asin,
            warehouse=warehouse
        )

        return jsonify(data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/asins')
@store_required
def get_asins():
    """Get list of ASINs for the store."""
    try:
        store_id = request.args.get('store_id', type=int)
        service = InventoryReportService()
        asins = service.get_asins(store_id)
        return jsonify(asins)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/warehouses')
@store_required
def get_warehouses():
    """Get list of warehouses for the store."""
    try:
        store_id = request.args.get('store_id', type=int)
        service = InventoryReportService()
        warehouses = service.get_warehouses(store_id)
        return jsonify(warehouses)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get inventory trends data."""
    try:
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        asin = request.args.get('asin', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        service = InventoryReportService()
        trends = service.get_trends(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            asin=asin
        )
        return jsonify(trends)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500
