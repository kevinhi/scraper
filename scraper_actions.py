# scraper_actions.py

import time
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from logging_setup import log_message, log_debug, log_error
from price_parser import parse_price

class ScraperActions:
    def __init__(self, driver, config, log_text, results_text):
        self.driver = driver
        self.config = config
        self.log_text = log_text
        self.results_text = results_text
        self.product_titles_seen = set()  # Track seen product titles to avoid duplicates
        self.product_data = []  # List to store extracted data

    def navigate_to_page(self, url):
        """Navigate the WebDriver to the specified URL."""
        try:
            log_message(f"Navigating to URL: {url}", self.log_text, level="info")
            self.driver.get(url)
            time.sleep(int(self.config.get('scroll_delay_var', 25)) / 1000)
        except TimeoutException as e:
            log_error(f"Timeout while navigating to URL: {url}. Error: {e}", self.log_text)
        except Exception as e:
            log_error(f"Unexpected error while navigating to URL: {url}. Error: {e}", self.log_text)

    def extract_product_containers(self):
        """Extract product containers from the current page using the container CSS selector."""
        container_selector = self.config.get('container_selector_var', '')
        try:
            containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
            log_debug(f"Found {len(containers)} product containers", self.log_text)
            return containers
        except NoSuchElementException:
            log_error(f"No product containers found using selector: {container_selector}", self.log_text)
            return []

    def extract_product_data(self, container):
        """Extract product data (title and price) from a container and store it in the results."""
        try:
            title_selector = self.config.get('title_selector_var', '')
            price_selector = self.config.get('price_selectors_var', '')

            title_element = container.find_element(By.CSS_SELECTOR, title_selector)
            product_title = title_element.text.strip()

            # Check for duplicate product titles
            if product_title in self.product_titles_seen:
                log_debug(f"Duplicate product found and skipped: {product_title}", self.log_text)
                return False
            self.product_titles_seen.add(product_title)

            # Extract price and validate
            price_element = container.find_element(By.CSS_SELECTOR, price_selector)
            raw_primary_price_text = price_element.text.strip()
            primary_price = parse_price(raw_primary_price_text, self.log_text)

            if primary_price is None:
                log_debug(f"Skipping product due to missing primary price: {product_title}", self.log_text)
                return False

            # Add product data to results
            self.results_text.insert("end", f"Title: {product_title}, Price: {primary_price}\n")
            self.product_data.append([product_title, primary_price])
            return True

        except NoSuchElementException:
            log_debug("Skipping container due to missing title or price element", self.log_text)
            return False
        except Exception as e:
            log_error(f"Unexpected error while extracting product data: {e}", self.log_text)
            return False

    def save_data_to_csv(self, filename="output.csv"):
        """Save extracted product data to a CSV file."""
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Product Title", "Primary Price"])
                writer.writerows(self.product_data)
            log_message(f"Product data saved to CSV file: {filename}", self.log_text, level="info")
        except Exception as e:
            log_error(f"Error saving data to CSV: {e}", self.log_text)

    def reset_data(self):
        """Reset stored product data and titles to start fresh."""
        self.product_data.clear()
        self.product_titles_seen.clear()
        log_message("Data reset for new scraping session.", self.log_text, level="info")
