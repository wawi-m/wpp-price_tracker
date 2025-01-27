import os
from app import create_app, db
from app.models.models import Platform, Category  # Import your models
from app.scrapers.run_scrapers import run_all_scrapers  # Import the scraper function
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

            # Initialize platforms if they don't exist
            platforms = [
                {'name': 'Jumia', 'url': 'https://www.jumia.co.ke'},
                {'name': 'Kilimall', 'url': 'https://www.kilimall.co.ke'}
            ]
            for p in platforms:
                if not Platform.query.filter_by(name=p['name']).first():
                    platform = Platform(name=p['name'], url=p['url'])
                    db.session.add(platform)
                    logger.info(f"Created platform: {p['name']}")

            # Initialize categories if they don't exist
            categories = ['Mobile Phones', 'Televisions']
            for c in categories:
                if not Category.query.filter_by(name=c).first():
                    category = Category(name=c)
                    db.session.add(category)
                    logger.info(f"Created category: {c}")

            db.session.commit()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {str(e)}")
            db.session.rollback()
            raise

def run_scrapers():
    """Run all scrapers with proper app context"""
    with app.app_context():
        try:
            run_all_scrapers()
            logger.info("Scrapers completed successfully")
        except Exception as e:
            logger.error(f"Error running scrapers: {str(e)}")

if __name__ == '__main__':
    init_db()  # Initialize database before running the app
    run_scrapers()  # Run the scrapers
    app.run(debug=True)  # Start the Flask app