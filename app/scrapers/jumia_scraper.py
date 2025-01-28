from app.scrapers.base import BaseScraper
import logging
import random
from datetime import datetime
from time import sleep
from bs4 import BeautifulSoup
import requests

class JumiaScraper(BaseScraper):
    def __init__(self):
        self.platform = 'Jumia'
        self.logger = logging.getLogger(__name__)
        super().__init__('https://www.jumia.co.ke/')

    def extract_product_details(self, container, category):
        """Extract product details from a product container (phone/TV)."""
        try:
            # Product Name
            name_elem = container.select_one('.core')
            if not name_elem:
                return None
            name = name_elem.get('data-name', '').strip()

            # Product URL
            url_elem = container.select_one('a.core')
            if not url_elem or not url_elem.has_attr('href'):
                return None
            url = 'https://www.jumia.co.ke' + url_elem['href']

            # Image URL
            img_elem = container.select_one('img')
            image_url = img_elem['data-src'] if img_elem else None

            # Price
            price_elem = container.select_one('.prc')
            price = float(price_elem.text.replace('KSh ', '').replace(',', '').strip()) if price_elem else None

            if not price:
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

    def scrape_products(self, category):
        """Scrape products from a given category (phones or TVs)."""
        try:
            url = f'https://www.jumia.co.ke/{category.lower().replace(" ", "-")}/'
            self.logger.info(f"Scraping {category} from {url}")
            products = []

            soup = self.get_soup(url)
            if soup:
                product_containers = soup.select('.prd')
                for container in product_containers:
                    product = self.extract_product_details(container, category)
                    if product:
                        products.append(product)

            return products
        except Exception as e:
            self.logger.error(f"Error scraping {category}: {str(e)}")
            return []

    def scrape_all(self):
        """Scrape both mobile phones and televisions."""
        phone_products = self.scrape_products('Mobile Phones')
        tv_products = self.scrape_products('Televisions')
        return phone_products + tv_products
