from bs4 import BeautifulSoup
import requests
import re
import logging
from app.scrapers.base import BaseScraper

class JumiaPhoneScraper(BaseScraper):
    def __init__(self):
        self.platform = 'Jumia'
        self.base_url = 'https://www.jumia.co.ke/mobile-phones/#catalog-listing'
        super().__init__(self.base_url)
        self.logger = logging.getLogger(__name__)

    def extract_product_details(self, container):
        try:
            # Get the product link element
            link_elem = container.find('a', class_='core')
            if not link_elem:
                return None

            # Extract product details
            name = link_elem.get('data-ga4-item_name', '').strip()
            url = f"https://www.jumia.co.ke{link_elem.get('href', '')}"
            image_url = link_elem.find('img')['data-src'] if link_elem.find('img') else ''
            price = float(link_elem.get('data-ga4-price', 0))
            discount = float(link_elem.get('data-ga4-discount', 0))
            old_price = price / (1 - discount/100) if discount else price
            item_id = link_elem.get('data-ga4-item_id', '')
            category = 'Phone'

            # Create product dictionary
            return {
                'platform': self.platform,
                'name': name,
                'price': price,
                'old_price': old_price,
                'discount': discount,
                'url': url,
                'image_url': image_url,
                'item_id': item_id,
                'category': category
            }
        except Exception as e:
            self.logger.error(f'Error extracting product: {str(e)}')
            return None

    def scrape_products(self):
        try:
            soup = self.get_soup(self.base_url)
            products = []
            product_containers = soup.find_all('article', class_='prd')
            
            for container in product_containers:
                product = self.extract_product_details(container)
                if product:
                    products.append(product)
            
            return products
        except Exception as e:
            self.logger.error(f'Error scraping Jumia Phones: {str(e)}')
            return []
