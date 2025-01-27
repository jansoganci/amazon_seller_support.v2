"""Uploaded data routes."""

from flask import render_template
from flask_login import login_required, current_user
from app.modules.business.models import BusinessReport
from app.modules.inventory.models import InventoryReport
from app.modules.advertising.models import AdvertisingReport
from app.modules.returns.models import ReturnReport
from app.utils.constants import get_category_by_asin
from app import db
from . import bp

@bp.route('/')
@login_required
def index():
    """Uploaded data index page."""
    return render_template('uploaded_data/uploaded_data.html')

@bp.route('/business-reports')
@login_required
def business_reports():
    """Display business reports."""
    reports = BusinessReport.query.filter_by(store_id=current_user.active_store_id).order_by(BusinessReport.date.desc()).all()
    return render_template('uploaded_data/business_report_data.html', reports=reports, get_category=get_category_by_asin)

@bp.route('/advertising-reports')
@login_required
def advertising_reports():
    """Display advertising reports."""
    reports = AdvertisingReport.query.filter_by(store_id=current_user.active_store_id).order_by(AdvertisingReport.date.desc()).all()
    return render_template('uploaded_data/advertising_report_data.html', reports=reports, get_category=get_category_by_asin)

@bp.route('/inventory-reports')
@login_required
def inventory_reports():
    """Display inventory reports."""
    reports = InventoryReport.query.filter_by(store_id=current_user.active_store_id).order_by(InventoryReport.date.desc()).all()
    return render_template('uploaded_data/inventory_report_data.html', reports=reports, get_category=get_category_by_asin)

@bp.route('/return-reports')
@login_required
def return_reports():
    """Display return reports."""
    reports = ReturnReport.query\
        .filter_by(store_id=current_user.active_store_id)\
        .order_by(ReturnReport.return_date.desc())\
        .all()
    return render_template('uploaded_data/return_report_data.html', reports=reports, get_category=get_category_by_asin)