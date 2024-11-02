# driver_utils.py

import os
import sys
import random
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import WebDriverException
from logging_setup import log_message, log_debug

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15",
    # Add more user agents as needed
]

def initialize_driver(user_agent=None, log_text=None, reuse_driver=False):
    """
    Initializes the Firefox WebDriver with dynamic user-agent and optional reuse.

    Parameters:
    - user_agent (str, optional): User-agent string; defaults to random choice if not provided.
    - log_text (tk.Text): Log widget in the GUI to log messages.
    - reuse_driver (bool): Flag to reuse an existing driver if possible.

    Returns:
    - driver (webdriver.Firefox or None): Initialized WebDriver instance or None on failure.
    """
    if reuse_driver:
        existing_driver = check_existing_driver()
        if existing_driver:
            log_message("Reusing existing WebDriver instance.", log_text, level="info")
            return existing_driver

    if not user_agent:
        user_agent = random.choice(USER_AGENTS)
    log_debug(f"Selected User-Agent: {user_agent}", log_text)

    driver_path = check_geckodriver(log_text)
    if not driver_path:
        log_message("Cannot proceed without Geckodriver. Exiting driver initialization.", log_text, level="error")
        return None

    try:
        options = Options()
        options.add_argument('--headless')
        options.set_preference("general.useragent.override", user_agent)

        driver = webdriver.Firefox(service=Service(driver_path), options=options)
        log_message("WebDriver initialized with selected User-Agent.", log_text)
        random_delay = random.uniform(2, 5)
        log_debug(f"Simulating delay of {random_delay:.2f} seconds.", log_text)
        time.sleep(random_delay)

        return driver
    except WebDriverException as e:
        log_message(f"Error initializing WebDriver: {e}", log_text, level="error")
        return None

def check_geckodriver(log_text):
    """
    Checks for Geckodriver in the current directory and system PATH.

    Parameters:
    - log_text (tk.Text): Log widget in the GUI to log messages.

    Returns:
    - str or None: Path to Geckodriver executable if found, otherwise None.
    """
    driver_name = 'geckodriver.exe' if sys.platform == "win32" else 'geckodriver'
    driver_path = os.path.join(os.getcwd(), driver_name)

    if os.path.exists(driver_path):
        log_message(f"Geckodriver found at: {driver_path}", log_text)
        return driver_path

    for path in os.environ["PATH"].split(os.pathsep):
        full_path = os.path.join(path, driver_name)
        if os.path.exists(full_path):
            log_message(f"Geckodriver found in system PATH at: {full_path}", log_text)
            return full_path

    log_message("Error: Geckodriver not found.", log_text, level="error")
    return None

def check_existing_driver():
    """
    Check if there’s an existing WebDriver instance to reuse.

    Returns:
    - WebDriver instance if available, otherwise None.
    """
    # Placeholder for functionality to detect and reuse existing driver.
    return None
