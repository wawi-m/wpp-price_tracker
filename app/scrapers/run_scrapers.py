from app import create_app, db
from app.models.models import Platform, Category, Product
from app.scrapers.jumia import JumiaScraper
from app.scrapers.kilimall import KilimallScraper
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database with platforms and categories"""
    # Create platforms
    platforms = [
        {'name': 'Jumia', 'url': 'https://www.jumia.co.ke'},
        {'name': 'Kilimall', 'url': 'https://www.kilimall.co.ke'}
    ]
    
    for p in platforms:
        if not Platform.query.filter_by(name=p['name']).first():
            platform = Platform(name=p['name'], url=p['url'])
            db.session.add(platform)
            logger.info(f"Created platform: {p['name']}")
    
    # Create categories
    categories = ['Mobile Phones', 'Televisions']
    for c in categories:
        if not Category.query.filter_by(name=c).first():
            category = Category(name=c)
            db.session.add(category)
            logger.info(f"Created category: {c}")
    
    db.session.commit()

def save_products(products, category_name):
    """Save scraped products to database"""
    try:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return
        
        products_updated = 0
        products_created = 0
        
        for product_data in products:
            if not product_data.get('price'):
                logger.warning(f"Skipping product with no price: {product_data.get('name')}")
                continue
                
            platform = Platform.query.filter_by(name=product_data['platform']).first()
            if not platform:
                logger.error(f"Platform not found: {product_data['platform']}")
                continue
            
            # Check if product exists
            product = Product.query.filter_by(url=product_data['url']).first()
            
            if not product:
                # Create new product
                product = Product(
                    name=product_data['name'],
                    url=product_data['url'],
                    image_url=product_data['image_url'],
                    platform_id=platform.id,
                    category_id=category.id,
                    current_price=product_data['price'],
                    currency='KES'
                )
                db.session.add(product)
                products_created += 1
                logger.info(f"Created new product: {product.name}")
            else:
                # Update existing product
                product.name = product_data['name']
                product.image_url = product_data['image_url']
                product.update_price(product_data['price'])
                products_updated += 1
                logger.info(f"Updated product: {product.name}")
        
        db.session.commit()
        logger.info(f"Category {category_name}: Created {products_created}, Updated {products_updated} products")
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving products: {str(e)}")
        raise

def run_scrapers():
    """Run all scrapers and save data"""
    app = create_app()
    with app.app_context():
        try:
            logger.info("Initializing database...")
            init_db()
            
            # Initialize scrapers
            scrapers = {
                'Mobile Phones': [JumiaScraper(), KilimallScraper()],
                'Televisions': [JumiaScraper(), KilimallScraper()]
            }
            
            # Run scrapers for each category
            for category, scraper_list in scrapers.items():
                logger.info(f"Scraping {category}...")
                for scraper in scraper_list:
                    logger.info(f"Using {scraper.__class__.__name__}...")
                    products = scraper.scrape_products(
                        'phones' if category == 'Mobile Phones' else 'tv'
                    )
                    save_products(products, category)
                    
            logger.info("Scraping completed successfully")
            
        except Exception as e:
            logger.error(f"Error running scrapers: {str(e)}")
            raise

if __name__ == '__main__':
    run_scrapers()
