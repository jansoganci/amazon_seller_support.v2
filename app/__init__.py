"""Flask application factory."""

import os
from flask import Flask, redirect, url_for
from flask_login import current_user
from app.extensions import db, migrate, login_manager, limiter
from jinja2 import ChoiceLoader, FileSystemLoader

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
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amazon_seller.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max file size
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Import models
    from app.models import User
    from app.modules.business.models import BusinessReport
    from app.modules.category.models.category import Category, ASINCategory

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard.index'))
        return redirect(url_for('auth.login'))

    # Create upload folder if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Register blueprints and extensions
    from app.modules.business.routes import bp as business_bp
    app.register_blueprint(business_bp)

    # Register advertising blueprint
    from app.modules.advertising.routes import bp as advertising_bp
    app.register_blueprint(advertising_bp)

    # Register inventory blueprint
    from app.modules.inventory.routes import bp as inventory_bp
    app.register_blueprint(inventory_bp)

    # Register returns blueprint
    from app.modules.returns.routes import bp as returns_bp
    app.register_blueprint(returns_bp)

    # Register dashboard blueprint
    from app.modules.dashboard.routes import bp as dashboard_bp
    app.register_blueprint(dashboard_bp)

    # Register stores blueprint
    from app.modules.stores.routes import bp as stores_bp
    app.register_blueprint(stores_bp)

    # Register upload_csv blueprint
    from app.modules.upload_csv.routes import bp as upload_csv_bp
    app.register_blueprint(upload_csv_bp)

    # Register uploaded_data blueprint
    from app.modules.uploaded_data.routes import bp as uploaded_data_bp
    app.register_blueprint(uploaded_data_bp)

    # Register settings blueprint
    from app.modules.settings.routes import bp as settings_bp
    app.register_blueprint(settings_bp)

    # Register analytics blueprint
    from app.modules.analytics.routes import bp as analytics_bp
    app.register_blueprint(analytics_bp)

    # Register category blueprint
    from app.modules.category.routes import bp as category_bp
    app.register_blueprint(category_bp)

    # Register auth blueprint
    from app.modules.auth.routes import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app

# Export db and migrate objects
__all__ = ['create_app', 'db', 'migrate', 'login_manager']
