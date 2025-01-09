from app.scrapers.base import BaseScraper
import re
import json
import logging
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

logger = logging.getLogger(__name__)

class KilimallScraper(BaseScraper):
    def __init__(self):
        super().__init__('https://www.kilimall.co.ke')
        self.mobile_url = f"{self.base_url}/category/mobile-phones?id=873"
        self.tv_url = f"{self.base_url}/category/television?id=2070"
        
        # Initialize undetected-chromedriver
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        
        self.driver = uc.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def __del__(self):
        """Clean up WebDriver"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def extract_product_details(self, product_element):
        """Extract product details from a product element"""
        try:
            # Get product name and link
            name_link = product_element.find_element(By.CSS_SELECTOR, '.goods-name')
            name = name_link.text.strip()
            url = name_link.get_attribute('href')
            
            # Get price
            price_elem = product_element.find_element(By.CSS_SELECTOR, '.price-box .price')
            price_text = price_elem.text.strip()
            price = float(re.sub(r'[^\d.]', '', price_text))
            
            # Get image
            img_elem = product_element.find_element(By.CSS_SELECTOR, '.goods-image img')
            image = img_elem.get_attribute('src')
            
            if not all([name, price, url]):
                logger.warning(f"Missing required fields for product: {name}")
                return None
                
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image,
                'platform': 'Kilimall'
            }
        except (NoSuchElementException, ValueError) as e:
            logger.error(f"Error extracting product details: {str(e)}")
            return None

    def scrape_products(self, category='phones'):
        """Scrape products from Kilimall website"""
        url = self.mobile_url if category == 'phones' else self.tv_url
        products = []
        page = 1
        
        try:
            # Load initial page
            self.driver.get(url)
            
            while True:
                try:
                    # Wait for products to load
                    self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.goods-item')))
                    time.sleep(2)  # Give JavaScript a moment to finish rendering
                    
                    # Get all product elements
                    product_elements = self.driver.find_elements(By.CSS_SELECTOR, '.goods-item')
                    
                    if not product_elements:
                        logger.info(f"No more products found on page {page}")
                        break
                    
                    # Extract product details
                    for element in product_elements:
                        product = self.extract_product_details(element)
                        if product:
                            products.append(product)
                            logger.info(f"Found product: {product['name']}")
                    
                    # Check if there's a next page button and it's clickable
                    try:
                        next_button = self.driver.find_element(By.CSS_SELECTOR, '.next-page:not(.disabled)')
                        if page >= 5:  # Limit to 5 pages for testing
                            break
                        next_button.click()
                        page += 1
                        time.sleep(2)  # Wait for page to load
                    except NoSuchElementException:
                        logger.info("No more pages available")
                        break
                        
                except TimeoutException:
                    logger.error(f"Timeout waiting for products on page {page}")
                    break
                    
        except Exception as e:
            logger.error(f"Error scraping products: {str(e)}")
        
        logger.info(f"Found {len(products)} products in category {category}")
        return products
