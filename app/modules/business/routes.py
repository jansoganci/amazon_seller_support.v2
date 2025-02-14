"""Business routes."""

from datetime import datetime, timedelta
from typing import Optional
from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for, current_app, send_file
from flask_login import login_required, current_user
from app.modules.stores.models import Store
from app.modules.business.models import BusinessReport
from app.utils.decorators import store_required
from app.modules.business.services import BusinessReportService, BusinessAnalytics
from app.modules.business.metrics import BUSINESS_METRICS
from app.core.metrics.engine import metric_engine
import logging

bp = Blueprint('business', __name__, 
              url_prefix='/business',
              template_folder='templates')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)



@bp.route('/')
@login_required
@store_required
def index():
    """Business report index page."""
    return render_template('business/index.html')

@bp.route('/api/trends')
@login_required
@store_required
def get_trends():
    """Get business trend data.
    
    This endpoint provides trend analysis for business metrics over a specified time period.
    Supports optional category filtering and configurable time ranges.
    
    Query Parameters:
        days (int): Number of days to analyze (default: 30, max: 365)
        category_id (int, optional): Category ID to filter by
        
    Returns:
        JSON response containing:
        - success (bool): Indicates if request was successful
        - data (dict): Contains trend data if successful
        - metrics (dict): Contains metric configurations
        - error (str): Error message if unsuccessful
        
    Status Codes:
        200: Success
        400: Invalid parameters
        403: Unauthorized store access
        500: Internal server error
    """
    try:
        # Get date range
        end_date = datetime.now()
        days = request.args.get('days', type=int, default=30)
        
        # Validate days parameter
        if days <= 0 or days > 365:
            logger.warning(f"Invalid days parameter: {days}")
            return jsonify({
                'success': False,
                'error': 'Days parameter must be between 1 and 365'
            }), 400
            
        start_date = end_date - timedelta(days=days)
        
        # Get optional filters
        category_id: Optional[int] = request.args.get('category_id', type=int)
            
        # Authorization check
        if not current_user.has_store_access(current_user.store_id):
            logger.warning(
                f"User {current_user.id} attempted unauthorized access to store {current_user.store_id}"
            )
            return jsonify({
                'success': False,
                'error': 'Unauthorized store access'
            }), 403
            
        # Get trends using analytics service
        service = BusinessReportService(current_user.store_id)
        trends = service.get_trends(
            start_date=start_date,
            end_date=end_date,
            category_id=category_id
        )
        
        logger.info(
            f"Retrieved trends for store {current_user.store_id} "
            f"from {start_date} to {end_date}"
        )
        
        return jsonify({
            'success': True,
            'data': trends,
            'metrics': BUSINESS_METRICS
        })
        
    except ValueError as e:
        logger.warning(f"Invalid parameter in trends request: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
        
    except Exception as e:
        logger.exception("Error retrieving trend data")
        return jsonify({
            'success': False,
            'error': 'An internal error occurred'
        }), 500

@bp.route('/api/categories/comparison')
@login_required
@store_required
def compare_categories():
    """Compare performance across categories."""
    try:
        # Get parameters
        end_date = datetime.now()
        days = int(request.args.get('days', 30))
        start_date = end_date - timedelta(days=days)
        category_ids = request.args.getlist('category_ids[]', type=int)
        
        if not category_ids:
            return jsonify({
                'success': False,
                'error': 'No categories specified'
            }), 400
            
        # Get comparison using analytics service
        service = BusinessReportService(current_user.store_id)
        comparison = service.get_category_comparison(
            start_date,
            end_date,
            category_ids
        )
        
        return jsonify({
            'success': True,
            'data': comparison,
            'metrics': BUSINESS_METRICS
        })
        
    except Exception as e:
        logger.exception("Error comparing categories")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/categories')
@login_required
@store_required
def get_categories():
    """Get available categories."""
    try:
        service = BusinessReportService(current_user.store_id)
        categories = service.get_categories()
        
        return jsonify({
            'success': True,
            'data': categories
        })
        
    except Exception as e:
        logger.exception("Error getting categories")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/api/asins')
@login_required
@store_required
def get_asins():
    """Get available ASINs."""
    try:
        service = BusinessReportService(current_user.store_id)
        asins = service.get_asins()
        
        return jsonify({
            'success': True,
            'data': asins
        })
        
    except Exception as e:
        logger.exception("Error getting ASINs")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@bp.route('/upload', methods=['POST'])
@login_required
@store_required
def upload():
    """Upload business report."""
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # TODO: Process business report
    return jsonify({'message': 'File uploaded successfully'}), 200

@bp.route('/process-csv', methods=['POST'])
@login_required
@store_required
def process_csv():
    """Business raporu CSV işleme endpoint'i."""
    try:
        # DataFrame'i request'ten al
        df = pd.DataFrame(request.json['data'])
        
        # CSV işleme
        processor = BusinessCSVProcessor()
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
        current_app.logger.error(f"CSV işleme hatası: {str(e)}")
        return jsonify({'success': False, 'message': ERROR_MESSAGES['UNKNOWN_ERROR']}), 500

@bp.route('/export', methods=['POST'])
@login_required
@store_required
def export():
    """Business raporu dışa aktarma endpoint'i."""
    try:
        # Request parametrelerini al
        data = request.get_json()
        store_id = data.get('store_id')
        start_date = datetime.strptime(data.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(data.get('end_date'), '%Y-%m-%d')

        # Parametreleri kontrol et
        if not all([store_id, start_date, end_date]):
            return jsonify({'success': False, 'message': ERROR_MESSAGES['MISSING_PARAMS']}), 400

        # Store erişim kontrolü
        if not current_user.has_store_access(store_id):
            return jsonify({'success': False, 'message': ERROR_MESSAGES['NO_STORE_ACCESS']}), 403

        # Verileri dışa aktar
        processor = BusinessCSVProcessor()
        success, message, df = processor.export_data(store_id, start_date, end_date)

        if not success:
            return jsonify({'success': False, 'message': message}), 404

        # CSV dosyası oluştur
        filename = f"business_report_{store_id}_{start_date.date()}_{end_date.date()}.csv"
        filepath = os.path.join(current_app.config['TEMP_FOLDER'], filename)
        df.to_csv(filepath, index=False)

        # Dosyayı gönder ve temizle
        return_data = send_file(
            filepath,
            mimetype='text/csv',
            as_attachment=True,
            download_name=filename
        )
        
        @return_data.call_on_close
        def cleanup():
            """Geçici dosyayı temizle."""
            try:
                os.remove(filepath)
            except Exception as e:
                current_app.logger.error(f"Geçici dosya silme hatası: {str(e)}")

        return return_data

    except Exception as e:
        current_app.logger.error(f"Dışa aktarma hatası: {str(e)}")
        return jsonify({'success': False, 'message': ERROR_MESSAGES['UNKNOWN_ERROR']}), 500

@bp.route('/stats', methods=['GET'])
@login_required
@store_required
def stats():
    """Business raporu istatistikleri endpoint'i."""
    try:
        store_id = request.args.get('store_id', type=int)
        if not store_id:
            return jsonify({'success': False, 'message': ERROR_MESSAGES['MISSING_PARAMS']}), 400

        # Store erişim kontrolü
        if not current_user.has_store_access(store_id):
            return jsonify({'success': False, 'message': ERROR_MESSAGES['NO_STORE_ACCESS']}), 403

        # İstatistikleri hesapla
        processor = BusinessCSVProcessor()
        success, message, df = processor.export_data(
            store_id,
            datetime.now().replace(day=1),  # Ayın başı
            datetime.now()  # Bugün
        )

        if not success:
            return jsonify({'success': False, 'message': message}), 404

        # İstatistikleri hesapla
        stats = {
            'total_sessions': int(df['sessions'].sum()),
            'total_orders': int(df['units_ordered'].sum()),
            'total_sales': float(df['ordered_product_sales'].sum()),
            'avg_conversion_rate': float(df['conversion_rate'].mean()),
            'top_products': df.nlargest(5, 'ordered_product_sales')[
                ['asin', 'title', 'ordered_product_sales']
            ].to_dict('records')
        }

        return jsonify({
            'success': True,
            'stats': stats
        })

    except Exception as e:
        current_app.logger.error(f"İstatistik hesaplama hatası: {str(e)}")
        return jsonify({'success': False, 'message': ERROR_MESSAGES['UNKNOWN_ERROR']}), 500

@bp.route('/revenue-trends')
@login_required
@store_required
def revenue_trends():
    """Revenue trends page."""
    analytics = BusinessAnalytics()
    store_id = 1  # TODO: Get from current user's store
    
    try:
        categories = analytics.get_available_categories(store_id)
        asins = analytics.get_available_asins(store_id)
        return render_template(
            'business/revenue_trends.html',
            store_id=store_id,
            categories=categories,
            asins=asins
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/reports')
@login_required
@store_required
def list_business_reports():
    """List all business reports."""
    try:
        reports = BusinessReport.query.all()
        return render_template(
            'business/reports.html',
            reports=reports
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/dashboard')
@login_required
@store_required
def dashboard():
    """Business dashboard page."""
    try:
        return render_template('business/dashboard.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/business_report')
@login_required
@store_required
def business_report():
    """Render the business report page with initial data."""
    try:
        store_id = current_user.active_store_id
        logger.debug(f"Loading business report for store_id: {store_id}")
        
        if not current_user.has_store_access(store_id):
            logger.warning(f"User {current_user.id} attempted to access store {store_id} without permission")
            flash('You do not have access to this store', 'error')
            return redirect(url_for('dashboard.index'))
            
        # Initialize service
        logger.debug("Initializing BusinessReportService")
        service = BusinessReportService(store_id)
        
        # Get initial data for the last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        logger.debug(f"Fetching trends data from {start_date} to {end_date}")
        initial_data = service.get_trends(
            start_date=start_date,
            end_date=end_date
        )
        
        # Format initial data according to BUSINESS_METRICS
        formatted_data = {}
        for metric_id, metric in BUSINESS_METRICS.items():
            if metric_id in initial_data:
                try:
                    value = initial_data[metric_id]
                    if isinstance(value, (int, float)):
                        numeric_value = float(value)
                    elif isinstance(value, str):
                        # Remove currency symbols, commas and percentage signs
                        clean_value = value.replace('$', '').replace(',', '').replace('%', '')
                        numeric_value = float(clean_value)
                    else:
                        numeric_value = 0.0
                        
                    format_str = metric['visualization']['format']
                    formatted_data[metric_id] = format_str.format(numeric_value)
                except (ValueError, TypeError) as e:
                    # Don't log warning for expected string formats
                    if not any(c in str(value) for c in ['$', ',', '%']):
                        logger.warning(f"Format error for {metric_id}: {str(e)}")
                    formatted_data[metric_id] = str(value) if value else 'N/A'
                
                # Add growth rate if available
                growth_key = f"{metric_id}_growth"
                if growth_key in initial_data:
                    try:
                        growth = initial_data[growth_key]
                        # Convert to float, removing % if present
                        if isinstance(growth, str):
                            growth = float(growth.strip('%').strip())
                        else:
                            growth = float(growth)
                        formatted_data[growth_key] = growth  # Store as float, not string
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Format error for {growth_key}: {str(e)}")
                        formatted_data[growth_key] = 0.0  # Default to 0 for invalid values
        
        logger.debug(f"Formatted data: {formatted_data}")
        
        # Get ASINs for filtering
        logger.debug("Fetching ASINs")
        asins = service.get_asins()
        logger.debug(f"Found {len(asins)} ASINs")
        
        # Get categories for filtering
        logger.debug("Fetching categories")
        categories = service.get_categories()
        logger.debug(f"Found {len(categories)} categories")

        # Structure initial data for frontend
        frontend_data = {
            'metrics': formatted_data,
            'charts': {
                'revenue_chart_data': service.get_revenue_chart_data(start_date, end_date),
                'metrics_chart_data': service.get_metrics_chart_data(start_date, end_date),
                'category_chart_data': service.get_category_chart_data(start_date, end_date),
                'alert_chart_data': service.get_alert_chart_data(start_date, end_date)
            }
        }

        return render_template(
            'business/business_report.html',
            store_id=store_id,
            initial_data=frontend_data,
            categories=categories,
            asins=asins,
            metrics=BUSINESS_METRICS
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in business report: {str(e)}")
        flash(str(e), 'warning')
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        logger.exception(f"Error rendering business report: {str(e)}")
        error_msg = 'An error occurred while loading the report.'
        if current_app.debug:
            error_msg += f' Details: {str(e)}'
        flash(error_msg, 'error')
        
        # Still show the report with default values
        return render_template(
            'business/business_report.html',
            store_id=store_id,
            initial_data={},  # Empty data will use defaults
            asins=service.get_asins() if 'service' in locals() else [],
            metrics=BUSINESS_METRICS,
            error_occurred=True  # Template can show error state
        )

@bp.route('/api/report-data')
@login_required
@store_required
def get_report_data():
    """Get report data for the specified store."""
    try:
        store_id = current_user.active_store_id
        if not current_user.has_store_access(store_id):
            return jsonify({'error': 'No access to this store'}), 403
            
        service = BusinessReportService(store_id)
        
        # Parse dates
        try:
            start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
            end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
            
        category = request.args.get('category')
        subcategory = request.args.get('subcategory')
        asin = request.args.get('asin')
        group_by = request.args.get('group_by', 'daily')
        
        if not all([start_date, end_date]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Get metrics and chart data
        try:
            metrics = service.get_trends(start_date, end_date)
            charts = {
                'revenue_chart_data': service.get_revenue_chart_data(start_date, end_date),
                'metrics_chart_data': service.get_metrics_chart_data(start_date, end_date),
                'category_chart_data': service.get_category_chart_data(start_date, end_date),
                'alert_chart_data': service.get_alert_chart_data(start_date, end_date)
            }
            
            return jsonify({
                'success': True,
                'metrics': metrics,
                'charts': charts
            })
            
        except Exception as e:
            logger.error(f"Error getting report data: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Error processing report data'
            }), 500
            
    except Exception as e:
        logger.exception(f"Error in report data endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500
            
        data = service.get_report_data(
            start_date=start_date,
            end_date=end_date,
            category=category,
            asin=asin
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/api/chart-data/<string:period>')
@login_required
@store_required
def get_chart_data(period):
    """Get chart data for the specified store and period."""
    try:
        store_id = current_user.active_store_id
        if not current_user.has_store_access(store_id):
            return jsonify({'error': 'No access to this store'}), 403
            
        service = BusinessReportService(store_id)
        
        # Calculate date range based on period
        end_date = datetime.now()
        if period == 'daily':
            start_date = end_date - timedelta(days=30)
        elif period == 'weekly':
            start_date = end_date - timedelta(weeks=12)
        elif period == 'monthly':
            start_date = end_date - timedelta(days=365)
        else:
            return jsonify({'error': 'Invalid period'}), 400
            
        data = service.get_chart_data(
            start_date=start_date,
            end_date=end_date,
            period=period
        )
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/data')
@login_required
@store_required
def get_filtered_data():
    """Get filtered business data."""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'date')  # Default to 'date'
        category = request.args.get('category')
        asin = request.args.get('asin')

        if not start_date or not end_date:
            return jsonify({'error': 'Start date and end date are required'}), 400

        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        store_id = current_user.active_store_id
        service = BusinessReportService(store_id)
        try:
            data = service.get_filtered_data(
                start_date=start_date,
                end_date=end_date,
                group_by=group_by,
                category=category,
                asin=asin
            )
            return jsonify(data)
        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        logger.error(f"Error fetching filtered data: {str(e)}")
        return jsonify({'error': 'An error occurred while fetching data'}), 500
