"""Data validation utilities for the Analytics Engine.

This module provides validation functions for various data types and formats
used in the Amazon Seller Support application.
"""

import re
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from decimal import Decimal

class DataValidator:
    """Validates various data types and formats used in the application."""

    # Constants for validation
    ASIN_PATTERN = r'^B[A-Z0-9]{9}$'  # Must start with 'B' followed by 9 alphanumeric characters
    MAX_TITLE_LENGTH = 200
    MIN_UNITS = 0
    MAX_UNITS = 999999
    MIN_PRICE = Decimal('0.01')
    MAX_PRICE = Decimal('999999.99')

    def validate_asin(self, asin: str) -> Tuple[bool, str]:
        """Validate Amazon Standard Identification Number (ASIN).
        
        Args:
            asin: The ASIN to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not asin:
            return False, "ASIN cannot be empty"
        
        if not isinstance(asin, str):
            return False, "ASIN must be a string"
            
        if not re.match(self.ASIN_PATTERN, asin):
            return False, "ASIN must start with 'B' followed by 9 alphanumeric characters"
            
        return True, ""

    def validate_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> Tuple[bool, str]:
        """Validate a date range.
        
        Args:
            start_date: Start date of the range
            end_date: End date of the range
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not start_date or not end_date:
            return False, "Both start_date and end_date are required"
            
        if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
            return False, "Dates must be datetime objects"
            
        if start_date > end_date:
            return False, "Start date cannot be after end date"
            
        if (end_date - start_date).days > 365:
            return False, "Date range cannot exceed 1 year"
            
        return True, ""

    def validate_numeric_value(
        self, 
        value: Any, 
        min_value: float, 
        max_value: float, 
        field_name: str
    ) -> Tuple[bool, str]:
        """Validate a numeric value within a range.
        
        Args:
            value: The value to validate
            min_value: Minimum allowed value
            max_value: Maximum allowed value
            field_name: Name of the field for error messages
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            return False, f"{field_name} cannot be None"
            
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return False, f"{field_name} must be a number"
            
        if num_value < min_value or num_value > max_value:
            return False, f"{field_name} must be between {min_value} and {max_value}"
            
        return True, ""

    def validate_business_report_data(self, data: Dict) -> List[str]:
        """Validate business report data.
        
        Args:
            data: Dictionary containing business report data
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = [
            'asin', 'title', 'units_sold', 'revenue', 
            'returns', 'conversion_rate', 'page_views', 'sessions'
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                
        if not errors:  # Only continue if we have all required fields
            # Validate ASIN
            is_valid, error = self.validate_asin(data['asin'])
            if not is_valid:
                errors.append(error)
                
            # Validate title
            if len(str(data['title'])) > self.MAX_TITLE_LENGTH:
                errors.append(f"Title length cannot exceed {self.MAX_TITLE_LENGTH} characters")
                
            # Validate numeric fields
            numeric_validations = [
                ('units_sold', self.MIN_UNITS, self.MAX_UNITS),
                ('revenue', float(self.MIN_PRICE), float(self.MAX_PRICE)),
                ('returns', 0, data['units_sold'] if 'units_sold' in data else 0),
                ('conversion_rate', 0, 1),
                ('page_views', 0, self.MAX_UNITS),
                ('sessions', 0, self.MAX_UNITS)
            ]
            
            for field, min_val, max_val in numeric_validations:
                is_valid, error = self.validate_numeric_value(
                    data.get(field), min_val, max_val, field
                )
                if not is_valid:
                    errors.append(error)
                    
        return errors

    def validate_inventory_report_data(self, data: Dict) -> List[str]:
        """Validate inventory report data.
        
        Args:
            data: Dictionary containing inventory report data
            
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        # Required fields
        required_fields = [
            'asin', 'title', 'units_available', 
            'units_inbound', 'units_reserved'
        ]
        
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                
        if not errors:  # Only continue if we have all required fields
            # Validate ASIN
            is_valid, error = self.validate_asin(data['asin'])
            if not is_valid:
                errors.append(error)
                
            # Validate title
            if len(str(data['title'])) > self.MAX_TITLE_LENGTH:
                errors.append(f"Title length cannot exceed {self.MAX_TITLE_LENGTH} characters")
                
            # Validate numeric fields
            numeric_validations = [
                ('units_available', self.MIN_UNITS, self.MAX_UNITS),
                ('units_inbound', self.MIN_UNITS, self.MAX_UNITS),
                ('units_reserved', self.MIN_UNITS, self.MAX_UNITS)
            ]
            
            for field, min_val, max_val in numeric_validations:
                is_valid, error = self.validate_numeric_value(
                    data.get(field), min_val, max_val, field
                )
                if not is_valid:
                    errors.append(error)
                    
        return errors
