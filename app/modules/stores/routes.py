from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app import db
from app.modules.stores.models import Store
from . import bp

@bp.route('/')
@login_required
def index():
    stores = Store.query.filter_by(user_id=current_user.id).all()
    return render_template('stores/stores.html', stores=stores)

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        name = request.form.get('name')
        marketplace = request.form.get('marketplace')
        
        if not name or not marketplace:
            flash('Please fill in all required fields.', 'error')
            return render_template('stores/create_store.html')
        
        try:
            store = Store(
                name=name,
                marketplace=marketplace,
                user_id=current_user.id
            )
            db.session.add(store)
            db.session.commit()
            
            print(f"Store created with ID: {store.id}")  # Debug log
            
            # Set as active store
            current_user.active_store_id = store.id
            db.session.commit()
            
            print(f"Active store ID set to: {current_user.active_store_id}")  # Debug log
            
            flash('Store created successfully!', 'success')
            return redirect(url_for('dashboard.index'))
        except Exception as e:
            print(f"Error creating store: {str(e)}")  # Debug log
            db.session.rollback()
            flash('An error occurred while creating the store.', 'error')
            return render_template('stores/create_store.html')
    
    return render_template('stores/create_store.html')

@bp.route('/set-active/<int:store_id>')
@login_required
def set_active(store_id):
    """Set active store."""
    store = Store.query.filter_by(id=store_id, user_id=current_user.id).first()
    if not store:
        flash('Store not found.', 'error')
        return redirect(url_for('stores.index'))
    
    print(f"Setting active store ID to: {store.id}")  # Debug log
    current_user.active_store_id = store.id
    db.session.commit()
    print(f"Active store ID is now: {current_user.active_store_id}")  # Debug log
    
    flash('Active store updated successfully!', 'success')
    return redirect(url_for('dashboard.index')) 