"""Advertising module."""

from flask import Blueprint

bp = Blueprint('advertising', __name__, 
              url_prefix='/advertising',
              template_folder='templates')

from . import routes  # Import routes to register them with the blueprint 