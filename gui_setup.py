# gui_setup.py

import tkinter as tk
from tkinter import ttk
from logging_setup import log_message
import queue

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

def setup_gui(root, field_vars, previous_values, gui_log_queue):
    """Set up the main GUI structure and components."""
    # Create frames for layout organization
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Notebook for Tabs
    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    general_frame = ttk.Frame(notebook)
    advanced_frame = ttk.Frame(notebook)
    notebook.add(general_frame, text='General Settings')
    notebook.add(advanced_frame, text='Advanced Settings')

    # Field Definitions for General and Advanced Settings
    setup_general_settings(general_frame, field_vars, previous_values)
    setup_advanced_settings(advanced_frame, field_vars, previous_values)

    # Logging and Status Text Area
    setup_log_area(root, gui_log_queue)

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

def setup_log_area(root, gui_log_queue):
    """Create a text area for displaying log messages."""
    log_frame = ttk.Frame(root)
    log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    log_label = ttk.Label(log_frame, text="Log Messages:")
    log_label.pack(anchor="w")
    log_text = tk.Text(log_frame, height=10, wrap=tk.WORD)
    log_text.pack(fill=tk.BOTH, expand=True)

    # Set up text tags for log levels
    log_text.tag_configure("DEBUG", foreground="blue")
    log_text.tag_configure("INFO", foreground="black")
    log_text.tag_configure("WARNING", foreground="orange")
    log_text.tag_configure("ERROR", foreground="red")
    log_text.tag_configure("CRITICAL", foreground="red", underline=1)

    # Start log processing
    process_log_queue(root, gui_log_queue, log_text)

def process_log_queue(root, gui_log_queue, log_text_widget):
    """Processes log messages from the queue and updates the log text widget."""
    while not gui_log_queue.empty():
        try:
            message, level = gui_log_queue.get_nowait()
            formatted_message = f"[{level.upper()}] {message}"
            log_text_widget.insert('end', formatted_message + '\n', level.upper())
            log_text_widget.see('end')
        except queue.Empty:
            break
    root.after(100, process_log_queue, root, gui_log_queue, log_text_widget)
