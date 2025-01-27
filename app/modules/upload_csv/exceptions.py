"""CSV processing exceptions."""

class CSVError(Exception):
    """Base exception for CSV processing errors."""
    pass

class CSVValidationError(CSVError):
    """Exception raised for CSV validation errors."""
    pass

class CSVProcessingError(CSVError):
    """Exception raised for CSV processing errors."""
    pass 