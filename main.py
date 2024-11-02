# main.py

import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from logging_setup import log_message, log_debug, log_error, flush_logs, setup_gui_log_processor
from scraper_manager import ScraperManager
from config_manager import (
    load_field_values,
    save_field_values,
    load_previous_values,
    save_previous_values,
    load_config_file,
    save_config_file
)
import os
import json

WINDOW_CONFIG_FILE = 'window_config.json'

class Tooltip:
    """Class to create a tooltip for a given widget."""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.tooltip_window = None

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip_window, text=self.text, background="yellow", relief="solid", borderwidth=1, font=("Helvetica", "8", "normal"))
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

def main():
    root = tk.Tk()
    root.title("Product Scraper")
    
    # Restore window size if previously saved
    window_config = load_window_config()
    root.geometry(f"{window_config.get('width', 800)}x{window_config.get('height', 600)}")
    root.minsize(800, 860)

    # GUI Elements and Styling
    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TLabel', font=('Helvetica', 10))
    style.configure('TButton', font=('Helvetica', 10))
    style.configure('TEntry', font=('Helvetica', 10))
    style.configure('TCombobox', font=('Helvetica', 10))
    style.configure('TNotebook.Tab', font=('Helvetica', 10))

    # Logging Queue Setup
    gui_log_queue = queue.Queue()
    setup_gui_log_processor(root, gui_log_queue, log_text_widget=None)

    # Status Bar
    status_bar = tk.Label(root, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # Control Frame for Buttons and Labels
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
    page_number_label = ttk.Label(control_frame, text="Page: N/A")
    page_number_label.pack(side=tk.LEFT, padx=5)
    containers_found_label = ttk.Label(control_frame, text="Containers Found: N/A")
    containers_found_label.pack(side=tk.LEFT, padx=5)
    total_products_found_label = ttk.Label(control_frame, text="Products Found: 0")
    total_products_found_label.pack(side=tk.LEFT, padx=5)
    total_products_skipped_label = ttk.Label(control_frame, text="Products Skipped: 0")
    total_products_skipped_label.pack(side=tk.LEFT, padx=5)
    user_agent_label = ttk.Label(control_frame, text=f"User-Agent: {''}")
    user_agent_label.pack(side=tk.LEFT, padx=5)

    # Define Variables for Form Fields
    field_vars = initialize_field_vars()

    # Load previous values and last selected values
    previous_values = load_previous_values(log_text=None)
    load_field_values(field_vars, log_text=None)
    user_agent_label.config(text=f"User-Agent: {field_vars['user_agent_var'].get()}")

    # GUI Menus
    setup_menu(root)

    # Notebook for Tabs
    notebook = ttk.Notebook(root)
    notebook.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    general_frame = ttk.Frame(notebook)
    advanced_frame = ttk.Frame(notebook)
    notebook.add(general_frame, text='General Settings')
    notebook.add(advanced_frame, text='Advanced Settings')

    # Set up fields in each tab
    setup_general_settings(general_frame, field_vars, previous_values)
    setup_advanced_settings(advanced_frame, field_vars, previous_values)

    # Scraper Manager Initialization
    scraper_manager = ScraperManager(
        config={key: var.get() for key, var in field_vars.items()},
        log_text=gui_log_queue,
        results_text=None,
        progress_bar=None,
        root=root,
        user_agent_label=user_agent_label,
        status_bar=status_bar,
        containers_found_label=containers_found_label,
        page_number_label=page_number_label,
        total_products_found_label=total_products_found_label,
        total_products_skipped_label=total_products_skipped_label,
        selectors_found_label=None
    )

    # Scraping Controls
    create_scraping_buttons(control_frame, scraper_manager, gui_log_queue)

    # Results and Log Display
    results_text, log_text = setup_display_widgets(root, gui_log_queue)

    # Schedule GUI log processor
    root.after(100, process_gui_log_queue, root, gui_log_queue, log_text)

    # Configure Window Resize Event for Saving Size
    root.bind("<Configure>", lambda event: save_window_config(root))

    # Start the GUI event loop
    root.mainloop()

def initialize_field_vars():
    """Initialize field variables for form fields."""
    field_names = [
        'entry_var', 'page_param_var', 'max_pages_var', 'price_var',
        'url_entry_var', 'url_path_var', 'url_append_params_var', 'csv_filename_var',
        'container_selector_var', 'title_selector_var', 'price_selectors_var',
        'secondary_price_indicator_var', 'secondary_price_selectors_var',
        'scroll_delay_var', 'element_wait_timeout_var', 'display_no_price_var',
        'user_agent_change_interval_var', 'user_agent_var', 'expected_containers_var',
        'expected_number_var', 'potential_selectors_var'
    ]
    field_vars = {name: tk.StringVar() for name in field_names}
    field_vars['display_no_price_var'] = tk.BooleanVar()
    return field_vars

def setup_general_settings(frame, field_vars, previous_values):
    """Create general settings fields with tooltips in the GUI."""
    general_fields = [
        ('entry_var', 'Search Query:', 'Keywords to search for products'),
        ('page_param_var', 'Page Parameter:', 'Parameter for pagination in URL'),
        ('max_pages_var', 'Max Pages:', 'Maximum number of pages to scrape'),
        ('price_var', 'Price Range:', 'Price filter for products'),
        ('url_entry_var', 'Base URL:', 'Base URL of the site to scrape'),
        ('url_path_var', 'URL Path:', 'Path after the base URL for specific searches'),
        ('csv_filename_var', 'CSV Filename:', 'Name of the CSV file for saving results')
    ]

    for row, (var_name, label_text, tooltip_text) in enumerate(general_fields):
        variable = field_vars[var_name]
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        entry = ttk.Combobox(frame, textvariable=variable, values=previous_values.get(var_name, []), width=30)
        entry.grid(row=row, column=1, pady=5, padx=5)
        entry.set(variable.get())
        Tooltip(entry, tooltip_text)

def setup_advanced_settings(frame, field_vars, previous_values):
    """Create advanced settings fields with tooltips in the GUI."""
    advanced_fields = [
        ('container_selector_var', 'Container Selector:', 'CSS selector for the product container'),
        ('title_selector_var', 'Title Selector:', 'CSS selector for product title'),
        ('price_selectors_var', 'Price Selector:', 'CSS selector for primary price'),
        ('scroll_delay_var', 'Scroll Delay:', 'Time delay for page scrolling'),
        ('element_wait_timeout_var', 'Element Timeout:', 'Timeout for waiting for elements to load'),
        ('user_agent_var', 'User Agent:', 'User-Agent string for scraping requests')
    ]

    for row, (var_name, label_text, tooltip_text) in enumerate(advanced_fields):
        variable = field_vars[var_name]
        label = ttk.Label(frame, text=label_text)
        label.grid(row=row, column=0, sticky=tk.W, pady=5, padx=5)
        entry = ttk.Combobox(frame, textvariable=variable, values=previous_values.get(var_name, []), width=30)
        entry.grid(row=row, column=1, pady=5, padx=5)
        entry.set(variable.get())
        Tooltip(entry, tooltip_text)

def setup_menu(root):
    """Create and configure the menu bar."""
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='File', menu=file_menu)
    file_menu.add_command(label='Open Config', command=lambda: open_config())
    file_menu.add_command(label='Save Config', command=lambda: save_config())
    file_menu.add_separator()
    file_menu.add_command(label='Exit', command=root.quit)
    help_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label='Help', menu=help_menu)
    help_menu.add_command(label='Documentation', command=lambda: open_documentation())
    help_menu.add_command(label='About', command=lambda: show_about())

