# logging_setup.py

import tkinter as tk
import queue
from logger_utility import LoggerUtility

# Create a centralized LoggerUtility instance
logger = LoggerUtility()

def log_message(message, log_text=None, level="info"):
    """
    Logs a message at the specified level and asynchronously updates the GUI if log_text is provided.

    Parameters:
    - message (str): The log message.
    - log_text (tk.Text, optional): Text widget for GUI logging.
    - level (str): Log level (info, warning, error, debug).
    """
    logger.log(level, message, log_text)
    if log_text:
        logger.log(level, f"Log message at level '{level}': {message}", log_text)

def log_error(message, log_text=None):
    """
    Logs an error message with GUI update.

    Parameters:
    - message (str): The error message.
    - log_text (tk.Text, optional): Text widget for GUI logging.
    """
    log_message(message, log_text, level="error")
    if log_text:
        logger.log("debug", f"Error logged: {message}", log_text)

def log_debug(message, log_text=None):
    """
    Logs a debug message with GUI update.

    Parameters:
    - message (str): The debug message.
    - log_text (tk.Text, optional): Text widget for GUI logging.
    """
    log_message(message, log_text, level="debug")

def flush_logs():
    """
    Ensures all log handlers flush their output, committing all logged messages.
    """
    try:
        for handler in logger.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
                logger.log("debug", "Log handler flushed", None)
        logger.log("info", "All log handlers flushed")
    except Exception as e:
        logger.log("error", f"Error flushing log handlers: {e}")

def backup_log_file(log_text=None):
    """
    Backs up the current log file by calling LoggerUtility's backup method.

    Parameters:
    - log_text (tk.Text, optional): Text widget for GUI logging.
    """
    try:
        logger.backup_log_file()
        log_message("Log file backed up successfully.", log_text, level="info")
    except Exception as e:
        log_error(f"Failed to backup log file: {e}", log_text)

def clear_log_file(log_text=None):
    """
    Clears the current log file after creating a backup.

    Parameters:
    - log_text (tk.Text, optional): Text widget for GUI logging.
    """
    try:
        logger.clear_log_file()
        log_message("Log file cleared for new session.", log_text, level="info")
    except Exception as e:
        log_error(f"Failed to clear log file: {e}", log_text)

def setup_gui_log_processor(root, gui_log_queue, log_text_widget):
    """
    Sets up the process for continuously updating the GUI log widget with messages from the log queue.

    Parameters:
    - root (tk.Tk): The main application window.
    - gui_log_queue (queue.Queue): Queue that holds log messages for the GUI.
    - log_text_widget (tk.Text): Text widget to display logs in the GUI.
    """
    def process_log_queue():
        """Processes queued log messages and updates the GUI."""
        while not gui_log_queue.empty():
            try:
                message, level = gui_log_queue.get_nowait()
                formatted_message = f"[{level.upper()}] {message}"
                log_text_widget.insert('end', formatted_message + '\n', level.upper())
                log_text_widget.see('end')
            except queue.Empty:
                break
            except Exception as e:
                log_error(f"Error updating log text widget: {e}")

        root.after(100, process_log_queue)  # Schedule next check for queued messages

    root.after(100, process_log_queue)  # Start processing the log queue
