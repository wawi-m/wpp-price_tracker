import requests
from bs4 import BeautifulSoup
import re
import logging
import time
import random

class KilimallScraper:
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
        Extract product details from HTML content.
        
        Args:
            html_content (str): HTML content of the page
        
        Returns:
            list: List of dictionaries containing product details
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        products = []

        # Find all product containers
        product_containers = soup.select('.product-item')

        for container in product_containers:
            try:
                # Product Name
                name_elem = container.select_one('.product-title')
                name = name_elem.text.strip() if name_elem else 'N/A'

                # Product URL
                url_elem = container.select_one('a.product-link')
                url = self.base_url + url_elem['href'] if url_elem and url_elem.has_attr('href') else 'N/A'

                # Extract item_id from URL
                item_id = None
                if url != 'N/A':
                    # Try to extract ID from URL pattern like '/item/xxx.html'
                    id_match = re.search(r'/item/(\d+)\.html', url)
                    if id_match:
                        item_id = id_match.group(1)

                # Category
                category = None
                category_elem = container.select_one('.product-category')
                if category_elem:
                    category = category_elem.text.strip()
                else:
                    # Try to get category from breadcrumb if available
                    breadcrumb = soup.select_one('.breadcrumb')
                    if breadcrumb:
                        category_items = breadcrumb.select('li')
                        if len(category_items) > 1:  # Skip 'Home'
                            category = category_items[-1].text.strip()

                # Image URL
                img_elem = container.select_one('img.product-image')
                image_url = img_elem['src'] if img_elem and img_elem.has_attr('src') else 'N/A'

                # Price
                price_elem = container.select_one('.product-price')
                price = self.clean_price(price_elem.text) if price_elem else None

                # Old Price (Original Price)
                old_price_elem = container.select_one('.original-price')
                old_price = self.clean_price(old_price_elem.text) if old_price_elem else None

                # Discount
                discount_elem = container.select_one('.discount-badge')
                discount = self.clean_price(discount_elem.text) if discount_elem else None

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
        Scrape products from a specific category URL.
        
        Args:
            category_url (str): URL of the category page
            max_pages (int): Maximum number of pages to scrape
        
        Returns:
            list: List of product dictionaries
        """
        all_products = []
        
        for page in range(1, max_pages + 1):
            try:
                # Add page parameter if needed
                page_url = f"{category_url}&page={page}" if '?' in category_url else f"{category_url}?page={page}"
                
                # Random delay between requests to avoid rate limiting
                delay = random.uniform(1.5, 3.5)
                self.logger.info(f"Waiting {delay:.2f} seconds before request")
                time.sleep(delay)
                
                # Make request with headers
                response = requests.get(page_url, headers=self.headers, timeout=15)
                response.raise_for_status()
                
                # Extract products from this page
                page_products = self.extract_products(response.text)
                
                # Break if no products found
                if not page_products:
                    break
                
                all_products.extend(page_products)
                
                self.logger.info(f"Scraped page {page}, total products: {len(all_products)}")
                
            except requests.RequestException as e:
                self.logger.error(f"Error scraping page {page} of category {category_url}: {e}")
                break
        
        return all_products

def main():
    # Example usage
    scraper = KilimallScraper()
    phones_url = 'https://www.kilimall.co.ke/category/mobile-phones?id=873&form=category'
    products = scraper.scrape_category(phones_url)
    
    # Optional: Save results to a file
    import json
    with open('kilimall_phones.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    print(f"Total products scraped: {len(products)}")

if __name__ == '__main__':
    main()