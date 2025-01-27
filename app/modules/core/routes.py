"""Core routes."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('core', __name__)

@bp.route('/')
@login_required
def index():
    """Core index page."""
    return render_template('core/index.html')

@bp.route('/upload')
@login_required
def upload():
    """Render upload page."""
    if not current_user.active_store_id:
        return redirect(url_for('stores.index'))
    return render_template('core/upload.html') 