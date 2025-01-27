"""Custom decorators."""

from functools import wraps
from flask import abort, request, redirect, url_for, flash
from flask_login import current_user

def store_required(f):
    """Store erişim kontrolü için decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Önce route'dan veya query string'den store_id'yi kontrol et
        store_id = kwargs.get('store_id') or request.args.get('store_id') or request.form.get('store_id')
        
        # Eğer store_id yoksa active_store_id'yi kontrol et
        if not store_id and hasattr(current_user, 'active_store_id'):
            store_id = current_user.active_store_id
            
        if not store_id:
            flash('Please select a store first.', 'warning')
            return redirect(url_for('stores.index'))
            
        if not current_user.has_store_access(store_id):
            abort(403, description="You don't have access to this store")
            
        return f(*args, **kwargs)
    return decorated_function 