def create_scraping_buttons(control_frame, scraper_manager, gui_log_queue):
    """Create Start, Stop, and Pause buttons for scraping control."""
    ttk.Button(control_frame, text="Start Scraping", command=lambda: start_scraping(scraper_manager)).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Stop Scraping", command=scraper_manager.stop_scraping).pack(side=tk.LEFT, padx=5)
    ttk.Button(control_frame, text="Pause", command=scraper_manager.toggle_pause).pack(side=tk.LEFT, padx=5)

def start_scraping(scraper_manager):
    """Starts the scraping process in a new thread."""
    threading.Thread(target=scraper_manager.start_scraping, daemon=True).start()
    flush_logs()

def setup_display_widgets(root, gui_log_queue):
    """Set up text areas for results and logging."""
    results_frame = ttk.Frame(root)
    results_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    results_text = tk.Text(results_frame, height=10, wrap=tk.WORD)
    results_text.pack(fill=tk.BOTH, expand=True)
    log_frame = ttk.Frame(root)
    log_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)
    log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)
    log_text.tag_configure("DEBUG", foreground="blue")
    log_text.tag_configure("INFO", foreground="black")
    log_text.tag_configure("WARNING", foreground="orange")
    log_text.tag_configure("ERROR", foreground="red")
    log_text.tag_configure("CRITICAL", foreground="red", underline=1)
    return results_text, log_text

def load_window_config():
    """Loads window configuration for size and position."""
    if os.path.exists(WINDOW_CONFIG_FILE):
        with open(WINDOW_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_window_config(root):
    """Saves the window size and position configuration."""
    window_config = {'width': root.winfo_width(), 'height': root.winfo_height()}
    with open(WINDOW_CONFIG_FILE, 'w') as f:
        json.dump(window_config, f)

def process_gui_log_queue(root, gui_log_queue, log_text_widget):
    """Processes log messages from the queue and updates the log text widget."""
    while not gui_log_queue.empty():
        try:
            message, level = gui_log_queue.get_nowait()
            formatted_message = f"[{level.upper()}] {message}"
            log_text_widget.insert('end', formatted_message + '\n', level.upper())
            log_text_widget.see('end')
        except queue.Empty:
            break
    root.after(100, process_gui_log_queue, root, gui_log_queue, log_text_widget)

if __name__ == "__main__":
    main()
