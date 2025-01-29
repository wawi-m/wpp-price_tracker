import logging
from app.scrapers.jumia_scraper import JumiaScraper
from app.scrapers.kilimall_scraper import KilimallScraper

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_scraper(scraper_class):
    """Test a scraper by running it and checking the results."""
    try:
        scraper = scraper_class()
        products = scraper.scrape_all()
        
        if not products:
            logger.error(f"{scraper.platform}: No products found!")
            return False
        
        logger.info(f"\n{scraper.platform} Results:")
        logger.info(f"Total products found: {len(products)}")
        
        # Display first 3 products as sample
        for i, product in enumerate(products[:3], 1):
            logger.info(f"\nProduct {i}:")
            logger.info(f"Name: {product['name']}")
            logger.info(f"Price: KES {product['price']:,.2f}")
            logger.info(f"URL: {product['url']}")
            logger.info(f"Category: {product['category']}")
        
        return True
    
    except Exception as e:
        logger.error(f"Error testing {scraper_class.__name__}: {str(e)}")
        return False

def main():
    """Test both scrapers."""
    logger.info("Testing Jumia Scraper...")
    jumia_success = test_scraper(JumiaScraper)
    
    logger.info("\nTesting Kilimall Scraper...")
    kilimall_success = test_scraper(KilimallScraper)
    
    if jumia_success and kilimall_success:
        logger.info("\nAll scrapers working correctly!")
    else:
        logger.error("\nSome scrapers failed!")

if __name__ == "__main__":
    main()
