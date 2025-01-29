from app.scrapers.base import BaseScraper
import logging
import random
from datetime import datetime
from time import sleep
import requests
from bs4 import BeautifulSoup

class KilimallScraper(BaseScraper):
    def __init__(self):
        self.platform = 'Kilimall'
        self.logger = logging.getLogger(__name__)
        super().__init__('https://www.kilimall.co.ke/')

    def extract_product_details(self, container, category):
        """Extract product details from a product container."""
        try:
            # Product Name
            name_elem = container.select_one('.product-title')
            if not name_elem:
                return None
            name = name_elem.text.strip()

            # Product URL
            url_elem = container.select_one('a')
            if not url_elem or not url_elem.has_attr('href'):
                return None
            url = url_elem['href']
            if url.startswith('/'):
                url = 'https://www.kilimall.co.ke' + url

            # Image URL
            img_elem = container.select_one('img')
            image_url = None
            if img_elem:
                # Try data-src first, then src
                image_url = img_elem.get('data-src') or img_elem.get('src')

            # Price
            price_elem = container.select_one('.product-price')
            if not price_elem:
                return None
            try:
                price_text = price_elem.text.strip()
                # Remove currency symbol and commas, then convert to float
                price = float(price_text.replace('KSh', '').replace(',', '').strip())
            except (ValueError, TypeError):
                self.logger.error(f"Error parsing price for product: {name}")
                return None

            return {
                'platform': self.platform,
                'name': name,
                'url': url,
                'price': price,
                'image_url': image_url,
                'category': category,
                'timestamp': datetime.now()
            }

        except Exception as e:
            self.logger.error(f"Error extracting product: {str(e)}")
            return None

    def get_category_url(self, category):
        """Get the URL for a given category."""
        category_mapping = {
            'Mobile Phones': {'slug': 'mobile-phones', 'id': '873'},
            'Televisions': {'slug': 'television', 'id': '2070'}
        }
        
        cat_info = category_mapping.get(category)
        if not cat_info:
            return None
            
        return f"https://www.kilimall.co.ke/category/{cat_info['slug']}?id={cat_info['id']}&form=category"

    def get_soup(self, url):
        """Get the BeautifulSoup object for a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error getting soup for {url}: {str(e)}")
            return None

    def scrape_products(self, category):
        """Scrape products from a given category."""
        try:
            url = self.get_category_url(category)
            if not url:
                self.logger.error(f"Unknown category: {category}")
                return []

            self.logger.info(f"Scraping {category} from {url}")
            products = []

            # Get the first page
            soup = self.get_soup(url)
            if not soup:
                return products

            # Extract products from the current page
            product_containers = soup.select('[data-v-c039e353].product-item')
            for container in product_containers:
                product = self.extract_product_details(container, category)
                if product:
                    products.append(product)
                    if len(products) >= 50:  # Limit to 50 products per category
                        break

            return products

        except Exception as e:
            self.logger.error(f"Error scraping {category}: {str(e)}")
            return []

    def scrape_all(self):
        """Scrape both mobile phones and televisions."""
        all_products = []
        
        # Scrape phones
        phone_products = self.scrape_products('Mobile Phones')
        if phone_products:
            all_products.extend(phone_products)
            sleep(random.uniform(2, 4))  # Random delay between categories
        
        # Scrape TVs
        tv_products = self.scrape_products('Televisions')
        if tv_products:
            all_products.extend(tv_products)
        
        return all_products
