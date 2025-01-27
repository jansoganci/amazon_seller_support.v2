from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
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
        
        # Otomatik giriș yap ve dashboard'a yönlendir
        login_user(user)
        flash('Registration successful!', 'success')
        return redirect(url_for('main.dashboard'))
        
    return render_template('auth/register.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Handle both form data and JSON
        if request.is_json:
            data = request.get_json()
            is_json = True
        else:
            data = request.form
            is_json = False
            
        if not data:
            if is_json:
                return {'error': 'No data provided'}, 400
            flash('Please fill all fields', 'error')
            return redirect(url_for('auth.login'))
            
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember', False)
        
        if not email or not password:
            if is_json:
                return {'error': 'Email and password are required'}, 400
            flash('Please fill all fields', 'error')
            return redirect(url_for('auth.login'))
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            # Make session permanent
            session.permanent = True
            # Login with remember option
            login_user(user, remember=remember)
            # Add user_id to session
            session['user_id'] = user.id
            
            if is_json:
                return {'message': 'Login successful', 'redirect': url_for('dashboard.index')}, 200
                
            return redirect(url_for('dashboard.index'))
            
        if is_json:
            return {'error': 'Invalid email or password'}, 401
            
        flash('Invalid email or password', 'error')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
