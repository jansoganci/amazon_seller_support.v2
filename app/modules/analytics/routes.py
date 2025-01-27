"""Analytics module routes."""

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from . import bp

@bp.route('/')
@login_required
def index():
    """Render analytics dashboard."""
    if not current_user.active_store_id:
        flash('Please select a store first', 'warning')
        return redirect(url_for('dashboard.index'))
    return render_template('analytics/analytics.html', active_store_id=current_user.active_store_id)