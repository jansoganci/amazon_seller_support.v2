"""Category module for Amazon Seller Support."""

from flask import Blueprint

bp = Blueprint('category', __name__, url_prefix='/api/categories')

from . import routes
from . import cli

def init_app(app: object) -> None:
    """Initialize category module.
    
    Args:
        app: Flask application instance.
    """
    app.register_blueprint(bp)
    app.cli.add_command(cli.category)
