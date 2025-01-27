from app import create_app, db
from app.models.models import Platform, Category  # Import your models
from app.scrapers.run_scrapers import run_all_scrapers  # Import the scraper function
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()

def init_db():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Initialize basic data
        platforms = [
            {'name': 'Jumia', 'url': 'https://www.jumia.co.ke'},
            {'name': 'Kilimall', 'url': 'https://www.kilimall.co.ke'}
        ]
        
        categories = ['Mobile Phones', 'Televisions']
        
        # Add platforms if they don't exist
        for p in platforms:
            if not Platform.query.filter_by(name=p['name']).first():
                platform = Platform(name=p['name'], url=p['url'])
                db.session.add(platform)
                logger.info(f"Created platform: {p['name']}")
        
        # Add categories if they don't exist
        for c in categories:
            if not Category.query.filter_by(name=c).first():
                category = Category(name=c)
                db.session.add(category)
                logger.info(f"Created category: {c}")
        
        db.session.commit()
        logger.info("Database initialized successfully")

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