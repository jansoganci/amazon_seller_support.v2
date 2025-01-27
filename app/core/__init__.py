"""Core module."""

from flask import Blueprint

bp = Blueprint('core', __name__)

from . import routes  # Import routes to register them with the blueprint
