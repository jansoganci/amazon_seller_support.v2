"""Utility functions for analytics calculations."""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
from .exceptions import InvalidDateRangeError


def validate_date_range(
    start_date: datetime,
    end_date: datetime,
    max_range_days: Optional[int] = None
) -> None:
    """Validate a date range.
    
    Args:
        start_date: Start date
        end_date: End date
        max_range_days: Optional maximum number of days allowed
        
    Raises:
        InvalidDateRangeError: If date range is invalid
    """
    if start_date > end_date:
        raise InvalidDateRangeError("Start date must be before end date")
        
    if max_range_days:
        days_diff = (end_date - start_date).days
        if days_diff > max_range_days:
            raise InvalidDateRangeError(
                f"Date range cannot exceed {max_range_days} days"
            )


def group_data_by_period(
    data: List[Dict],
    date_field: str,
    group_by: str = 'daily'
) -> Dict[str, List[Dict]]:
    """Group data by time period.
    
    Args:
        data: List of data points
        date_field: Name of the date field in data points
        group_by: Period to group by (daily/weekly/monthly)
        
    Returns:
        Dict with period keys and lists of data points
    """
    grouped_data = {}
    
    for item in data:
        date = item[date_field]
        if isinstance(date, str):
            date = datetime.fromisoformat(date)
            
        if group_by == 'daily':
            key = date.strftime('%Y-%m-%d')
        elif group_by == 'weekly':
            key = date.strftime('%Y-W%W')
        else:  # monthly
            key = date.strftime('%Y-%m')
            
        if key not in grouped_data:
            grouped_data[key] = []
        grouped_data[key].append(item)
        
    return grouped_data


def calculate_percentage_change(
    current_value: Union[int, float],
    previous_value: Union[int, float]
) -> float:
    """Calculate percentage change between two values.
    
    Args:
        current_value: Current period value
        previous_value: Previous period value
        
    Returns:
        Percentage change as float
    """
    if previous_value == 0:
        return 100 if current_value > 0 else 0
        
    return ((current_value - previous_value) / previous_value) * 100
