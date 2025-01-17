import os
import tempfile
import pytest
from app import create_app, db
from app.models import User, Store

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # Create a temporary file to isolate the database for each test
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app({
        'TESTING': True,
        'DATABASE': db_path,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })

    yield app

    # Close and remove the temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """A test CLI runner for the app."""
    return app.test_cli_runner()

class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, email='test@example.com', password='test'):
        return self._client.post(
            '/auth/login',
            data={'email': email, 'password': password}
        )

    def logout(self):
        return self._client.get('/auth/logout')

@pytest.fixture
def auth(client):
    return AuthActions(client)

@pytest.fixture
def app_context(app):
    """Create an application context."""
    with app.app_context():
        db.create_all()
        yield

@pytest.fixture
def test_user(app_context):
    """Create a test user."""
    user = User(name='test', email='test@example.com', password='test')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def store(app_context, test_user):
    """Create a test store."""
    store = Store(name="Test Store", marketplace="US", user_id=test_user.id)
    db.session.add(store)
    db.session.commit()
    return store
