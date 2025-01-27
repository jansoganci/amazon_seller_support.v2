"""Returns module initialization."""

from flask import Blueprint
import os

# Get the directory containing this file
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

bp = Blueprint('returns', __name__, 
               url_prefix='/returns',
               template_folder=template_dir)

def init_app(app):
    """Initialize returns module."""
    from . import routes  # Import routes here to avoid circular imports
    
    # Register blueprint
    app.register_blueprint(bp)

__all__ = ['bp', 'init_app']