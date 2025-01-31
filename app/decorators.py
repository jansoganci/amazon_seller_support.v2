"""Decorators for the application."""

from functools import wraps
from flask import jsonify
from flask_login import current_user
from werkzeug.exceptions import Unauthorized, Forbidden

def admin_required(f):
    """Require admin role for route."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({"error": "Authentication required"}), 401
        if current_user.role != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        return f(*args, **kwargs)
    return decorated_function
