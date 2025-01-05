from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    for user in users:
        if user._preferences is None:
            user._preferences = '{"language":"tr","currency":"TRY","theme":"light","notifications":{"email":true,"browser":true}}'
    db.session.commit()
    print("User preferences updated successfully!")
