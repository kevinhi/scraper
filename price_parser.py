# price_parser.py

import re
from logging_setup import log_message, log_debug

def parse_price(price_text, log_text=None):
    """
    Parses and converts price text into a numeric format, correctly handling commas, periods, and various currency symbols.

    Parameters:
    - price_text (str): Raw price text from web scraping.
    - log_text (tk.Text, optional): Log widget to log messages.

    Returns:
    - float or None: Parsed price as a floating-point number, or None if parsing failed.
    """
    original_text = price_text.strip()
    if log_text:
        log_debug(f"Received price text for parsing: '{original_text}'", log_text)

    if not original_text:
        if log_text:
            log_message("Price text is empty, cannot parse.", log_text, level="warning")
        return None

    try:
        # Remove currency symbols and keep only numbers, commas, and periods
        cleaned_text = re.sub(r'[^\d,.\n]', '', original_text)
        if log_text:
            log_debug(f"Removed non-numeric characters: '{cleaned_text}'", log_text)

        # Replace newlines and whitespace with periods (to normalize decimal points)
        cleaned_text = cleaned_text.replace('\n', '.').replace('\r', '.').strip()
        if log_text:
            log_debug(f"Replaced newlines and extra spaces: '{cleaned_text}'", log_text)

        # Handle cases with both commas and periods
        if ',' in cleaned_text and '.' in cleaned_text:
            if cleaned_text.index(',') < cleaned_text.index('.'):
                # Comma appears before period; treat comma as thousand separator
                cleaned_text = cleaned_text.replace(',', '')
            else:
                # Treat comma as decimal separator if after period
                cleaned_text = cleaned_text.replace(',', '')

        # Handle cases with only commas
        elif ',' in cleaned_text and '.' not in cleaned_text:
            # Single comma, no period; treat comma as decimal separator
            if cleaned_text.count(',') == 1:
                cleaned_text = cleaned_text.replace(',', '.')
            else:
                # Multiple commas; treat commas as thousand separators
                cleaned_text = cleaned_text.replace(',', '')

        # Convert to float
        parsed_price = float(cleaned_text)
        if log_text:
            log_message(f"Parsed price: {parsed_price}", log_text, level="info")
        return parsed_price

    except ValueError:
        if log_text:
            log_error(f"Failed to parse price from '{original_text}': Format not recognized", log_text)
        return None
