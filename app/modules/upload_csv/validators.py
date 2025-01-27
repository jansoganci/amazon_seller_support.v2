"""
CSV validation utilities.
"""

from typing import Tuple, List, Dict, Any
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime
import logging
import re
from werkzeug.datastructures import FileStorage

from .constants import CSV_COLUMNS, ERROR_MESSAGES

logger = logging.getLogger(__name__)

class CSVValidator:
    # Constants for validation
    ASIN_PATTERN = r'^B[A-Z0-9]{9}$'
    MAX_TITLE_LENGTH = 200
    MIN_UNITS = 0
    MAX_UNITS = 999999
    MIN_PRICE = Decimal('0.01')
    MAX_PRICE = Decimal('999999.99')

    @staticmethod
    def validate_file_type(file: FileStorage) -> Tuple[bool, str]:
        """Validate that the uploaded file is a CSV."""
        if not file:
            return False, ERROR_MESSAGES['file_required']
        if not file.filename.endswith('.csv'):
            return False, ERROR_MESSAGES['invalid_file_type']
        return True, ""

    @staticmethod
    def validate_required_columns(df: pd.DataFrame, report_type: str) -> Tuple[bool, str]:
        """Validate that all required columns are present."""
        required_columns = CSV_COLUMNS[report_type]['required']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            return False, ERROR_MESSAGES['missing_columns'].format(', '.join(missing_columns))
        return True, ""

    @staticmethod
    def validate_numeric_columns(df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate numeric columns have correct data types."""
        errors = []
        numeric_columns = CSV_COLUMNS[report_type]['numeric']
        
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

    @staticmethod
    def validate_date_columns(df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate date columns have correct format."""
        errors = []
        date_columns = CSV_COLUMNS[report_type]['date']
        
        for col in date_columns:
            if col not in df.columns:
                continue
                
            try:
                df[col] = pd.to_datetime(df[col])
            except ValueError:
                errors.append(
                    f"Column '{col}' contains invalid date values. Use YYYY-MM-DD format"
                )
                
        return errors

    @staticmethod
    def validate_boolean_columns(df: pd.DataFrame, report_type: str) -> List[str]:
        """Validate boolean columns have correct values."""
        errors = []
        if 'boolean' not in CSV_COLUMNS[report_type]:
            return errors
            
        boolean_columns = CSV_COLUMNS[report_type]['boolean']
        valid_values = [True, False, 1, 0, '1', '0', 'true', 'false', 'True', 'False']
        
        for col in boolean_columns:
            if col not in df.columns:
                continue
                
            invalid_values = df[~df[col].isin(valid_values)][col].unique()
            if len(invalid_values) > 0:
                errors.append(
                    f"Column '{col}' contains invalid boolean values: {invalid_values}"
                )
                
        return errors

    def validate_asin(self, asin: str) -> Tuple[bool, str]:
        """Validate Amazon Standard Identification Number (ASIN)."""
        if not asin:
            return False, "ASIN cannot be empty"
        
        if not isinstance(asin, str):
            return False, "ASIN must be a string"
            
        if not re.match(self.ASIN_PATTERN, asin):
            return False, "ASIN must start with 'B' followed by 9 alphanumeric characters"
            
        return True, ""

    def validate_title(self, title: str) -> Tuple[bool, str]:
        """Validate product title."""
        if not title:
            return False, "Title cannot be empty"
            
        if len(str(title)) > self.MAX_TITLE_LENGTH:
            return False, f"Title length cannot exceed {self.MAX_TITLE_LENGTH} characters"
            
        return True, ""

    def validate_numeric_value(self, value: Any, min_value: float, max_value: float, field_name: str) -> Tuple[bool, str]:
        """Validate a numeric value within a range."""
        if value is None:
            return False, f"{field_name} cannot be None"
            
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"
            
        if num_value < min_value or num_value > max_value:
            return False, f"{field_name} must be between {min_value} and {max_value}"
            
        return True, ""

    @staticmethod
    def check_duplicates(df: pd.DataFrame, report_type: str) -> List[Dict[str, Any]]:
        """Check for duplicate entries based on unique constraints."""
        duplicates = []
        
        if report_type == 'business_report':
            dupe_mask = df.duplicated(subset=['store_id', 'date', 'asin'], keep=False)
        elif report_type == 'advertising_report':
            dupe_mask = df.duplicated(
                subset=['store_id', 'date', 'campaign_name', 'ad_group_name'], 
                keep=False
            )
        elif report_type == 'inventory_report':
            dupe_mask = df.duplicated(subset=['store_id', 'date', 'sku'], keep=False)
        elif report_type == 'return_report':
            dupe_mask = df.duplicated(subset=['store_id', 'return_date', 'order_id'], keep=False)
        else:
            return duplicates

        if dupe_mask.any():
            dupes = df[dupe_mask]
            for _, row in dupes.iterrows():
                duplicates.append({
                    'store_id': row['store_id'],
                    'date': row['date'].strftime('%Y-%m-%d') if isinstance(row['date'], datetime) else row['date']
                })
                
        return duplicates

    def validate_csv(self, df: pd.DataFrame, report_type: str) -> Tuple[bool, List[str]]:
        """
        Validate the CSV data for a specific report type.
        Returns (is_valid, error_messages).
        """
        errors = []
        
        # Check required columns
        is_valid, error_msg = self.validate_required_columns(df, report_type)
        if not is_valid:
            errors.append(error_msg)
            return False, errors
            
        # Validate numeric columns
        numeric_errors = self.validate_numeric_columns(df, report_type)
        errors.extend(numeric_errors)
        
        # Validate date columns
        date_errors = self.validate_date_columns(df, report_type)
        errors.extend(date_errors)
        
        # Validate boolean columns
        boolean_errors = self.validate_boolean_columns(df, report_type)
        errors.extend(boolean_errors)
        
        # Additional validations based on report type
        for _, row in df.iterrows():
            if 'asin' in row:
                is_valid, error = self.validate_asin(row['asin'])
                if not is_valid:
                    errors.append(f"Row {_+1}: {error}")
                    
            if 'title' in row:
                is_valid, error = self.validate_title(row['title'])
                if not is_valid:
                    errors.append(f"Row {_+1}: {error}")
                    
            # Numeric validations based on report type
            if report_type == 'business_report':
                numeric_validations = [
                    ('units_ordered', self.MIN_UNITS, self.MAX_UNITS),
                    ('ordered_product_sales', float(self.MIN_PRICE), float(self.MAX_PRICE)),
                    ('sessions', 0, self.MAX_UNITS)
                ]
                
                for field, min_val, max_val in numeric_validations:
                    if field in row:
                        is_valid, error = self.validate_numeric_value(
                            row[field], min_val, max_val, field
                        )
                        if not is_valid:
                            errors.append(f"Row {_+1}: {error}")
        
        # Check for duplicates
        duplicates = self.check_duplicates(df, report_type)
        if duplicates:
            for dupe in duplicates:
                errors.append(
                    ERROR_MESSAGES['duplicate_data'].format(
                        dupe['store_id'], 
                        dupe['date']
                    )
                )
                
        return len(errors) == 0, errors 