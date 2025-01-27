"""Returns CSV validator module."""

from typing import Tuple
import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

from app.modules.returns.constants import (
    REQUIRED_COLUMNS, ERROR_MESSAGES,
    VALID_RETURN_CENTERS, VALID_RETURN_CARRIERS,
    VALID_TRACKING_PREFIXES
)
from .base import BaseCSVValidator

logger = logging.getLogger(__name__)

class ReturnCSVValidator(BaseCSVValidator):
    """Returns report CSV validator."""

    def __init__(self, user_id: int = None, store_id: int = None):
        """Initialize validator with user and store IDs."""
        super().__init__(user_id, store_id)
        self._required_columns = REQUIRED_COLUMNS

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate returns report data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        try:
            # Validate numeric columns
            numeric_columns = {
                'quantity': (int, 'Quantity must be greater than 0', lambda x: x > 0),
                'refund_amount': (Decimal, 'Refund amount cannot be negative', lambda x: x >= 0)
            }

            for col, (type_func, error_msg, validator) in numeric_columns.items():
                invalid_rows = []
                for idx, value in enumerate(df[col], 1):
                    try:
                        val = type_func(str(value))
                        if not validator(val):
                            invalid_rows.append(idx)
                    except (ValueError, InvalidOperation):
                        invalid_rows.append(idx)
                
                if invalid_rows:
                    return False, f"{error_msg} in rows: {', '.join(map(str, invalid_rows))}"

            # Validate date format
            invalid_dates = []
            for idx, date in enumerate(df['return_date'], 1):
                try:
                    pd.to_datetime(date)
                except ValueError:
                    invalid_dates.append(idx)
            
            if invalid_dates:
                return False, f"Invalid date format in rows: {', '.join(map(str, invalid_dates))}"

            # Validate return center
            invalid_centers = []
            for idx, center in enumerate(df['return_center'], 1):
                if center not in VALID_RETURN_CENTERS:
                    invalid_centers.append(idx)
            
            if invalid_centers:
                return False, ERROR_MESSAGES['INVALID_RETURN_CENTER']

            # Validate return carrier
            invalid_carriers = []
            for idx, carrier in enumerate(df['return_carrier'], 1):
                if carrier not in VALID_RETURN_CARRIERS:
                    invalid_carriers.append(idx)
            
            if invalid_carriers:
                return False, ERROR_MESSAGES['INVALID_RETURN_CARRIER']

            # Validate tracking number
            invalid_tracking = []
            for idx, tracking in enumerate(df['tracking_number'], 1):
                tracking_str = str(tracking)
                if not any(tracking_str.startswith(prefix) for prefix in VALID_TRACKING_PREFIXES):
                    invalid_tracking.append(idx)
            
            if invalid_tracking:
                return False, ERROR_MESSAGES['INVALID_TRACKING_NUMBER']

            return True, "Data validation successful"

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
