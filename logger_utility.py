# logger_utility.py

import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler
import queue

class LoggerUtility:
    """
    A centralized logger utility for consistent logging across the application.
    """
    _instance = None  # Singleton instance

    def __new__(cls, log_file='scraping.log', log_level=logging.DEBUG, log_queue=None):
        if cls._instance is None:
            cls._instance = super(LoggerUtility, cls).__new__(cls)
            cls._instance._initialize(log_file, log_level, log_queue)
        return cls._instance

    def _initialize(self, log_file, log_level, log_queue):
        """
        Initializes the logger with file and console handlers.
        """
        self.logger = logging.getLogger('scraper')
        self.logger.setLevel(log_level)
        self.log_queue = log_queue

        # File handler with rotation
        file_handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=3)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        # Console handler for basic info
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s - %(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def log(self, level, message, log_text=None):
        """
        Logs a message at the specified level and optionally updates the GUI log widget.
        """
        log_methods = {
            "info": self.logger.info,
            "warning": self.logger.warning,
            "error": self.logger.error,
            "debug": self.logger.debug,
            "critical": self.logger.critical,
        }
        log_method = log_methods.get(level.lower(), self.logger.info)
        log_method(message)

        if self.log_queue is not None:
            self.log_queue.put((message, level))

        if log_text is not None and hasattr(log_text, 'insert'):
            self._log_to_gui(log_text, message, level)

    def _log_to_gui(self, log_text, message, level):
        """
        Logs a message to a Tkinter Text widget for GUI updates.
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        formatted_message = f"[{timestamp}] {level.upper()}: {message}"
        log_text.insert('end', formatted_message + '\n', level.upper())
        log_text.see('end')

    @staticmethod
    def backup_log_file():
        """
        Creates a backup of the current log file.
        """
        backup_filename = f"scraping_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        try:
            if os.path.exists('scraping.log'):
                os.rename('scraping.log', backup_filename)
                LoggerUtility().log("info", f"Log file backed up to: {backup_filename}")
        except Exception as e:
            LoggerUtility().log("error", f"Failed to backup log file: {e}")

    @staticmethod
    def clear_log_file():
        """
        Clears the contents of the log file and backs up the previous log.
        """
        LoggerUtility.backup_log_file()
        try:
            with open('scraping.log', 'w', encoding='utf-8') as log_file:
                log_file.truncate(0)
            LoggerUtility().log("info", "Log file cleared for new session.")
        except Exception as e:
            LoggerUtility().log("error", f"Failed to clear log file: {e}")

    def flush_logs(self):
        """
        Flushes all log handlers to ensure logs are written.
        """
        for handler in self.logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
