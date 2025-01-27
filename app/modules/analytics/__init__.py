from flask import Blueprint

bp = Blueprint('analytics', __name__, 
               url_prefix='/analytics',
               template_folder='templates')

from . import routes  # Import routes after blueprint creation 