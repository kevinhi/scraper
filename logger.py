# logger.py

import logging
import time
import threading
from logging.handlers import RotatingFileHandler
from logging_setup import log_message, log_debug, log_error
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from driver_utils import initialize_driver

LOG_FILE = 'scraper.log'
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 3  # Keep up to 3 backup log files

# Initialize rotating log handler
log_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_SIZE, backupCount=BACKUP_COUNT)
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(log_formatter)

logger = logging.getLogger('ScraperLogger')
logger.setLevel(logging.DEBUG)
logger.addHandler(log_handler)

class ScraperManager:
    def __init__(self, config, log_text, results_text, progress_bar, root, user_agent_label, status_bar):
        self.config = config
        self.log_text = log_text
        self.results_text = results_text
        self.progress_bar = progress_bar
        self.root = root
        self.user_agent_label = user_agent_label
        self.status_bar = status_bar
        self.driver = None
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()
        self.pause_event.set()

    def set_gui_labels(self, containers_found_label, page_number_label, total_products_found_label, total_products_skipped_label, selectors_found_label):
        """Set the GUI labels for displaying scraping progress and statistics."""
        self.containers_found_label = containers_found_label
        self.page_number_label = page_number_label
        self.total_products_found_label = total_products_found_label
        self.total_products_skipped_label = total_products_skipped_label
        self.selectors_found_label = selectors_found_label

    def start_scraping(self):
        """Starts the scraping process, including driver initialization and URL navigation."""
        logger.info("Scraping started.")
        self.stop_event.clear()
        self.pause_event.set()

        try:
            user_agent = self.config.get('user_agent_var', '')
            self.driver = initialize_driver(user_agent, self.log_text)
            if not self.driver:
                logger.error("Failed to initialize WebDriver.")
                return

            self.user_agent_label.config(text=f"User-Agent: {user_agent}")
            max_pages = int(self.config.get('max_pages_var', 1))
            base_url = self.config.get('url_entry_var', '') + self.config.get('url_path_var', '')

            for page_num in range(1, max_pages + 1):
                if self.stop_event.is_set():
                    logger.warning("Scraping stopped by user.")
                    break

                while not self.pause_event.is_set():
                    time.sleep(0.1)  # Pause the scraping process if paused

                current_url = f"{base_url}{self.config.get('page_param_var', '')}{page_num}"
                logger.info(f"Navigating to URL: {current_url}")
                self.driver.get(current_url)
                time.sleep(int(self.config.get('scroll_delay_var', 25)) / 1000)

                container_selector = self.config.get('container_selector_var', '')
                try:
                    containers = self.driver.find_elements(By.CSS_SELECTOR, container_selector)
                    self.containers_found_label.config(text=f"Containers Found: {len(containers)}")
                    logger.debug(f"Found {len(containers)} product containers on page {page_num}")
                except NoSuchElementException:
                    logger.error(f"No containers found with selector: {container_selector}")
                    continue

                products_found = 0
                products_skipped = 0
                for container in containers:
                    if self.stop_event.is_set():
                        break

                    try:
                        title_selector = self.config.get('title_selector_var', '')
                        title_element = container.find_element(By.CSS_SELECTOR, title_selector)
                        title = title_element.text.strip()

                        price_selector = self.config.get('price_selectors_var', '')
                        price_element = container.find_element(By.CSS_SELECTOR, price_selector)
                        price = price_element.text.strip()

                        self.results_text.insert("end", f"Title: {title}, Price: {price}\n")
                        products_found += 1
                    except NoSuchElementException:
                        products_skipped += 1
                        logger.debug("Skipping container due to missing elements")
                        continue

                self.total_products_found_label.config(text=f"Products Found: {products_found}")
                self.total_products_skipped_label.config(text=f"Products Skipped: {products_skipped}")
                self.page_number_label.config(text=f"Page: {page_num}")

                progress = int((page_num / max_pages) * 100)
                self.progress_bar['value'] = progress
                self.root.update_idletasks()

        except TimeoutException as e:
            logger.error(f"Page load timed out: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
        finally:
            self.stop_scraping()

    def stop_scraping(self):
        """Stops the scraping process and closes the WebDriver."""
        logger.info("Stopping scraping")
        self.stop_event.set()
        if self.driver:
            self.driver.quit()
            logger.info("WebDriver closed.")
        self.status_bar.config(text="Scraping stopped.")

    def pause_scraping(self):
        """Pauses the scraping process."""
        logger.info("Pausing scraping")
        self.pause_event.clear()

    def resume_scraping(self):
        """Resumes the scraping process."""
        logger.info("Resuming scraping")
        self.pause_event.set()
