from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from app.models.store import Store
from werkzeug.security import generate_password_hash

bp = Blueprint('settings', __name__, url_prefix='/settings', template_folder='templates')

@bp.route('/')
@login_required
def index():
    # Initialize preferences if not exists
    if not hasattr(current_user, 'preferences'):
        current_user.preferences = {
            'language': 'en',
            'currency': 'USD',
            'theme': 'light',
            'notifications': {
                'email': False,
                'browser': False
            }
        }
        db.session.commit()
    return render_template('settings/settings.html')

@bp.route('/update', methods=['POST'])
@login_required
def update():
    if 'update_profile' in request.form:
        name = request.form.get('name')
        email = request.form.get('email')
        
        if name and email:
            current_user.name = name
            current_user.email = email
            db.session.commit()
            flash('Profile updated successfully!', 'success')
    
    elif 'update_password' in request.form:
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        if current_password and new_password and confirm_password:
            if current_user.check_password(current_password):
                if new_password == confirm_password:
                    current_user.set_password(new_password)
                    db.session.commit()
                    flash('Password updated successfully!', 'success')
                else:
                    flash('New passwords do not match!', 'error')
            else:
                flash('Current password is incorrect!', 'error')
    
    elif 'update_preferences' in request.form:
        language = request.form.get('language')
        currency = request.form.get('currency')
        theme = request.form.get('theme')
        email_notifications = request.form.get('email_notifications') == 'on'
        browser_notifications = request.form.get('browser_notifications') == 'on'
        
        preferences = current_user.preferences
        preferences['language'] = language
        preferences['currency'] = currency
        preferences['theme'] = theme
        preferences['notifications']['email'] = email_notifications
        preferences['notifications']['browser'] = browser_notifications
        
        current_user.preferences = preferences
        db.session.commit()
        flash('Preferences updated successfully!', 'success')
    
    return redirect(url_for('settings.index'))

@bp.route('/stores/create', methods=['GET', 'POST'])
@login_required
def create_store():
    """Create new store page"""
    if request.method == 'POST':
        name = request.form.get('name')
        marketplace = request.form.get('marketplace')
        
        if not name or not marketplace:
            flash('Please fill in all fields', 'danger')
            return redirect(url_for('settings.create_store'))
            
        store = Store(
            name=name,
            marketplace=marketplace,
            user_id=current_user.id
        )
        
        db.session.add(store)
        db.session.commit()
        flash('Store created successfully', 'success')
        return redirect(url_for('settings.list_stores'))
        
    return render_template('settings/create_store.html')

@bp.route('/stores', methods=['GET'])
@login_required
def list_stores():
    """List user's stores"""
    stores = Store.query.filter_by(user_id=current_user.id).all()
    return render_template('settings/stores.html', stores=stores) 