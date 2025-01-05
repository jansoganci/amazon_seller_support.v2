from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # Konfigürasyon
    app.config['SECRET_KEY'] = 'dev'  # Geliştirme için geçici key
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10MB max-limit
    
    # Eklentilerin başlatılması
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    login_manager.login_view = 'auth.login'
    
    with app.app_context():
        # Model importları
        from app.models.user import User
        from app.models.store import Store
        from app.models.csv_file import CSVFile
        from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport
        
        # Blueprint'lerin kaydedilmesi
        from app.routes import main, auth, csv
        app.register_blueprint(main.bp)
        app.register_blueprint(auth.bp)
        app.register_blueprint(csv.bp)
        
        # Veritabanı oluşturma
        db.create_all()
    
    return app
