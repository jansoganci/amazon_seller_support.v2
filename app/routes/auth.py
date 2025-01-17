from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Validation
        if not email or not password or not name:
            flash('Please fill all fields', 'error')
            return redirect(url_for('auth.register'))
            
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return redirect(url_for('auth.register'))
            
        # Create new user
        user = User(name=name, email=email, password=password)
        
        db.session.add(user)
        db.session.commit()
        
        # Otomatik giriş yap ve dashboard'a yönlendir
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember', False)
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Session'ı kalıcı yap
            session.permanent = True
            # Kullanıcıyı hatırla seçeneği ile giriş yap
            login_user(user, remember=remember)
            # Login sonrası session'a user_id ekle
            session['user_id'] = user.id
            session['_fresh'] = True
            
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('main.dashboard'))
        else:
            flash('Invalid email or password', 'error')
            
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
