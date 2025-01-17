from app import create_app, db
from flask_migrate import Migrate  # Import Flask-Migrate

app = create_app()
migrate = Migrate(app, db)  # Initialize Flask-Migrate

if __name__ == '__main__':
    with app.app_context():
        # db.create_all()  # You can remove this line since Flask-Migrate will handle schema changes
        pass
    app.run(debug=True, port=3005)