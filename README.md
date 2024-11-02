# scraper

# **Product Scraper Application**

The **Product Scraper Application** is a desktop-based GUI tool designed to scrape product information from e-commerce websites such as Amazon. It allows users to configure scraping parameters, initiate the scraping process, and view results in real-time within the GUI. Scraped data can be saved to a CSV file for further analysis.

---

## **Table of Contents**
1. [Features](#features)
2. [File Structure](#file-structure)
3. [Technical Specifications](#technical-specifications)
4. [Setup Instructions](#setup-instructions)
5. [Usage](#usage)
6. [Configuration Details](#configuration-details)
7. [Error Handling and Logging](#error-handling-and-logging)
8. [Future Improvements](#future-improvements)
9. [License](#license)

---

## **Features**

- **User-Friendly GUI**: Built with Tkinter, the interface provides easy controls for configuring scraping parameters.
- **Real-Time Logging and Status Updates**: View detailed logs and progress information as the scraping progresses.
- **Configuration Management**: Save and load user configurations, with fields pre-filled based on previous inputs.
- **Data Extraction**: Scrapes product titles, prices, and other details from e-commerce platforms.
- **Export to CSV**: Save scraped data to a CSV file for analysis.
- **Error Handling and Resilience**: Manages web driver errors, invalid selectors, and other runtime issues gracefully.
- **Window Size Memory**: Remembers GUI window size across sessions.

---

## **File Structure**

The application is organized into modular components, each serving a specific purpose.

### **1. `main.py`**
   - Entry point for the application.
   - Sets up the Tkinter GUI, initializes logging, and handles user interactions.
   - Handles window size memory, logging setup, and starts the main event loop.

### **2. `scraper_manager.py`**
   - Manages the scraping process, including initializing the web driver, navigating pages, extracting data, and updating the GUI.
   - Contains functions for starting, pausing, resuming, and stopping the scraper.
   - Handles selectors, extracts product data, and saves results to CSV.

### **3. `config_manager.py`**
   - Manages loading and saving of configuration settings, including backup of existing configurations.
   - Loads and saves previous field values to pre-fill fields in the GUI.

### **4. `logger.py`**
   - Sets up log file rotation and manages log levels (info, warning, error, debug).
   - Logs messages to both the console and the GUI.

### **5. `logging_setup.py`**
   - Provides centralized functions for logging to ensure consistent log handling across modules.
   - Supports asynchronous logging to avoid freezing the GUI.

### **6. `driver_utils.py`**
   - Initializes and configures the Selenium WebDriver with options like user-agent and headless mode.
   - Includes functionality to reuse WebDriver instances and to verify driver activity.

### **7. `price_parser.py`**
   - Parses price strings from websites and converts them to numerical values.
   - Handles different currency formats, symbols, commas, and periods.

### **8. `gui_setup.py`**
   - Sets up the layout and components of the Tkinter GUI, including tooltips for better usability.
   - Creates frames, tabs, buttons, text areas for logging, and input fields for settings.

---

## **Technical Specifications**

- **Programming Language**: Python 3.x
- **GUI Framework**: Tkinter
- **Web Automation**: Selenium WebDriver
   - **Browser Driver**: Geckodriver for Firefox (can be configured for other browsers)
- **Data Storage**: CSV format for data output
- **Dependencies**:
  - Python Packages: `tkinter`, `selenium`, `json`, `csv`, `threading`, `queue`, `re`, `datetime`

### **System Requirements**

- **Python Version**: 3.7 or higher
- **Selenium WebDriver**: Geckodriver is required and should be in the system PATH or application directory.

---

## **Setup Instructions**

### **1. Clone the Repository**

```bash
git clone <repository-url>
cd product-scraper-application
```

### **2. Install Dependencies**

```bash
pip install selenium
```

### **3. Download Geckodriver**

- [Download Geckodriver](https://github.com/mozilla/geckodriver/releases)
- Place it in the application directory or add it to your system PATH.

### **4. Run the Application**

```bash
python main.py
```

---

## **Usage**

1. **Configure Scraping Parameters**:
   - Launch the application and fill in fields like the search query, maximum pages, and price range.
   - Specify the selectors for product title and price.

2. **Start Scraping**:
   - Click "Start Scraping" to begin the process.
   - View real-time progress updates, including product counts and current page.

3. **Pause/Resume/Stop Scraping**:
   - Use the "Pause", "Resume", or "Stop" buttons to control the process.

4. **View and Save Logs**:
   - Logs are displayed in the GUI and saved to a file (`scraper.log`), with automatic rotation to prevent large log files.

5. **Save Results**:
   - Scraped data is saved to a CSV file (`output.csv` by default) for further analysis.

---

## **Configuration Details**

- **General Settings**:
   - `Search Query`: Keywords for the product search.
   - `Max Pages`: Maximum number of pages to scrape.
   - `Price Range`: Price filter for the products.
   - `Base URL` and `URL Path`: URL details for the target site.
   - `CSV Filename`: Name of the output file.

- **Advanced Settings**:
   - `Container Selector`: CSS selector for the main product container.
   - `Title Selector`: CSS selector for product title.
   - `Price Selector`: CSS selector for product price.
   - `Scroll Delay`: Time delay for page scrolling.
   - `Element Timeout`: Maximum wait time for page elements to load.

---

## **Error Handling and Logging**

- **Error Handling**:
   - The application uses specific error handling for Selenium exceptions, JSON loading errors, and invalid configurations.
   - Errors encountered during scraping are logged and displayed in the GUI.
   - Graceful shutdown of the WebDriver on error ensures resources are released properly.

- **Logging**:
   - Logs are saved with a rotating file handler (`scraper.log`) to avoid large log files.
   - Logging levels (INFO, DEBUG, ERROR) are used to differentiate the importance of messages.
   - Asynchronous logging ensures that log updates do not freeze the GUI.
   - Logs include time-stamped messages for detailed tracking.

---

## **Future Improvements**

- **Multithreaded Scraping**: Speed up data collection by scraping multiple pages in parallel.
- **Proxy and User-Agent Rotation**: Add support for rotating proxies and user-agents to avoid IP bans.
- **Database Storage**: Provide an option to store data in a database (e.g., SQLite) for better data management.
- **Additional Export Formats**: Enable export to formats like JSON or Excel.
- **Scheduled Scraping**: Allow users to schedule scraping tasks to run at specific times.

---

## **License**

This project is licensed under the MIT License.

