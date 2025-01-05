from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Store

bp = Blueprint('analytics', __name__)

@bp.route('/seasonal')
@login_required
def seasonal_analytics():
    """Render the seasonal analytics dashboard."""
    store = Store.query.filter_by(user_id=current_user.id).first()
    if not store:
        return render_template('analytics/seasonal.html', store_id=None)
    return render_template('analytics/seasonal.html', store_id=store.id)

@bp.route('/upload-csv')
@login_required
def upload_csv():
    """Render the CSV upload page."""
    report_types = [
        'business_report',
        'inventory_report',
        'advertising_report',
        'return_report'
    ]
    return render_template('csv/upload.html', report_types=report_types)

@bp.route('/api/v1/analytics/seasonal/<int:store_id>')
@login_required
def get_seasonal_analytics(store_id):
    """Get seasonal analytics data."""
    try:
        # Verify store ownership
        store = Store.query.filter_by(id=store_id, user_id=current_user.id).first()
        if not store:
            return jsonify({'error': 'Store not found'}), 404

        # Get season type from query params
        season_type = request.args.get('season_type', 'monthly')
        
        # Return sample data based on season type
        if season_type == 'monthly':
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            values = [1000, 1200, 1100, 1300, 1400, 1600, 1800, 1700, 1900, 2100, 2500, 3000]
        elif season_type == 'quarterly':
            labels = ['Q1', 'Q2', 'Q3', 'Q4']
            values = [3300, 4300, 5400, 7600]
        else:  # weekly
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4']
            values = [500, 600, 700, 800]

        return jsonify({
            'revenue_trend': {
                'labels': labels,
                'values': values
            }
        })

    except Exception as e:
        print(f"Error in get_seasonal_analytics: {str(e)}")
        return jsonify({
            'revenue_trend': {
                'labels': [],
                'values': []
            }
        })

@bp.route('/api/v1/analytics/peaks/<int:store_id>')
@login_required
def get_peak_periods(store_id):
    """Get peak sales periods."""
    try:
        # Verify store ownership
        store = Store.query.filter_by(id=store_id, user_id=current_user.id).first()
        if not store:
            return jsonify({'error': 'Store not found'}), 404

        # Return sample data
        return jsonify({
            'labels': ['Black Friday', 'Christmas', 'Prime Day', "Valentine's"],
            'values': [5000, 4500, 3500, 2000]
        })

    except Exception as e:
        print(f"Error in get_peak_periods: {str(e)}")
        return jsonify({
            'labels': [],
            'values': []
        })

@bp.route('/api/v1/analytics/special-periods/<int:store_id>')
@login_required
def get_special_periods(store_id):
    """Get special period comparisons."""
    try:
        # Verify store ownership
        store = Store.query.filter_by(id=store_id, user_id=current_user.id).first()
        if not store:
            return jsonify({'error': 'Store not found'}), 404

        # Return sample data
        return jsonify({
            'labels': ['Revenue', 'Orders', 'Average Order Value', 'Customer Satisfaction', 'Return Rate'],
            'values': [90, 85, 88, 92, 95]
        })

    except Exception as e:
        print(f"Error in get_special_periods: {str(e)}")
        return jsonify({
            'labels': [],
            'values': []
        })

@bp.route('/test-data')
@login_required
def create_test_data():
    """Create test data for the current user."""
    # Check if user already has a store
    store = Store.query.filter_by(user_id=current_user.id).first()
    
    if not store:
        # Create a new store
        store = Store(
            name="Test Store",
            region="US",
            user_id=current_user.id
        )
        db.session.add(store)
        db.session.commit()
        
        return jsonify({
            'message': 'Test store created successfully',
            'store_id': store.id
        })
    
    return jsonify({
        'message': 'Test store already exists',
        'store_id': store.id
    })
