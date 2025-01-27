"""Test cases for business CSV validator."""

import pytest
import pandas as pd
from datetime import datetime

from app.modules.business.validators.csv_validator import BusinessCSVValidator
from app.modules.business.constants import (
    ERROR_MESSAGES,
    REQUIRED_COLUMNS,
    MAX_ASIN_LENGTH,
    MAX_SKU_LENGTH,
    MAX_TITLE_LENGTH,
    DATE_FORMAT
)

@pytest.fixture
def validator():
    """CSV validator fixture."""
    return BusinessCSVValidator()

@pytest.fixture
def valid_data():
    """Valid data fixture."""
    return pd.DataFrame({
        'store_id': [1],
        'date': ['2024-01-01'],
        'sku': ['SKU123'],
        'asin': ['B000001234'],
        'title': ['Test Product'],
        'sessions': [100],
        'units_ordered': [10],
        'ordered_product_sales': [100.00],
        'total_order_items': [15],
        'conversion_rate': [10.50]
    })

def test_validate_dataframe_valid(validator, valid_data):
    """Test validation of valid DataFrame."""
    result = validator.validate_dataframe(valid_data)
    print("Validation errors:", result.errors)  # Debug line
    assert result.is_valid
    assert not result.errors

def test_validate_dataframe_empty(validator):
    """Test validation of empty DataFrame."""
    empty_df = pd.DataFrame()
    result = validator.validate_dataframe(empty_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['EMPTY_FILE'] in result.errors

def test_validate_dataframe_missing_columns(validator):
    """Test validation of DataFrame with missing columns."""
    invalid_df = pd.DataFrame({
        'date': ['2024-01-01'],
        'asin': ['B0000012345']
    })
    result = validator.validate_dataframe(invalid_df)
    assert not result.is_valid
    assert any(ERROR_MESSAGES['MISSING_COLUMNS'].format('') in error for error in result.errors)

def test_validate_dataframe_duplicate_entries(validator):
    """Test validation of DataFrame with duplicate entries."""
    duplicate_df = pd.DataFrame({
        'store_id': [1, 1],
        'date': ['2024-01-01', '2024-01-01'],
        'sku': ['SKU123', 'SKU123'],
        'asin': ['B0000012345', 'B0000012345'],
        'title': ['Test Product', 'Test Product'],
        'sessions': [100, 100],
        'units_ordered': [10, 10],
        'ordered_product_sales': [100.00, 100.00],
        'total_order_items': [15, 15],
        'conversion_rate': [10.50, 10.50]
    })
    result = validator.validate_dataframe(duplicate_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['DUPLICATE_ENTRY'] in result.errors

def test_validate_date_format(validator, valid_data):
    """Test date format validation."""
    invalid_date_df = valid_data.copy()
    invalid_date_df['date'] = ['01/01/2024']
    result = validator.validate_date_format(invalid_date_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['INVALID_DATE_FORMAT'] in result.errors

def test_validate_asin_length(validator, valid_data):
    """Test ASIN length validation."""
    invalid_asin_df = valid_data.copy()
    invalid_asin_df['asin'] = ['B' * (MAX_ASIN_LENGTH + 1)]
    result = validator.validate_asin_length(invalid_asin_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['ASIN_TOO_LONG'] in result.errors

def test_validate_sku_length(validator, valid_data):
    """Test SKU length validation."""
    invalid_sku_df = valid_data.copy()
    invalid_sku_df['sku'] = ['S' * (MAX_SKU_LENGTH + 1)]
    result = validator.validate_sku_length(invalid_sku_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['SKU_TOO_LONG'] in result.errors

def test_validate_title_length(validator, valid_data):
    """Test title length validation."""
    invalid_title_df = valid_data.copy()
    invalid_title_df['title'] = ['A' * (MAX_TITLE_LENGTH + 1)]
    result = validator.validate_title_length(invalid_title_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['TITLE_TOO_LONG'] in result.errors

def test_validate_numeric_fields(validator, valid_data):
    """Test numeric fields validation."""
    invalid_numeric_df = valid_data.copy()
    invalid_numeric_df['ordered_product_sales'] = ['invalid']
    result = validator.validate_numeric_fields(invalid_numeric_df)
    assert not result.is_valid
    assert any(ERROR_MESSAGES['INVALID_NUMERIC'].format('') in error for error in result.errors)

def test_validate_negative_values(validator, valid_data):
    """Test negative values validation."""
    negative_values_df = valid_data.copy()
    negative_values_df['ordered_product_sales'] = [-100.00]
    result = validator.validate_negative_values(negative_values_df)
    assert not result.is_valid
    assert any(ERROR_MESSAGES['NEGATIVE_VALUE'].format('') in error for error in result.errors)

def test_validate_conversion_rate(validator, valid_data):
    """Test conversion rate validation."""
    invalid_rate_df = valid_data.copy()
    invalid_rate_df['conversion_rate'] = [150.00]
    result = validator.validate_conversion_rate(invalid_rate_df)
    assert not result.is_valid
    assert ERROR_MESSAGES['INVALID_CONVERSION_RATE'] in result.errors

def test_validate_data_row(validator, valid_data):
    """Test single data row validation."""
    result = validator.validate_data_row(valid_data.iloc[0])
    print("Row validation errors:", result.errors)  # Debug line
    assert result.is_valid
    assert not result.errors

def test_validate_data_row_invalid(validator):
    """Test invalid data row validation."""
    invalid_data = pd.DataFrame({
        'store_id': [-1],
        'date': ['invalid_date'],
        'sku': ['S' * (MAX_SKU_LENGTH + 1)],
        'asin': ['B' * (MAX_ASIN_LENGTH + 1)],
        'title': ['A' * (MAX_TITLE_LENGTH + 1)],
        'sessions': [-1],
        'units_ordered': [-1],
        'ordered_product_sales': [-100.00],
        'total_order_items': [-1],
        'conversion_rate': [150.00]
    })
    result = validator.validate_data_row(invalid_data.iloc[0])
    assert not result.is_valid
    assert len(result.errors) > 0