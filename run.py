import os
from app import create_app, db
from app.models.models import Platform, Category
from app.scrapers.run_scrapers import run_all_scrapers
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get database URL from environment variable
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

# Create Flask app with database URL
app = create_app(database_url)

def init_db():
    """Initialize the database with platforms and categories if they don't exist."""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()

            # Initialize platforms and categories
            Platform.insert_default_platforms()
            Category.insert_default_categories()
            
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

if __name__ == '__main__':
    init_db()  # Initialize database before running the app
    run_all_scrapers()  # Run scrapers once
    app.run(debug=True)  # Start the Flask app