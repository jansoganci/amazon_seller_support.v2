"""Upload CSV module."""

from flask import Blueprint
from dataclasses import dataclass

bp = Blueprint('upload_csv', __name__, 
               url_prefix='/upload',
               template_folder='templates')

@dataclass
class CSVFileData:
    """CSV file data class for file uploads."""
    filename: str
    content: bytes
    mimetype: str

def init_app(app):
    """Initialize upload_csv module."""
    from . import routes  # Import routes here to avoid circular imports
    app.register_blueprint(bp)

__all__ = ['bp', 'init_app', 'CSVFileData']