"""Business CSV validator module."""

from typing import Dict, Any, List
import pandas as pd
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.modules.business.constants import (
    ERROR_MESSAGES,
    REQUIRED_COLUMNS,
    MAX_ASIN_LENGTH,
    MAX_SKU_LENGTH,
    MAX_TITLE_LENGTH,
    DATE_FORMAT
)

class ValidationResult:
    """Validation result class."""
    
    def __init__(self, is_valid: bool = True, errors: List[str] = None):
        """Initialize validation result."""
        self.is_valid = is_valid
        self.errors = errors or []

class BusinessCSVValidator:
    """Business CSV validator class."""
    
    def validate_dataframe(self, df: pd.DataFrame) -> ValidationResult:
        """Validate entire DataFrame."""
        result = ValidationResult()
        
        # Check for empty DataFrame
        if df.empty:
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['EMPTY_FILE'])
            return result
        
        # Check for required columns
        missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
        if missing_columns:
            result.is_valid = False
            result.errors.append(
                ERROR_MESSAGES['MISSING_COLUMNS'].format(
                    ', '.join(missing_columns)
                )
            )
            return result
        
        # Check for duplicate entries
        duplicates = df[['date', 'asin']].duplicated()
        if duplicates.any():
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['DUPLICATE_ENTRY'])
            return result
        
        # Validate each row
        for index, row in df.iterrows():
            row_result = self.validate_data_row(row)
            if not row_result.is_valid:
                result.is_valid = False
                result.errors.extend(row_result.errors)
                return result
        
        return result
    
    def validate_data_row(self, row: pd.Series) -> ValidationResult:
        """Validate a single data row."""
        result = ValidationResult()
        df = pd.DataFrame([row])
        
        # Required fields validation
        fields_result = self.validate_required_fields(df)
        if not fields_result.is_valid:
            result.is_valid = False
            result.errors.extend(fields_result.errors)
            return result
        
        # Date format validation
        date_result = self.validate_date_format(df)
        if not date_result.is_valid:
            result.is_valid = False
            result.errors.extend(date_result.errors)
            return result
        
        # Length validations
        length_validations = [
            self.validate_sku_length,
            self.validate_asin_length,
            self.validate_title_length
        ]
        
        for validation in length_validations:
            length_result = validation(df)
            if not length_result.is_valid:
                result.is_valid = False
                result.errors.extend(length_result.errors)
                return result
        
        # Numeric validations
        numeric_result = self.validate_numeric_fields(df)
        if not numeric_result.is_valid:
            result.is_valid = False
            result.errors.extend(numeric_result.errors)
            return result
        
        # Negative values validation
        negative_result = self.validate_negative_values(df)
        if not negative_result.is_valid:
            result.is_valid = False
            result.errors.extend(negative_result.errors)
            return result
        
        # Conversion rate validation
        conversion_result = self.validate_conversion_rate(df)
        if not conversion_result.is_valid:
            result.is_valid = False
            result.errors.extend(conversion_result.errors)
            return result
        
        return result
    
    def validate_required_fields(self, df: pd.DataFrame) -> ValidationResult:
        """Validate required fields are present and not null."""
        result = ValidationResult()
        
        for column in REQUIRED_COLUMNS:
            if column not in df.columns or df[column].isnull().any():
                result.is_valid = False
                result.errors.append(
                    ERROR_MESSAGES['MISSING_REQUIRED_FIELD'].format(column)
                )
        
        return result
    
    def validate_date_format(self, df: pd.DataFrame) -> ValidationResult:
        """Validate date format."""
        result = ValidationResult()
        
        try:
            for date_str in df['date']:
                try:
                    datetime.strptime(date_str, DATE_FORMAT)
                except ValueError:
                    result.is_valid = False
                    result.errors.append(ERROR_MESSAGES['INVALID_DATE_FORMAT'])
                    return result
        except (ValueError, TypeError):
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['INVALID_DATE_FORMAT'])
            return result
        
        return result
    
    def validate_sku_length(self, df: pd.DataFrame) -> ValidationResult:
        """Validate SKU length."""
        result = ValidationResult()
        
        if (df['sku'].str.len() > MAX_SKU_LENGTH).any():
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['SKU_TOO_LONG'])
        
        return result
    
    def validate_asin_length(self, df: pd.DataFrame) -> ValidationResult:
        """Validate ASIN length."""
        result = ValidationResult()
        
        if (df['asin'].str.len() > MAX_ASIN_LENGTH).any():
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['ASIN_TOO_LONG'])
        
        return result
    
    def validate_title_length(self, df: pd.DataFrame) -> ValidationResult:
        """Validate title length."""
        result = ValidationResult()
        
        if (df['title'].str.len() > MAX_TITLE_LENGTH).any():
            result.is_valid = False
            result.errors.append(ERROR_MESSAGES['TITLE_TOO_LONG'])
        
        return result
    
    def validate_numeric_fields(self, df: pd.DataFrame) -> ValidationResult:
        """Validate numeric fields."""
        result = ValidationResult()
        integer_fields = [
            'store_id',
            'sessions',
            'units_ordered',
            'total_order_items'
        ]
        decimal_fields = [
            'ordered_product_sales',
            'conversion_rate'
        ]
        
        # Validate integer fields
        for field in integer_fields:
            try:
                pd.to_numeric(df[field], downcast='integer')
            except (ValueError, TypeError):
                result.is_valid = False
                result.errors.append(
                    ERROR_MESSAGES['INVALID_NUMERIC'].format(field)
                )
        
        # Validate decimal fields
        for field in decimal_fields:
            try:
                pd.to_numeric(df[field], downcast='float')
            except (ValueError, TypeError):
                result.is_valid = False
                result.errors.append(
                    ERROR_MESSAGES['INVALID_NUMERIC'].format(field)
                )
        
        return result
    
    def validate_negative_values(self, df: pd.DataFrame) -> ValidationResult:
        """Validate no negative values in numeric fields."""
        result = ValidationResult()
        numeric_fields = [
            'sessions',
            'units_ordered',
            'ordered_product_sales',
            'total_order_items'
        ]
        
        for field in numeric_fields:
            if (pd.to_numeric(df[field]) < 0).any():
                result.is_valid = False
                result.errors.append(
                    ERROR_MESSAGES['NEGATIVE_VALUE'].format(field)
                )
        
        return result
    
    def validate_conversion_rate(self, df: pd.DataFrame) -> ValidationResult:
        """Validate conversion rate is between 0 and 100."""
        result = ValidationResult()
        
        try:
            conversion_rate = pd.to_numeric(df['conversion_rate'])
            if ((conversion_rate < 0) | (conversion_rate > 100)).any():
                result.is_valid = False
                result.errors.append(ERROR_MESSAGES['INVALID_CONVERSION_RATE'])
        except (ValueError, TypeError):
            result.is_valid = False
            result.errors.append(
                ERROR_MESSAGES['INVALID_NUMERIC'].format('conversion_rate')
            )
        
        return result
