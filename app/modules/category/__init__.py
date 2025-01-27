"""Kategori modülü."""

from flask import Blueprint

bp = Blueprint('category', __name__)

from . import cli

def init_app(app):
    """Kategori modülünü başlat."""
    app.register_blueprint(bp)
    app.cli.add_command(cli.kategori)
