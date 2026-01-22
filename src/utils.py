import pandas as pd
from datetime import datetime

def safe_int(value, default=0):
    """Convert value to int safely."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def safe_float(value, default=0.0):
    """Convert value to float safely."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def parse_date(date_str, fmt="%Y-%m-%dT%H:%M:%SZ"):
    """Parse date string to datetime object safely."""
    try:
        return datetime.strptime(date_str, fmt)
    except (ValueError, TypeError):
        return None

def clean_string(text):
    """Remove leading/trailing whitespace and handle None."""
    if text is None:
        return ""
    return str(text).strip()

def validate_dataframe(df, required_columns):
    """Ensure DataFrame has the required columns and is not empty."""
    if df.empty:
        return False
    for col in required_columns:
        if col not in df.columns:
            return False
    return True
