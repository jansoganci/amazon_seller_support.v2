import os
import sys
import pytest
from app import create_app, db
from flask_login import login_user

# Ana dizini Python yoluna ekle
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    app = create_app('testing')
    
    # Test veritabanı ayarları
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['LOGIN_DISABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    # Test için upload klasörü
    test_upload_folder = os.path.join(os.path.dirname(__file__), 'test_uploads')
    if not os.path.exists(test_upload_folder):
        os.makedirs(test_upload_folder)
    app.config['UPLOAD_FOLDER'] = test_upload_folder
    
    # Context
    ctx = app.app_context()
    ctx.push()
    
    # Test veritabanını oluştur
    db.create_all()
    
    yield app
    
    # Temizlik
    db.session.remove()
    db.drop_all()
    ctx.pop()
    
@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
