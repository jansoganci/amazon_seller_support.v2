"""Validation utilities."""

from datetime import datetime
from typing import Optional, Tuple, Union

def validate_date_format(
    date_str: str,
    format_str: str = "%Y-%m-%d"
) -> Tuple[bool, Optional[datetime], Optional[str]]:
    """Validate date string format.
    
    Args:
        date_str: Date string to validate
        format_str: Expected date format (default: YYYY-MM-DD)
        
    Returns:
        Tuple containing:
        - bool: True if valid, False if invalid
        - datetime: Parsed datetime object if valid, None if invalid
        - str: Error message if invalid, None if valid
    """
    try:
        date_obj = datetime.strptime(date_str, format_str)
        return True, date_obj, None
    except ValueError:
        return False, None, f"Invalid date format. Expected format: {format_str}"

def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_days: int = 365
) -> Tuple[bool, Optional[str]]:
    """Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        max_days: Maximum allowed days between dates
        
    Returns:
        Tuple containing:
        - bool: True if valid, False if invalid
        - str: Error message if invalid, None if valid
    """
    if start_date > end_date:
        return False, "Start date must be before end date"
        
    days_diff = (end_date - start_date).days
    if days_diff > max_days:
        return False, f"Date range cannot exceed {max_days} days"
        
    return True, None

def validate_integer_range(
    value: Union[int, str],
    min_value: int,
    max_value: int,
    field_name: str = "Value"
) -> Tuple[bool, Optional[int], Optional[str]]:
    """Validate integer within range.
    
    Args:
        value: Integer value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        field_name: Name of the field for error messages
        
    Returns:
        Tuple containing:
        - bool: True if valid, False if invalid
        - int: Parsed integer if valid, None if invalid
        - str: Error message if invalid, None if valid
    """
    try:
        int_value = int(value)
        if min_value <= int_value <= max_value:
            return True, int_value, None
        return False, None, f"{field_name} must be between {min_value} and {max_value}"
    except (ValueError, TypeError):
        return False, None, f"{field_name} must be a valid integer"
