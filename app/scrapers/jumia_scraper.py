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
            name_elem = container.select_one('h3.name')
            if not name_elem:
                return None
            name = name_elem.text.strip()

            # Product URL
            url_elem = container.select_one('a.core')
            if not url_elem or not url_elem.has_attr('href'):
                return None
            url = 'https://www.jumia.co.ke' + url_elem['href']

            # Image URL
            img_elem = container.select_one('img.img')
            image_url = img_elem['data-src'] if img_elem and 'data-src' in img_elem.attrs else None

            # Price
            price_elem = container.select_one('.prc')
            if not price_elem:
                return None
            try:
                price = float(price_elem.text.replace('KSh ', '').replace(',', '').strip())
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

    def scrape_products(self, category):
        """Scrape products from a given category (phones or TVs)."""
        try:
            category_slug = category.lower().replace(" ", "-")
            url = f'https://www.jumia.co.ke/{category_slug}/'
            self.logger.info(f"Scraping {category} from {url}")
            products = []

            # Get the first page
            soup = self.get_soup(url)
            if not soup:
                return products

            # Extract products from the current page
            product_containers = soup.select('article.prd')
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
