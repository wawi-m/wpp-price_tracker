import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import random

class KilimallTVScraper:
    def __init__(self, base_url='https://www.kilimall.co.ke'):
        self.base_url = base_url
        self.platform = 'Kilimall'
        
        # Logging configuration
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Headers to mimic a browser request
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.kilimall.co.ke/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }

    def clean_price(self, price_str):
        """Clean and convert price string to float."""
        if not price_str:
            return None
        return float(re.sub(r'[^\d.]', '', price_str))

    def extract_products(self, html_content):
        """
        Extract TV product details from HTML content.
        
        Args:
            html_content (str): HTML content of the page
        
        Returns:
            list: List of dictionaries containing TV product details
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        # Find all product containers - using Jumia's article class structure
        product_containers = soup.select('article.prd')

        for container in product_containers:
            try:
                # Get the product link element which contains most metadata
                link_elem = container.select_one('a.core')
                if not link_elem:
                    continue

                # Extract data-* attributes
                item_id = link_elem.get('data-gtm-id', 'N/A')
                category = link_elem.get('data-gtm-category', 'N/A').split('/')[-1] if link_elem.get('data-gtm-category') else 'N/A'

                # Product Name
                name_elem = container.select_one('.name')
                name = name_elem.text.strip() if name_elem else 'N/A'

                # Product URL - using the link href
                url = self.base_url + link_elem['href'] if link_elem.has_attr('href') else 'N/A'

                # Image URL - using the img tag within the link
                img_elem = link_elem.select_one('img')
                image_url = img_elem.get('data-src') if img_elem and img_elem.has_attr('data-src') else 'N/A'

                # Price - look for both current and old price
                price_container = container.select_one('.prc')
                price = self.clean_price(price_container.text) if price_container else None

                # Old Price
                old_price_elem = container.select_one('.old')
                old_price = self.clean_price(old_price_elem.text) if old_price_elem else None

                # Discount - calculated from data attribute
                discount = float(link_elem.get('data-gtm-discount', 0))

                # Create product dictionary
                product = {
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

                products.append(product)

            except Exception as e:
                self.logger.error(f"Error extracting product: {e}")

        self.logger.info(f"Extracted {len(products)} products")
        return products

    def scrape_category(self, category_url, max_pages=5):
        """
        Scrape TV products from a specific category URL.
        
        Args:
            category_url (str): URL of the category page
            max_pages (int): Maximum number of pages to scrape
        
        Returns:
            list: List of all products scraped
        """
        all_products = []
        current_page = 1

        try:
            while current_page <= max_pages:
                # Add page parameter to URL if not first page
                page_url = f"{category_url}?page={current_page}" if current_page > 1 else category_url
                
                # Add random delay between requests
                time.sleep(random.uniform(1, 3))
                
                # Make the request
                self.logger.info(f"Scraping page {current_page}: {page_url}")
                response = requests.get(page_url, headers=self.headers)
                
                if response.status_code == 200:
                    # Extract products from the page
                    products = self.extract_products(response.text)
                    
                    if not products:
                        self.logger.info("No more products found. Stopping pagination.")
                        break
                        
                    all_products.extend(products)
                    current_page += 1
                else:
                    self.logger.error(f"Failed to fetch page {current_page}. Status code: {response.status_code}")
                    break
                    
        except Exception as e:
            self.logger.error(f"Error during scraping: {e}")
            
        self.logger.info(f"Total products scraped: {len(all_products)}")
        return all_products


def main():
    # Sample usage
    scraper = KilimallTVScraper()
    # Replace with actual TV category URL
    sample_url = "https://www.kilimall.co.ke/category/television?id=2070&form=category"
    products = scraper.scrape_category(sample_url)
    
    # Log the results
    for product in products:
        print(f"Found TV: {product['name']} - Price: {product['price']}")


if __name__ == '__main__':
    main()
