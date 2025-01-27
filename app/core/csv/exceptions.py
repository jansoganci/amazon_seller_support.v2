"""CSV processing exceptions."""

class CSVError(Exception):
    """Base exception for CSV processing errors."""
    pass

class CSVValidationError(CSVError):
    """Exception raised when CSV validation fails."""
    pass
