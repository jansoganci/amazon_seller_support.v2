"""Test suite for the Data Validator."""

import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from app.utils.data_validator import DataValidator

@pytest.fixture
def validator():
    """Create a DataValidator instance for testing."""
    return DataValidator()

@pytest.fixture
def valid_business_data():
    """Create valid business report data."""
    return {
        'asin': 'B00TEST123',
        'title': 'Test Product',
        'units_sold': 100,
        'revenue': 1000.00,
        'returns': 5,
        'conversion_rate': 0.05,
        'page_views': 2000,
        'sessions': 1500
    }

@pytest.fixture
def valid_inventory_data():
    """Create valid inventory report data."""
    return {
        'asin': 'B00TEST123',
        'title': 'Test Product',
        'units_available': 100,
        'units_inbound': 50,
        'units_reserved': 10
    }

class TestASINValidation:
    """Test cases for ASIN validation."""
    
    def test_valid_asin(self, validator):
        """Test validation of a valid ASIN."""
        is_valid, error = validator.validate_asin('B00TEST123')
        assert is_valid
        assert error == ""

    def test_empty_asin(self, validator):
        """Test validation of an empty ASIN."""
        is_valid, error = validator.validate_asin('')
        assert not is_valid
        assert "empty" in error.lower()

    def test_invalid_asin_format(self, validator):
        """Test validation of invalid ASIN formats."""
        test_cases = [
            'b00test123',  # lowercase
            'B00TEST12',   # too short
            'B00TEST1234', # too long
            'B00TEST12!',  # invalid character
            '1234567890'   # all numbers
        ]
        
        for asin in test_cases:
            is_valid, error = validator.validate_asin(asin)
            assert not is_valid
            assert error

class TestDateRangeValidation:
    """Test cases for date range validation."""
    
    def test_valid_date_range(self, validator):
        """Test validation of a valid date range."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=30)
        
        is_valid, error = validator.validate_date_range(start_date, end_date)
        assert is_valid
        assert error == ""

    def test_invalid_date_order(self, validator):
        """Test validation when end date is before start date."""
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)
        
        is_valid, error = validator.validate_date_range(start_date, end_date)
        assert not is_valid
        assert "after" in error.lower()

    def test_date_range_too_long(self, validator):
        """Test validation of date range exceeding 1 year."""
        start_date = datetime.now()
        end_date = start_date + timedelta(days=366)
        
        is_valid, error = validator.validate_date_range(start_date, end_date)
        assert not is_valid
        assert "1 year" in error.lower()

class TestBusinessReportValidation:
    """Test cases for business report data validation."""
    
    def test_valid_business_data(self, validator, valid_business_data):
        """Test validation of valid business report data."""
        errors = validator.validate_business_report_data(valid_business_data)
        assert not errors

    def test_missing_required_fields(self, validator, valid_business_data):
        """Test validation with missing required fields."""
        for field in valid_business_data.keys():
            invalid_data = valid_business_data.copy()
            del invalid_data[field]
            
            errors = validator.validate_business_report_data(invalid_data)
            assert errors
            assert any(field in error.lower() for error in errors)

    def test_invalid_numeric_values(self, validator, valid_business_data):
        """Test validation with invalid numeric values."""
        test_cases = [
            ('units_sold', -1),
            ('revenue', -100),
            ('returns', -5),
            ('conversion_rate', 1.5),
            ('page_views', -1),
            ('sessions', -1)
        ]
        
        for field, invalid_value in test_cases:
            invalid_data = valid_business_data.copy()
            invalid_data[field] = invalid_value
            
            errors = validator.validate_business_report_data(invalid_data)
            assert errors
            assert any(field in error.lower() for error in errors)

class TestInventoryReportValidation:
    """Test cases for inventory report data validation."""
    
    def test_valid_inventory_data(self, validator, valid_inventory_data):
        """Test validation of valid inventory report data."""
        errors = validator.validate_inventory_report_data(valid_inventory_data)
        assert not errors

    def test_missing_required_fields(self, validator, valid_inventory_data):
        """Test validation with missing required fields."""
        for field in valid_inventory_data.keys():
            invalid_data = valid_inventory_data.copy()
            del invalid_data[field]
            
            errors = validator.validate_inventory_report_data(invalid_data)
            assert errors
            assert any(field in error.lower() for error in errors)

    def test_invalid_numeric_values(self, validator, valid_inventory_data):
        """Test validation with invalid numeric values."""
        test_cases = [
            ('units_available', -1),
            ('units_inbound', -50),
            ('units_reserved', -10)
        ]
        
        for field, invalid_value in test_cases:
            invalid_data = valid_inventory_data.copy()
            invalid_data[field] = invalid_value
            
            errors = validator.validate_inventory_report_data(invalid_data)
            assert errors
            assert any(field in error.lower() for error in errors)

    def test_excessive_values(self, validator, valid_inventory_data):
        """Test validation with excessive numeric values."""
        invalid_data = valid_inventory_data.copy()
        invalid_data['units_available'] = 1000000  # Exceeds MAX_UNITS
        
        errors = validator.validate_inventory_report_data(invalid_data)
        assert errors
        assert any('units_available' in error.lower() for error in errors)
