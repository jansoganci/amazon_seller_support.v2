import os
import sys
import pytest
from app import create_app, db
from flask_login import login_user, current_user
from werkzeug.security import generate_password_hash
from app.models.user import User
from app.models.store import Store

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
    
    # Test kullanıcısını oluştur
    test_user = User(
        name='Test User',
        email='test@example.com',
        password='test123'
    )
    db.session.add(test_user)
    db.session.commit()
    
    # Test mağazasını ekle
    test_store = Store(id=1, name='Test Store', region='US', user_id=test_user.id)
    db.session.add(test_store)
    db.session.commit()
    
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

@pytest.fixture
def auth(client, app):
    class AuthActions:
        def __init__(self, client):
            self._client = client
            self._app = app

        def login(self, email='test@example.com', password='test123'):
            with self._app.test_request_context():
                user = User.query.filter_by(email=email).first()
                if user and user.check_password(password):
                    login_user(user)
                    
            return self._client.post(
                '/auth/login',
                data={'email': email, 'password': password},
                follow_redirects=True
            )

        def logout(self):
            return self._client.get('/auth/logout', follow_redirects=True)

    return AuthActions(client)
