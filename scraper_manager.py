# scraper_manager.py

import threading
import time
import csv
from selenium.common.exceptions import (
    NoSuchElementException, TimeoutException, WebDriverException, StaleElementReferenceException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from driver_utils import initialize_driver
from price_parser import parse_price
from logging_setup import log_message, log_debug, log_error

class ScraperManager:
    def __init__(self, config, log_text, results_text, progress_bar, root,
                 user_agent_label, status_bar, containers_found_label,
                 page_number_label, total_products_found_label,
                 total_products_skipped_label, selectors_found_label):
        self.config = config
        self.log_text = log_text
        self.results_text = results_text
        self.progress_bar = progress_bar
        self.root = root
        self.user_agent_label = user_agent_label
        self.status_bar = status_bar
        self.containers_found_label = containers_found_label
        self.page_number_label = page_number_label
        self.total_products_found_label = total_products_found_label
        self.total_products_skipped_label = total_products_skipped_label
        self.selectors_found_label = selectors_found_label
        self.driver = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()
        self.product_data = []  # Store collected product data for CSV export

    def start_scraping(self):
        """Start the scraping process."""
        log_message("Scraping process started", self.log_text, level="info")
        self.stop_event.clear()
        self.pause_event.set()
        self.driver = initialize_driver(self.config.get('user_agent_var', ''), self.log_text)

        if not self.driver:
            log_error("Failed to initialize WebDriver.", self.log_text)
            return

        try:
            max_pages = int(self.config.get('max_pages_var', 1))
            base_url = self.construct_base_url()
            self.update_status_bar("Starting scraping...")

            for page_number in range(1, max_pages + 1):
                if self.stop_event.is_set():
                    log_message("Scraping stopped by user", self.log_text, level="warning")
                    break

                self.handle_pause()
                current_url = self.construct_url(page_number)
                self.load_page(current_url, page_number)

                containers = self.extract_containers()
                if not containers:
                    continue

                self.process_containers(containers, page_number)

                progress_value = (page_number / max_pages) * 100
                self.update_progress(progress_value)
                self.update_estimated_time(page_number, max_pages)

            self.save_data_to_csv()
            self.show_completion_message()
            self.update_status_bar("Scraping completed.")

        except Exception as e:
            log_error(f"Unexpected error during scraping: {e}", self.log_text)
            self.update_status_bar(f"Error during scraping: {e}")
        finally:
            if self.driver:
                self.driver.quit()
                log_message("WebDriver closed.", self.log_text, level="info")

    def handle_pause(self):
        """Handle pause in scraping if triggered."""
        while not self.pause_event.is_set():
            if self.stop_event.is_set():
                log_message("Scraping stopped by user during pause.", self.log_text, level="warning")
                return
            time.sleep(0.1)

    def load_page(self, url, page_number):
        """Load a page in the WebDriver."""
        log_message(f"Navigating to URL: {url}", self.log_text, level="info")
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, 'body')))
            log_debug(f"Page {page_number} loaded successfully.", self.log_text)
        except TimeoutException:
            log_error(f"Timeout loading page {page_number}.", self.log_text)
        except WebDriverException as e:
            log_error(f"Error loading page {page_number}: {e}", self.log_text)

    def extract_containers(self):
        """Extract product containers from the current page."""
        container_selector = self.config.get('container_selector_var', '')
        try:
            containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
            self.update_gui_label(self.containers_found_label, f"Containers Found: {len(containers)}")
            log_debug(f"Found {len(containers)} containers", self.log_text)
            return containers
        except NoSuchElementException:
            log_error(f"No containers found with selector '{container_selector}'", self.log_text)
            return []

    def process_containers(self, containers, page_number):
        """Process each product container to extract data."""
        products_found = 0
        products_skipped = 0

        for container in containers:
            if self.stop_event.is_set():
                log_message("Scraping stopped by user during container processing.", self.log_text, level="warning")
                return

            try:
                title, price = self.extract_product_data(container)
                if title and price is not None:
                    self.product_data.append((title, price))  # Save for CSV
                    self.results_text.insert("end", f"Title: {title}, Price: {price}\n")
                    products_found += 1
                else:
                    products_skipped += 1

            except Exception as e:
                log_error(f"Unexpected error processing container: {e}", self.log_text)

        self.update_gui_label(self.total_products_found_label, f"Products Found: {products_found}")
        self.update_gui_label(self.total_products_skipped_label, f"Products Skipped: {products_skipped}")
        self.update_gui_label(self.page_number_label, f"Page: {page_number}")

    def extract_product_data(self, container):
        """Extract product title and price from a container."""
        title_selector = self.config.get('title_selector_var', '')
        price_selector = self.config.get('price_selectors_var', '')

        try:
            title_element = container.find_element(By.CSS_SELECTOR, title_selector)
            title = title_element.text.strip()

            price_element = container.find_element(By.CSS_SELECTOR, price_selector)
            price_text = price_element.text.strip()
            price = parse_price(price_text, self.log_text)
            return title, price
        except NoSuchElementException:
            log_debug("Missing title or price element, skipping container", self.log_text)
            return None, None

    def construct_base_url(self):
        """Construct the base URL from configuration."""
        base_url = self.config.get('url_entry_var', '') + self.config.get('url_path_var', '')
        log_debug(f"Constructed base URL: {base_url}", self.log_text)
        return base_url

    def construct_url(self, page_number):
        """Construct the URL for the current page number."""
        page_param = self.config.get('page_param_var', '&page=')
        return f"{self.construct_base_url()}{page_param}{page_number}"

    def save_data_to_csv(self):
        """Save the collected data to a CSV file."""
        filename = self.config.get('csv_filename_var', 'scraped_data.csv')
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Product Title", "Primary Price"])
            writer.writerows(self.product_data)
        log_message(f"Data saved to CSV: {filename}", self.log_text, level="info")

    def update_progress(self, value):
        """Update the progress bar in the GUI."""
        self.root.after(0, lambda: self.progress_bar.config(value=value))

    def update_estimated_time(self, page_number, max_pages):
        """Update estimated time remaining based on current progress."""
        elapsed_time = time.time() - self.start_time
        remaining_pages = max_pages - page_number
        estimated_time = (elapsed_time / page_number) * remaining_pages
        mins, secs = divmod(int(estimated_time), 60)
        self.update_status_bar(f"Estimated time remaining: {mins}m {secs}s")

    def update_gui_label(self, label, text):
        """Update a GUI label asynchronously."""
        self.root.after(0, lambda: label.config(text=text))

    def update_status_bar(self, message):
        """Update the status bar asynchronously."""
        self.root.after(0, lambda: self.status_bar.config(text=message))

    def show_completion_message(self):
        """Show a completion message in the GUI."""
        from tkinter import messagebox
        self.root.after(0, lambda: messagebox.showinfo("Scraping Complete", "Scraping process completed successfully."))

    def stop_scraping(self):
        """Stops the scraping process gracefully."""
        self.stop_event.set()
        log_message("Scraping stopped by user.", self.log_text, level="info")

    def toggle_pause(self):
        """Toggle the pause state of the scraping process."""
        if self.pause_event.is_set():
            self.pause_event.clear()
            log_message("Scraping paused.", self.log_text, level="info")
        else:
            self.pause_event.set()
            log_message("Scraping resumed.", self.log_text, level="info")
