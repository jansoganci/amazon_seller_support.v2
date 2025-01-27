"""Inventory module initialization."""

from flask import Blueprint

bp = Blueprint('inventory', __name__, 
              url_prefix='/inventory',
              template_folder='templates')

def init_app(app):
    """Initialize inventory module."""
    from . import routes  # Import routes here to avoid circular imports
    app.register_blueprint(bp)