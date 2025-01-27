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

    def clean_price(self, price_str):
        """Clean price string and convert to float"""
        try:
            # Remove currency symbol and commas, then convert to float
            price_str = re.sub(r'[^\d.]', '', price_str)
            return float(price_str) if price_str else 0.0
        except (ValueError, TypeError):
            return 0.0

    def extract_product_details(self, container):
        try:
            # Get the product link element
            link_elem = container.find('a', class_='core')
            if not link_elem:
                return None

            # Extract product details
            name = link_elem.get('data-name', '').strip()
            url = f"https://www.jumia.co.ke{link_elem.get('href', '')}"
            image_url = link_elem.find('img')['data-src'] if link_elem.find('img') else ''
            
            # Extract price from the price div
            price_div = container.find('div', class_='prc')
            price_str = price_div.text.strip() if price_div else '0'
            price = self.clean_price(price_str)
            
            # Extract old price
            old_price_div = container.find('div', class_='old')
            old_price = self.clean_price(old_price_div.text.strip()) if old_price_div else price
            
            # Calculate discount
            discount = round(((old_price - price) / old_price) * 100, 2) if old_price > price else 0
            
            item_id = link_elem.get('data-id', '')
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
            
            self.logger.info(f'Successfully scraped {len(products)} products from Jumia Phones')
            return products
        except Exception as e:
            self.logger.error(f'Error scraping Jumia Phones: {str(e)}')
            return []
