from app.scrapers.base import BaseScraper
import re

class JumiaScraper(BaseScraper):
    def __init__(self):
        super().__init__('https://www.jumia.co.ke')
        self.mobile_url = f"{self.base_url}/mobile-phones/"
        self.tv_url = f"{self.base_url}/televisions/"

    def extract_product_details(self, product_element):
        try:
            name = product_element.select_one('.name').text.strip()
            price_elem = product_element.select_one('.prc')
            price = float(re.sub(r'[^\d.]', '', price_elem.text)) if price_elem else None
            url = self.base_url + product_element.select_one('a')['href']
            image = product_element.select_one('img')['data-src']
            
            return {
                'name': name,
                'price': price,
                'url': url,
                'image_url': image,
                'platform': 'Jumia'
            }
        except (AttributeError, TypeError, ValueError) as e:
            print(f"Error extracting product details: {e}")
            return None

    def scrape_products(self, category='phones'):
        url = self.mobile_url if category == 'phones' else self.tv_url
        products = []
        page = 1
        
        while True:
            try:
                soup = self.get_soup(f"{url}?page={page}")
                product_elements = soup.select('article.prd')
                
                if not product_elements:
                    break
                    
                for element in product_elements:
                    product = self.extract_product_details(element)
                    if product:
                        products.append(product)
                
                page += 1
                if page > 5:  # Limit to 5 pages for testing
                    break
                    
            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                break
                
        return products
