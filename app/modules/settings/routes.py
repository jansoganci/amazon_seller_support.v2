"""Settings module routes."""

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from . import bp

@bp.route('/')
@login_required
def index():
    """Render settings page."""
    # Eğer kullanıcının preferences'ı None ise, varsayılan değerleri ayarla
    if current_user.preferences is None:
        current_user.preferences = {
            'language': 'en',
            'currency': 'USD',
            'theme': 'light',
            'notifications': {
                'email': True,
                'browser': True
            }
        }
        db.session.commit()
    
    return render_template('settings/settings.html')

@bp.route('/update', methods=['POST'])
@login_required
def update():
    """Update user settings."""
    if 'update_profile' in request.form:
        current_user.name = request.form.get('name')
        current_user.email = request.form.get('email')
        flash('Profile updated successfully!', 'success')
    
    elif 'update_password' in request.form:
        if current_user.check_password(request.form.get('current_password')):
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if new_password == confirm_password:
                current_user.set_password(new_password)
                flash('Password updated successfully!', 'success')
            else:
                flash('New passwords do not match!', 'error')
        else:
            flash('Current password is incorrect!', 'error')
    
    elif 'update_preferences' in request.form:
        current_user.preferences = {
            'language': request.form.get('language'),
            'currency': request.form.get('currency'),
            'theme': request.form.get('theme'),
            'notifications': {
                'email': 'email_notifications' in request.form,
                'browser': 'browser_notifications' in request.form
            }
        }
        flash('Preferences updated successfully!', 'success')
    
    db.session.commit()
    return redirect(url_for('settings.index')) 