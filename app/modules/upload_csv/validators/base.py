"""Base CSV validator module."""

from typing import Tuple, List, Dict, Any
import pandas as pd
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging

from app.extensions import db
from app.models import Store
from ..exceptions import CSVValidationError
from ..constants import CSV_COLUMNS, ERROR_MESSAGES

logger = logging.getLogger(__name__)

class BaseCSVValidator:
    """Base class for all CSV validators."""

    def __init__(self, user_id: int = None, store_id: int = None):
        """Initialize validator.
        
        Args:
            user_id: User ID for validation
            store_id: Store ID for validation
        """
        self.user_id = user_id
        self.store_id = store_id
        
    def validate_file_type(self, file) -> Tuple[bool, str]:
        """Validate file type is CSV."""
        if not file.filename.endswith('.csv'):
            return False, ERROR_MESSAGES['invalid_file_type']
        return True, ""
        
    def validate_csv(self, df: pd.DataFrame, report_type: str) -> Tuple[bool, List[str]]:
        """Validate CSV structure and data."""
        errors = []
        
        # Check required columns
        required_columns = CSV_COLUMNS.get(report_type, {}).get('required', [])
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            errors.append(ERROR_MESSAGES['missing_columns'].format(', '.join(missing_columns)))
            
        # Check for empty dataframe
        if df.empty:
            errors.append(ERROR_MESSAGES['file_empty'])
            
        # Validate numeric columns
        numeric_errors = self._validate_numeric_columns(df, report_type)
        errors.extend(numeric_errors)
        
        # Validate date columns
        date_errors = self._validate_date_columns(df, report_type)
        errors.extend(date_errors)
        
        # Validate boolean columns (if any)
        boolean_errors = self._validate_boolean_columns(df, report_type)
        errors.extend(boolean_errors)
        
        return len(errors) == 0, errors

    def _validate_numeric_columns(self, df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate numeric columns have correct data types."""
        errors = []
        numeric_columns = CSV_COLUMNS.get(report_type, {}).get('numeric', {})
        
        for col, dtype in numeric_columns.items():
            if col not in df.columns:
                continue
                
            try:
                if dtype == int:
                    df[col] = pd.to_numeric(df[col], downcast='integer')
                elif dtype == Decimal:
                    df[col] = df[col].apply(lambda x: Decimal(str(x)))
            except (ValueError, InvalidOperation):
                errors.append(f"Column '{col}' contains invalid numeric values")
                
        return errors

    def _validate_date_columns(self, df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate date columns have correct format."""
        errors = []
        date_columns = CSV_COLUMNS.get(report_type, {}).get('date', [])
        
        for col in date_columns:
            if col not in df.columns:
                continue
                
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                errors.append(f"Column '{col}' contains invalid date values. Use YYYY-MM-DD format")
                
        return errors

    def _validate_boolean_columns(self, df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate boolean columns have correct values."""
        errors = []
        boolean_columns = CSV_COLUMNS.get(report_type, {}).get('boolean', [])
        valid_values = [True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False']
        
        for col in boolean_columns:
            if col not in df.columns:
                continue
                
            invalid_values = df[~df[col].isin(valid_values)][col].unique()
            if len(invalid_values) > 0:
                errors.append(f"Column '{col}' contains invalid boolean values: {invalid_values}")
                
        return errors

    def validate_file(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate CSV file structure.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        # Check if DataFrame is empty
        if df.empty:
            return False, ERROR_MESSAGES['file_empty']

        # Check required columns
        missing_columns = [col for col in self._required_columns if col not in df.columns]
        if missing_columns:
            return False, ERROR_MESSAGES['missing_columns'].format(', '.join(missing_columns))

        return True, "File structure is valid"

    def validate_store_access(self, store_id: int) -> Tuple[bool, str]:
        """Validate user has access to store.
        
        Args:
            store_id: Store ID to validate access for
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        if not store_id:
            return False, "Store ID is required"

        store = Store.query.filter_by(id=store_id, user_id=self.user_id).first()
        if not store:
            return False, ERROR_MESSAGES['store_not_found']

        return True, "Store access validated"

    @abstractmethod
    def validate_data(self, df: pd.DataFrame) -> Tuple[bool, str]:
        """Validate CSV data content.
        
        Args:
            df: DataFrame to validate
            
        Returns:
            Tuple[bool, str]: (success status, error message)
        """
        pass