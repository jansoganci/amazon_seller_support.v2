from app import create_app, db
from app.models.user import User
from app.extensions import bcrypt

app = create_app()

with app.app_context():
    # Create a test user
    user = User(username='test', email='test@example.com')
    user.password_hash = bcrypt.generate_password_hash('test123').decode('utf-8')

    # Add to database
    db.session.add(user)
    db.session.commit()

    print('Test user created successfully!') 