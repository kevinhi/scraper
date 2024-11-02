# config_manager.py

import json
import os
import tkinter as tk  # Import tkinter for BooleanVar and StringVar support
from logging_setup import log_message, log_debug, log_error

CONFIG_FILE = 'config.json'
FIELD_VALUES_FILE = 'field_values.json'
BACKUP_CONFIG_FILE = 'config_backup.json'

def load_config_file(log_text=None):
    """Load configuration settings from 'config.json'."""
    if not os.path.exists(CONFIG_FILE):
        log_message(f"{CONFIG_FILE} not found. Using default configuration.", log_text, level="warning")
        return {}

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        log_message(f"Loaded configuration from '{CONFIG_FILE}'.", log_text, level="info")
        return config_data
    except json.JSONDecodeError as e:
        log_error(f"JSON format error in '{CONFIG_FILE}': {e}", log_text)
    except Exception as e:
        log_error(f"Unexpected error loading configuration: {e}", log_text)
    return {}

def save_config_file(config_data, log_text=None):
    """Save configuration settings to 'config.json'."""
    create_backup(CONFIG_FILE, BACKUP_CONFIG_FILE, log_text)
    
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        log_message(f"Configuration saved to '{CONFIG_FILE}'.", log_text, level="info")
        return True
    except TypeError as e:
        log_error(f"Non-serializable data in configuration: {e}", log_text)
    except Exception as e:
        log_error(f"Unexpected error saving configuration: {e}", log_text)
    return False

def load_field_values(field_vars, log_text=None):
    """Load field values into the GUI from configuration file."""
    config_data = load_config_file(log_text)
    for key, var in field_vars.items():
        if key in config_data:
            value = config_data[key]
            if hasattr(var, "set"):
                if isinstance(var, tk.BooleanVar):
                    var.set(bool(value))
                else:
                    var.set(value)
                log_debug(f"Set '{key}' to '{value}'", log_text)
            else:
                log_error(f"Cannot set '{key}'; not a Tkinter Variable", log_text)
        else:
            log_message(f"Config key '{key}' not found. Using default.", log_text, level="warning")

def save_field_values(field_vars, log_text=None):
    """Save current field values from the GUI to the configuration file."""
    config_data = {key: var.get() for key, var in field_vars.items() if hasattr(var, "get")}
    success = save_config_file(config_data, log_text)
    if success:
        log_message("Field values saved successfully.", log_text, level="info")
    else:
        log_error("Failed to save some field values.", log_text)

def load_previous_values(log_text=None):
    """Load previous field values for user convenience."""
    if not os.path.exists(FIELD_VALUES_FILE):
        log_message(f"{FIELD_VALUES_FILE} not found. Starting with empty values.", log_text, level="warning")
        return {}

    try:
        with open(FIELD_VALUES_FILE, 'r', encoding='utf-8') as f:
            previous_values = json.load(f)
        log_message(f"Loaded previous field values from '{FIELD_VALUES_FILE}'.", log_text, level="info")
        return previous_values
    except json.JSONDecodeError as e:
        log_error(f"JSON format error in '{FIELD_VALUES_FILE}': {e}", log_text)
    except Exception as e:
        log_error(f"Unexpected error loading previous values: {e}", log_text)
    return {}

def save_previous_values(previous_values, log_text=None):
    """Save previous field values to be loaded on next application start."""
    try:
        with open(FIELD_VALUES_FILE, 'w', encoding='utf-8') as f:
            json.dump(previous_values, f, indent=4)
        log_message(f"Previous field values saved to '{FIELD_VALUES_FILE}'.", log_text, level="info")
    except TypeError as e:
        log_error(f"Non-serializable data in previous values: {e}", log_text)
    except Exception as e:
        log_error(f"Unexpected error saving previous values: {e}", log_text)

def create_backup(original_file, backup_file, log_text=None):
    """Create a backup of the configuration file before overwriting it."""
    try:
        if os.path.exists(original_file):
            with open(original_file, 'r') as f:
                data = f.read()
            with open(backup_file, 'w') as f:
                f.write(data)
            log_message(f"Backup of '{original_file}' created as '{backup_file}'.", log_text, level="info")
    except Exception as e:
        log_error(f"Failed to create backup for '{original_file}': {e}", log_text)
