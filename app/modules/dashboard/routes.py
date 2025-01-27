"""Dashboard module routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from app.modules.business.models import BusinessReport
from . import bp

@bp.route('/')
@login_required
def index():
    """Render dashboard page."""
    print(f"Current user: {current_user.username}")  # Debug log
    print(f"Active store ID: {current_user.active_store_id}")  # Debug log
    
    # Kullanıcının aktif mağazası yoksa, mağaza seçme sayfasına yönlendir
    if not current_user.active_store_id:
        print("No active store found!")  # Debug log
        flash('Please select or create a store first.', 'info')
        return redirect(url_for('stores.index'))
    
    print(f"Rendering dashboard for store ID: {current_user.active_store_id}")  # Debug log
    
    # Get business reports for the active store
    business_reports = BusinessReport.query.filter_by(
        store_id=current_user.active_store_id
    ).order_by(BusinessReport.date.desc()).limit(10).all()
    
    return render_template('dashboard/dashboard.html', business_reports=business_reports)