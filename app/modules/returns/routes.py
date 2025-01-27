"""Returns routes."""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from datetime import datetime
import os
from app.modules.returns.models import ReturnReport
from app.modules.returns.services import ReturnReportService
from app.utils.decorators import store_required

bp = Blueprint('returns', __name__, 
               url_prefix='/returns',
               template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

@bp.route('/')
@login_required
def index():
    """Returns report index page."""
    return render_template('returns/index.html')

@bp.route('/report')
@store_required
def return_report():
    """Render the returns report page."""
    template_path = os.path.join('returns', 'return_report.html')
    return render_template(template_path)

@bp.route('/upload', methods=['POST'])
@login_required
def upload():
    """Upload returns report."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Process returns report
    return jsonify({'message': 'File uploaded successfully'}), 200

@bp.route('/process-csv', methods=['POST'])
@login_required
@store_required
def process_csv():
    """Returns report CSV processing endpoint."""
    try:
        # Get DataFrame from request
        df = pd.DataFrame(request.json['data'])
        
        # Process CSV
        processor = ReturnCSVProcessor()
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

@bp.route('/data')
@store_required
def get_return_data():
    """Get return data based on filters."""
    try:
        # Get filter parameters
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        asin = request.args.get('asin', type=str)
        return_reason = request.args.get('return_reason', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        # Get data from service
        service = ReturnReportService()
        data = service.get_return_data(
            store_id=store_id,
            start_date=start_date,
            end_date=end_date,
            asin=asin,
            return_reason=return_reason
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
        service = ReturnReportService()
        asins = service.get_asins(store_id)
        return jsonify(asins)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/return-reasons')
@store_required
def get_return_reasons():
    """Get list of return reasons for the store."""
    try:
        store_id = request.args.get('store_id', type=int)
        service = ReturnReportService()
        reasons = service.get_return_reasons(store_id)
        return jsonify(reasons)
    except Exception as e:
        return jsonify({'error': 'Internal server error'}), 500

@bp.route('/trends')
@store_required
def get_trends():
    """Get return trends data."""
    try:
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date', type=str)
        end_date = request.args.get('end_date', type=str)
        asin = request.args.get('asin', type=str)

        # Validate dates
        start_date = datetime.strptime(start_date, '%Y-%m-%d') if start_date else None
        end_date = datetime.strptime(end_date, '%Y-%m-%d') if end_date else None

        service = ReturnReportService()
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
