# app/scrapers/run_scrapers.py
from app import create_app, db
from app.models.models import Platform, Category, Product
from app.scrapers.jumia_scraper import JumiaScraper
from app.scrapers.kilimall_scraper import KilimallScraper
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_products(products, category_name):
    """Save scraped products to the database."""
    try:
        category = Category.query.filter_by(name=category_name).first()
        if not category:
            logger.error(f"Category not found: {category_name}")
            return
        
        platform_cache = {}
        products_updated = 0
        products_created = 0
        
        for product_data in products:
            try:
                # Get platform
                platform_name = product_data['platform']
                if platform_name not in platform_cache:
                    platform = Platform.query.filter_by(name=platform_name).first()
                    if not platform:
                        logger.error(f"Platform not found: {platform_name}")
                        continue
                    platform_cache[platform_name] = platform
                platform = platform_cache[platform_name]
                
                # Check if product exists
                product = Product.query.filter_by(
                    url=product_data['url'],
                    platform_id=platform.id
                ).first()
                
                if product:
                    # Update existing product
                    if product.current_price != product_data['price']:
                        product.update_price(product_data['price'])
                    product.name = product_data['name']
                    product.image_url = product_data.get('image_url')
                    product.last_price_update = datetime.utcnow()
                    products_updated += 1
                else:
                    # Create new product
                    product = Product(
                        name=product_data['name'],
                        url=product_data['url'],
                        image_url=product_data.get('image_url'),
                        current_price=product_data['price'],
                        platform=platform,
                        category=category,
                        last_price_update=datetime.utcnow()
                    )
                    db.session.add(product)
                    products_created += 1
                
            except Exception as e:
                logger.error(f"Error processing product {product_data.get('name')}: {str(e)}")
                continue
        
        db.session.commit()
        logger.info(f"Category {category_name}: Created {products_created} products, Updated {products_updated} products")
        
    except Exception as e:
        logger.error(f"Error saving products: {str(e)}")
        db.session.rollback()
        raise

def run_all_scrapers():
    """Run all scrapers and save data."""
    app = create_app()
    with app.app_context():
        # Initialize scrapers (now using unified scrapers for Jumia and Kilimall)
        scrapers = [
            (JumiaScraper(), "Mobile Phones"),
            (JumiaScraper(), "Televisions"),
            (KilimallScraper(), "Mobile Phones"),
            (KilimallScraper(), "Televisions")
        ]
        
        total_products = 0
        # Run each scraper
        for scraper, category in scrapers:
            try:
                logger.info(f"Running {scraper.__class__.__name__} for category {category}")
                products = scraper.scrape_all()
                if products:
                    total_products += len(products)
                    save_products(products, category)
            except Exception as e:
                logger.error(f"Error running {scraper.__class__.__name__} for category {category}: {str(e)}")
        
        logger.info(f"Scraping completed. Total products processed: {total_products}")

if __name__ == '__main__':
    run_all_scrapers()
