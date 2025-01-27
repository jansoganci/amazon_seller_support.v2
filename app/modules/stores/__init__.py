from flask import Blueprint

bp = Blueprint('stores', __name__, 
               url_prefix='/stores',
               template_folder='templates')

from . import routes  # Import routes after blueprint creation 