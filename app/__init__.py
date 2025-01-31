"""Flask application factory."""

import os
from flask import Flask, redirect, url_for, jsonify, request
from flask_login import current_user, login_manager
from jinja2 import ChoiceLoader, FileSystemLoader

from app.extensions import db, migrate, login_manager, limiter
from app.modules.auth.models import User

def create_app(config_object=None):
    """Create Flask application."""
    app = Flask(__name__)

    # Configure template loader to include both app/templates and app/core/templates
    template_dirs = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core/templates')
    ]
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(template_dirs),
        app.jinja_loader
    ])

    if config_object:
        if isinstance(config_object, dict):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)
    else:
        app.config['SECRET_KEY'] = 'dev'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'instance', 'amazon_seller.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size

    # Upload folder config
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'uploads')
    
    # Create upload folders if they don't exist
    upload_folders = ['temp', 'processed']
    for folder in upload_folders:
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], folder)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    @login_manager.unauthorized_handler
    def unauthorized():
        if request.path.startswith('/api/'):
            return jsonify({"error": "Unauthorized access"}), 401
        return redirect(url_for('auth.login'))

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID."""
        return User.query.get(int(user_id))

    # Import models
    from app.modules.business.models import BusinessReport
    from app.modules.stores.models import Store
    from app.modules.category.models.category import Category, ASINCategory

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Register blueprints and extensions
    from app.modules.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.modules.business.routes import bp as business_bp
    app.register_blueprint(business_bp)

    from app.modules.advertising.routes import bp as advertising_bp
    app.register_blueprint(advertising_bp)

    from app.modules.inventory.routes import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    from app.modules.returns.routes import bp as returns_bp
    app.register_blueprint(returns_bp)

    from app.modules.dashboard.routes import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    from app.modules.stores.routes import bp as stores_bp
    app.register_blueprint(stores_bp)

    from app.modules.upload_csv.routes import bp as upload_csv_bp
    app.register_blueprint(upload_csv_bp)

    from app.modules.uploaded_data.routes import bp as uploaded_data_bp
    app.register_blueprint(uploaded_data_bp)

    from app.modules.analytics.routes import bp as analytics_bp
    app.register_blueprint(analytics_bp)

    from app.modules.category.routes import bp as category_bp
    app.register_blueprint(category_bp)

    from app.modules.admin.routes import bp as admin_bp
    app.register_blueprint(admin_bp)

    from app.modules.settings.routes import bp as settings_bp
    app.register_blueprint(settings_bp)

    return app

# Export db and migrate objects
__all__ = ['create_app', 'db', 'migrate', 'login_manager']
