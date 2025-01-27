from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from time import sleep
import logging
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class BaseScraper(ABC):
    def __init__(self, base_url):
        self.base_url = base_url
        self.logger = logging.getLogger(__name__)
        self.setup_driver()

    def setup_driver(self):
        """Setup Chrome webdriver with headless mode"""
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Add random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0'
        ]
        chrome_options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": random.choice(user_agents)})
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            self.logger.error(f"Error setting up Chrome driver: {str(e)}")
            raise

    def get_soup(self, url, wait_for=None, max_retries=3, delay=2):
        """Get BeautifulSoup object from URL using Selenium with retries and rate limiting"""
        for attempt in range(max_retries):
            try:
                sleep(delay)  # Rate limiting
                self.driver.get(url)
                
                if wait_for:
                    # Wait for specific element to be present
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )
                
                # Get page source after JavaScript execution
                page_source = self.driver.page_source
                return BeautifulSoup(page_source, 'html.parser')
            
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt == max_retries - 1:  # Last attempt
                    raise
                sleep(delay * (attempt + 1))  # Exponential backoff
        return None

    def __del__(self):
        """Clean up webdriver when object is destroyed"""
        try:
            if hasattr(self, 'driver'):
                self.driver.quit()
        except Exception as e:
            self.logger.error(f"Error closing driver: {str(e)}")

    @abstractmethod
    def scrape_products(self):
        """Scrape products from the platform"""
        pass

    @abstractmethod
    def extract_product_details(self, product_element):
        """Extract product details from a product element"""
        pass
