from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from time import sleep
import logging
import random

class BaseScraper(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        
        # List of common user agents
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0'
        ]
        
        # Set initial headers
        self.update_headers()

    def update_headers(self):
        """Update session headers with a random user agent"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
            'TE': 'Trailers'
        }
        self.session.headers.update(headers)

    def get_soup(self, url, max_retries=3, delay=2):
        """Get BeautifulSoup object from URL with retries and rate limiting"""
        for attempt in range(max_retries):
            try:
                sleep(delay)  # Rate limiting
                self.update_headers()  # Update headers before each request
                response = self.session.get(url)
                response.raise_for_status()
                return BeautifulSoup(response.text, 'html.parser')
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    raise
                sleep(delay * (attempt + 1))  # Exponential backoff
        return None

    @abstractmethod
    def scrape_products(self):
        """Scrape products from the platform"""
        pass

    @abstractmethod
    def extract_product_details(self, product_element):
        """Extract product details from a product element"""
        pass
