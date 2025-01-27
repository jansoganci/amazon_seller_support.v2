from flask import Blueprint

bp = Blueprint('uploaded_data', __name__, 
               url_prefix='/uploaded-data',
               template_folder='templates')

from . import routes  # Import routes after blueprint creation 