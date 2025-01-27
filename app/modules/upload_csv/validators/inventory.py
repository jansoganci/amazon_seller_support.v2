"""Inventory CSV validator module."""

from typing import Tuple
import pandas as pd
from decimal import Decimal, InvalidOperation
import logging

from app.modules.inventory.constants import REQUIRED_COLUMNS, ERROR_MESSAGES
from .base import BaseCSVValidator

logger = logging.getLogger(__name__)

class InventoryCSVValidator(BaseCSVValidator):
    """Inventory report CSV validator."""

    def __init__(self, user_id: int = None, store_id: int = None):
        """Initialize validator with user and store IDs."""
        super().__init__(user_id, store_id)
        self._required_columns = REQUIRED_COLUMNS

    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate inventory report data.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        try:
            # Validate numeric columns
            numeric_columns = {
                'sellable_quantity': int,
                'unsellable_quantity': int,
                'reserved_quantity': int,
                'restock_level': int,
                'inbound_quantity': int
            }

            for col, type_func in numeric_columns.items():
                invalid_rows = []
                for idx, value in enumerate(df[col], 1):
                    if pd.notna(value):  # Only validate non-null values
                        try:
                            type_func(str(value))
                        except (ValueError, InvalidOperation):
                            invalid_rows.append(idx)
                
                if invalid_rows:
                    return False, f"Invalid {col} values in rows: {', '.join(map(str, invalid_rows))}"

            # Validate date format
            invalid_dates = []
            for idx, date in enumerate(df['snapshot_date'], 1):
                try:
                    pd.to_datetime(date)
                except ValueError:
                    invalid_dates.append(idx)
            
            if invalid_dates:
                return False, f"Invalid date format in rows: {', '.join(map(str, invalid_dates))}"

            return True, "Data validation successful"

        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}" 