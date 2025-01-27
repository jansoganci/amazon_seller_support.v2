from app import create_app, db
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        # Create database tables
        logger.info('Creating database tables...')
        db.create_all()
        logger.info('Database tables created successfully')
    
    logger.info('Starting application on http://127.0.0.1:3005')
    app.run(host='127.0.0.1', port=3005, debug=True)