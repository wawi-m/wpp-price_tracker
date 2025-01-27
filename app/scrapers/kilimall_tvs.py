from app.scrapers.base import BaseScraper
import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import random

class KilimallTVScraper(BaseScraper):
    def __init__(self):
        self.platform = 'Kilimall'
        base_url = 'https://www.kilimall.co.ke/category/television?id=2070&form=category'
        super().__init__(base_url)
        self.logger = logging.getLogger(__name__)

    def extract_product_details(self, container):
        """Extract product details from a product container."""
        try:
            # Product Name
            name_elem = container.select_one('.product-title')
            if not name_elem:
                return None
            name = name_elem.text.strip()

            # Product URL
            url_elem = container.select_one('a.product-link')
            if not url_elem or not url_elem.has_attr('href'):
                return None
            url = 'https://www.kilimall.co.ke' + url_elem['href']

            # Image URL
            img_elem = container.select_one('img.product-image')
            image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else None

            # Price
            price_elem = container.select_one('.product-price')
            price = float(re.sub(r'[^\d.]', '', price_elem.text)) if price_elem else None

            if not price:
                return None

            return {
                'platform': self.platform,
                'name': name,
                'url': url,
                'price': price,
                'image_url': image_url
            }
        except Exception as e:
            self.logger.error(f'Error extracting product details: {str(e)}')
            return None

    def scrape_products(self):
        """Scrape products from Kilimall TVs category."""
        try:
            products = []
            max_pages = 5

            for page in range(1, max_pages + 1):
                page_url = f"{self.base_url}&page={page}"
                self.logger.info(f"Scraping page {page}: {page_url}")
                
                # Add delay between requests
                time.sleep(random.uniform(1, 3))
                
                soup = self.get_soup(page_url)
                if not soup:
                    break

                # Find all product containers
                product_containers = soup.select('.product-item')
                if not product_containers:
                    break

                for container in product_containers:
                    product = self.extract_product_details(container)
                    if product:
                        products.append(product)

                self.logger.info(f"Scraped {len(products)} products from page {page}")

            self.logger.info(f"Successfully scraped total of {len(products)} products from Kilimall TVs")

            for product_data in products:
                product = Product(
                    name=product_data['name'],
                    price=product_data['price'],
                    url=product_data['url'],
                    platform=product_data['platform'],
                    image_url=product_data['image_url']
                )
                db.session.add(product)  # Add product to the session

            db.session.commit()  # Commit the session to save all products

            return products

        except Exception as e:
            self.logger.error(f'Error scraping Kilimall TVs: {str(e)}')
            return []

if __name__ == '__main__':
    scraper = KilimallTVScraper()
    products = scraper.scrape_products()
    print(f"Scraped {len(products)} products")
