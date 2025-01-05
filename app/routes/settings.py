from flask import Blueprint, render_template, request, flash, redirect, url_for, make_response
from flask_login import login_required, current_user
from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash

bp = Blueprint('settings', __name__)

@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Kullanıcı ayarları sayfası"""
    if request.method == 'POST':
        # Profil güncelleme
        if 'update_profile' in request.form:
            name = request.form.get('name')
            email = request.form.get('email')
            
            if name:
                current_user.name = name
            if email and email != current_user.email:
                # Email değişikliği için ek doğrulama eklenebilir
                if User.query.filter_by(email=email).first():
                    flash('Bu e-posta adresi zaten kullanımda', 'danger')
                    return redirect(url_for('settings.settings'))
                current_user.email = email
            
            db.session.commit()
            flash('Profil bilgileri güncellendi', 'success')
            
        # Şifre değiştirme
        elif 'update_password' in request.form:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            confirm_password = request.form.get('confirm_password')
            
            if not current_user.check_password(current_password):
                flash('Mevcut şifre yanlış', 'danger')
            elif new_password != confirm_password:
                flash('Yeni şifreler eşleşmiyor', 'danger')
            else:
                current_user.password_hash = generate_password_hash(new_password)
                db.session.commit()
                flash('Şifre başarıyla değiştirildi', 'success')
                
        # Uygulama ayarları
        elif 'update_preferences' in request.form:
            language = request.form.get('language', 'tr')
            currency = request.form.get('currency', 'TRY')
            theme = request.form.get('theme', 'light')
            
            current_user.preferences = {
                'language': language,
                'currency': currency,
                'theme': theme,
                'notifications': {
                    'email': request.form.get('email_notifications') == 'on',
                    'browser': request.form.get('browser_notifications') == 'on'
                }
            }
            db.session.commit()
            flash('Tercihler güncellendi', 'success')
            
            # Tema değişikliği yapıldıysa, tarayıcı temasını güncelle
            response = make_response(redirect(url_for('settings.settings')))
            response.set_cookie('theme', theme)
            return response
            
        return redirect(url_for('settings.settings'))
        
    return render_template('settings/settings.html')
