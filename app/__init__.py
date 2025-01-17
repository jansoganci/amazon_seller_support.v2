from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
import os
from datetime import timedelta
import logging

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app(config_name=None):
    app = Flask(__name__)
    
    # Logging ayarları
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Konfigürasyon
    if config_name == 'testing':
        app.config['SECRET_KEY'] = 'test'
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_uploads')
    else:
        app.config['SECRET_KEY'] = 'dev'  # Geliştirme için geçici key
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=31)
        app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=31)
        app.config['SESSION_PROTECTION'] = 'strong'
    
    # Upload klasörü oluştur
    if not os.path.exists(app.config.get('UPLOAD_FOLDER', 'uploads')):
        os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'))
    
    # Eklentilerin başlatılması
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    login_manager.session_protection = 'strong'
    
    # Shell context'i için login_manager'ı hazırla
    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'User': User,
            'Store': Store,
            'login_manager': login_manager
        }
    
    with app.app_context():
        # Model importları
        from app.models.user import User
        from app.models.store import Store
        from app.models.csv_file import CSVFile
        from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport
        
        # Blueprint'lerin kaydedilmesi
        from app.routes import main, auth, csv, settings, analytics
        app.register_blueprint(auth.bp)
        app.register_blueprint(main.bp)
        app.register_blueprint(csv.bp)
        app.register_blueprint(settings.bp)
        app.register_blueprint(analytics.bp, url_prefix='/analytics')
    
    return app
