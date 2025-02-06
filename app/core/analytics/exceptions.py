"""Custom exceptions for the analytics engine."""

from typing import Optional


class AnalyticsError(Exception):
    """Base exception for all analytics-related errors."""
    
    def __init__(self, message: str, details: Optional[dict] = None):
        """Initialize the error.
        
        Args:
            message: Error message
            details: Optional dictionary with error details
        """
        super().__init__(message)
        self.details = details or {}


class MetricCalculationError(AnalyticsError):
    """Raised when metric calculation fails."""
    pass


class DataValidationError(AnalyticsError):
    """Raised when input data validation fails."""
    pass


class DataFetchError(AnalyticsError):
    """Raised when data fetching fails."""
    pass


class InvalidDateRangeError(AnalyticsError):
    """Raised when date range is invalid."""
    pass


class PermissionError(AnalyticsError):
    """Raised when user doesn't have permission for the operation."""
    pass
