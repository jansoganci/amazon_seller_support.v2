"""Business module initialization."""

from flask import Blueprint
import os

# Get the directory containing this file
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

bp = Blueprint('business', __name__, 
              url_prefix='/business',
              template_folder=template_dir)

def init_app(app):
    """Initialize business module."""
    from . import routes  # Import routes here to avoid circular imports
    from .metrics import register_metrics
    
    # Register business metrics
    register_metrics()
    
    # Register blueprint
    app.register_blueprint(bp)

__all__ = ['bp', 'init_app']
