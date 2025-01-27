"""Tests for CSV processors."""

import pytest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
from datetime import datetime
from werkzeug.datastructures import FileStorage

from app.modules.upload_csv.processors.business import BusinessCSVProcessor, BUSINESS_REPORT_COLUMNS
from app.modules.upload_csv.processors.advertising import AdvertisingCSVProcessor, ADVERTISING_REPORT_COLUMNS
from app.modules.upload_csv.processors.inventory import InventoryCSVProcessor
from app.modules.upload_csv.processors.base import BaseCSVProcessor, ProcessingStatus
from app.modules.upload_csv.processors.returns import ReturnCSVProcessor
from app.modules.upload_csv.utils import FileValidationError
from app.modules.upload_csv.validators.advertising import AdvertisingCSVValidator
from app.modules.upload_csv.validators.inventory import InventoryCSVValidator
from app.modules.upload_csv.validators.returns import ReturnCSVValidator
from app import create_app, db
from app.config import TestingConfig

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestingConfig)
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def app_context(app):
    """An application context for the tests."""
    with app.app_context():
        yield

class TestBaseCSVProcessor:
    """Test cases for BaseCSVProcessor."""
    
    def test_initialization(self):
        """Test processor initialization."""
        processor = BusinessCSVProcessor()
        assert processor.report_type == 'business_report'
        assert processor.processing_status is not None
        assert processor.processing_status.status == 'initializing'
    
    def test_process_file_size_validation(self, sample_csv_file):
        """Test file size validation."""
        processor = BusinessCSVProcessor()
        
        # Mock validate_file_size to return error
        with patch('app.modules.upload_csv.processors.validate_file_size', 
                  return_value=(False, "File too large")):
            success, message = processor.process_file(sample_csv_file, user_id=1)
            
            assert not success
            assert "File too large" in message
            assert processor.processing_status.status == 'failed'
            assert len(processor.processing_status.errors) == 1
    
    def test_process_file_type_validation(self, sample_csv_file):
        """Test file type validation."""
        processor = BusinessCSVProcessor()
        
        # Mock validate_file_type to return error
        with patch('app.modules.upload_csv.processors.validate_file_type',
                  return_value=(False, "Invalid file type")):
            success, message = processor.process_file(sample_csv_file, user_id=1)
            
            assert not success
            assert "Invalid file type" in message
            assert processor.processing_status.status == 'failed'
    
    def test_process_file_folder_creation_error(self, sample_csv_file):
        """Test folder creation error handling."""
        processor = BusinessCSVProcessor()
        
        # Mock validate_file_size and type to pass
        with patch('app.modules.upload_csv.processors.validate_file_size',
                  return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.validate_file_type',
                   return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.create_upload_folders',
                   side_effect=FileValidationError("Folder creation failed")):
            
            success, message = processor.process_file(sample_csv_file, user_id=1)
            
            assert not success
            assert "Folder creation failed" in message
            assert processor.processing_status.status == 'failed'
    
    def test_chunked_processing(self, large_csv_file, temp_upload_dir):
        """Test chunked processing of large files."""
        processor = BusinessCSVProcessor()
        
        # Mock all validations to pass
        with patch('app.modules.upload_csv.processors.validate_file_size',
                  return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.validate_file_type',
                   return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.create_upload_folders',
                   return_value=(temp_upload_dir, temp_upload_dir)), \
             patch.object(processor, 'save_data',
                         return_value=(True, "Data saved")):
            
            success, message = processor.process_file(large_csv_file, user_id=1)
            
            assert success
            assert processor.processing_status.status == 'completed'
            assert processor.processing_status.total_rows > 0
            assert processor.processing_status.processed_rows > 0
            assert processor.processing_status.current_chunk > 1
    
    def test_processing_status_tracking(self, sample_csv_file, temp_upload_dir):
        """Test processing status tracking."""
        processor = BusinessCSVProcessor()
        
        # Mock all validations and operations to pass
        with patch('app.modules.upload_csv.processors.validate_file_size',
                  return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.validate_file_type',
                   return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.create_upload_folders',
                   return_value=(temp_upload_dir, temp_upload_dir)), \
             patch.object(processor, 'save_data',
                         return_value=(True, "Data saved")):
            
            processor.process_file(sample_csv_file, user_id=1)
            status = processor.get_processing_status()
            
            assert isinstance(status, dict)
            assert 'total_rows' in status
            assert 'processed_rows' in status
            assert 'progress' in status
            assert 'status' in status
            assert status['status'] == 'completed'
    
    def test_error_handling_during_processing(self, sample_csv_file, temp_upload_dir):
        """Test error handling during file processing."""
        processor = BusinessCSVProcessor()
        
        # Mock validations to pass but processing to fail
        with patch('app.modules.upload_csv.processors.validate_file_size',
                  return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.validate_file_type',
                   return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.create_upload_folders',
                   return_value=(temp_upload_dir, temp_upload_dir)), \
             patch.object(processor, 'save_data',
                         side_effect=Exception("Processing error")):
            
            success, message = processor.process_file(sample_csv_file, user_id=1)
            
            assert not success
            assert "Processing error" in message
            assert processor.processing_status.status == 'failed'
            assert len(processor.processing_status.errors) > 0
    
    def test_cleanup_on_failure(self, sample_csv_file, temp_upload_dir):
        """Test cleanup of temporary files on processing failure."""
        processor = BusinessCSVProcessor()
        
        # Mock validations to pass but processing to fail
        with patch('app.modules.upload_csv.processors.validate_file_size',
                  return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.validate_file_type',
                   return_value=(True, "")), \
             patch('app.modules.upload_csv.processors.create_upload_folders',
                   return_value=(temp_upload_dir, temp_upload_dir)), \
             patch.object(processor, 'save_data',
                         side_effect=Exception("Processing error")), \
             patch('app.modules.upload_csv.processors.cleanup_temp_files') as mock_cleanup:
            
            processor.process_file(sample_csv_file, user_id=1)
            
            # Verify cleanup was called
            assert mock_cleanup.called

class TestBusinessCSVProcessor:
    """Test cases for BusinessCSVProcessor."""
    
    @pytest.fixture
    def valid_business_data(self):
        """Valid business report data fixture."""
        return pd.DataFrame({
            'store_id': [1, 2],
            'date': ['2025-01-01', '2025-01-02'],
            'order_id': [12345678901234567890, 12345678901234567891],
            'sku': ['ABC123', 'ABC124'],
            'asin': ['B0123456789', 'B0123456790'],
            'title': ['Test Ürün 1', 'Test Ürün 2'],
            'quantity': [1, 2],
            'price': [99.99, 199.99],
            'revenue': [99.99, 399.98]
        })
    
    @pytest.fixture
    def invalid_business_data(self):
        """Invalid business report data fixture."""
        return pd.DataFrame({
            'store_id': ['invalid', 2],  # Invalid store_id
            'date': ['2025-13-01', '2025-01-02'],  # Invalid date
            'order_id': ['123-4567890-1234567', '123-4567890-1234568'],
            'sku': ['ABC123', 'ABC124'],
            'asin': ['B0123456789', 'B0123456790'],
            'title': ['Test Ürün 1', 'Test Ürün 2'],
            'quantity': ['invalid', 2],  # Invalid quantity
            'price': [-99.99, 199.99],  # Invalid price
            'revenue': ['invalid', 399.98]  # Invalid revenue
        })
    
    def test_initialization(self):
        """Test BusinessCSVProcessor initialization."""
        processor = BusinessCSVProcessor()
        assert processor.report_type == 'business_report'
        assert processor.validator is not None
    
    def test_validate_data_success(self, valid_business_data):
        """Test validation with valid data."""
        processor = BusinessCSVProcessor()
        success, errors = processor.validate_data(valid_business_data)
        assert success
        assert len(errors) == 0
    
    def test_validate_data_missing_columns(self):
        """Test validation with missing columns."""
        processor = BusinessCSVProcessor()
        invalid_df = pd.DataFrame({
            'store_id': [1],
            'date': ['2025-01-01']  # Missing required columns
        })
        success, errors = processor.validate_data(invalid_df)
        assert not success
        assert any("Missing required columns" in error for error in errors)
    
    def test_validate_data_invalid_types(self, invalid_business_data):
        """Test validation with invalid data types."""
        processor = BusinessCSVProcessor()
        success, errors = processor.validate_data(invalid_business_data)
        assert not success
        assert len(errors) > 0
        # Check specific error messages
        error_messages = "\n".join(errors)
        assert "Invalid value for Store ID" in error_messages  # Invalid store_id
        assert "Invalid date format (YYYY-MM-DD)" in error_messages  # Invalid date
        assert "Invalid value for Order ID" in error_messages  # Invalid order_id
        assert "Invalid value for Quantity" in error_messages  # Invalid quantity
        assert "Invalid value for Price" in error_messages  # Invalid price
        assert "Invalid value for Revenue" in error_messages  # Invalid revenue
    
    def test_validate_data_future_date(self):
        """Test validation with future dates."""
        processor = BusinessCSVProcessor()
        future_data = pd.DataFrame({
            'store_id': [1],
            'date': [(datetime.now().date() + pd.Timedelta(days=1)).strftime('%Y-%m-%d')],
            'order_id': [12345678901234567890],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'title': ['Test Ürün'],
            'quantity': [1],
            'price': [99.99],
            'revenue': [99.99]
        })
        success, errors = processor.validate_data(future_data)
        assert not success
        assert any("Future dates are not allowed" in error for error in errors)
    
    def test_save_data_success(self, app_context, valid_business_data):
        """Test successful data saving."""
        processor = BusinessCSVProcessor()
        with patch('app.modules.upload_csv.processors.business.db.session.add'), \
             patch('app.modules.upload_csv.processors.business.db.session.commit'):
            success, message = processor.save_data(valid_business_data, user_id=1)
            assert success
            assert "Processed" in message
    
    def test_save_data_db_error(self, app_context, valid_business_data):
        """Test database error handling during save."""
        processor = BusinessCSVProcessor()
        with patch('app.modules.upload_csv.processors.business.db.session.add'), \
             patch('app.modules.upload_csv.processors.business.db.session.commit',
                   side_effect=Exception("Database error")):
            success, message = processor.save_data(valid_business_data, user_id=1)
            assert not success
            assert "Error saving data" in message
    
    def test_get_template(self):
        """Test template retrieval."""
        processor = BusinessCSVProcessor()
        template = processor.get_template()
        assert template['name'] == 'Business Report'
        assert template['columns'] == BUSINESS_REPORT_COLUMNS
        assert 'sample_row' in template
        # Verify all required columns are in sample row
        for column in BUSINESS_REPORT_COLUMNS.keys():
            assert column in template['sample_row']

class TestAdvertisingCSVProcessor:
    """Tests for AdvertisingCSVProcessor."""

    @pytest.fixture
    def valid_advertising_data(self):
        """Valid advertising data for testing."""
        return pd.DataFrame({
            'store_id': [1],
            'date': ['2025-01-01'],
            'campaign_name': ['Test Campaign'],
            'ad_group_name': ['Test Ad Group'],
            'targeting_type': ['AUTO'],
            'match_type': ['BROAD'],
            'search_term': ['test product'],
            'impressions': [1000],
            'clicks': [100],
            'ctr': [10.0],
            'cpc': [0.50],
            'spend': [50.00],
            'total_sales': [200.00],
            'acos': [25.0],
            'total_orders': [10],
            'total_units': [15],
            'conversion_rate': [0.10]
        })

    @pytest.fixture
    def invalid_advertising_data(self):
        """Invalid advertising data for testing."""
        return pd.DataFrame({
            'store_id': ['invalid'],  # Should be int
            'date': ['2025-13-01'],  # Invalid date
            'campaign_name': ['Test Campaign'],
            'ad_group_name': ['Test Ad Group'],
            'targeting_type': ['AUTO'],
            'match_type': ['BROAD'],
            'search_term': ['test product'],
            'impressions': [100],
            'clicks': [1000],  # More clicks than impressions
            'ctr': [150.0],  # CTR > 100%
            'cpc': [0.50],
            'spend': [50.00],
            'total_sales': [200.00],
            'acos': [-25.0],  # Negative ACoS
            'total_orders': [15],
            'total_units': [10],  # Less units than orders
            'conversion_rate': [1.5]  # Conversion rate > 1
        })

    def test_initialization(self):
        """Test processor initialization."""
        processor = AdvertisingCSVProcessor()
        assert processor.report_type == 'advertising_report'
        assert isinstance(processor.validator, AdvertisingCSVValidator)

    def test_validate_data_success(self, valid_advertising_data):
        """Test validation with valid data."""
        processor = AdvertisingCSVProcessor()
        success, errors = processor.validate_data(valid_advertising_data)
        assert success
        assert len(errors) == 0

    def test_validate_data_missing_columns(self):
        """Test validation with missing columns."""
        processor = AdvertisingCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'date': ['2025-01-01']
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert len(errors) > 0
        error_messages = "\n".join(errors)
        assert "Columns must be in the specified order" in error_messages

    def test_validate_data_invalid_types(self, invalid_advertising_data):
        """Test validation with invalid data types."""
        processor = AdvertisingCSVProcessor()
        success, errors = processor.validate_data(invalid_advertising_data)
        assert not success
        assert len(errors) > 0
        error_messages = "\n".join(errors)
        assert "Invalid value for Store ID" in error_messages
        assert "Invalid date format (YYYY-MM-DD)" in error_messages
        assert "CTR must be between 0 and 100" in error_messages
        assert "ACoS cannot be negative" in error_messages
        assert "Clicks cannot be more than impressions" in error_messages
        assert "Total units cannot be less than total orders" in error_messages
        assert "Conversion rate must be between 0 and 1" in error_messages

    def test_validate_data_future_date(self):
        """Test validation with future dates."""
        processor = AdvertisingCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'date': ['2026-01-01'],  # Future date
            'campaign_name': ['Test Campaign'],
            'ad_group_name': ['Test Ad Group'],
            'targeting_type': ['AUTO'],
            'match_type': ['BROAD'],
            'search_term': ['test product'],
            'impressions': [1000],
            'clicks': [100],
            'ctr': [10.0],
            'cpc': [0.50],
            'spend': [50.00],
            'total_sales': [200.00],
            'acos': [25.0],
            'total_orders': [10],
            'total_units': [15],
            'conversion_rate': [0.10]
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert "Future dates are not allowed" in errors

    def test_save_data_success(self, valid_advertising_data, app_context):
        """Test successful data save."""
        processor = AdvertisingCSVProcessor()
        success, message = processor.save_data(valid_advertising_data, user_id=1)
        assert success
        assert "Processed" in message
        assert "new records" in message

    def test_save_data_db_error(self, valid_advertising_data, app_context):
        """Test database error handling during save."""
        processor = AdvertisingCSVProcessor()
        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            success, message = processor.save_data(valid_advertising_data, user_id=1)
            assert not success
            assert "Error saving data" in message

    def test_get_template(self):
        """Test template retrieval."""
        processor = AdvertisingCSVProcessor()
        template = processor.get_template()
        assert template['name'] == 'Advertising Report'
        assert 'columns' in template
        assert 'sample_row' in template
        assert len(template['columns']) == len(template['sample_row'])

class TestInventoryCSVProcessor:
    """Tests for InventoryCSVProcessor."""

    @pytest.fixture
    def valid_inventory_data(self):
        """Valid inventory data for testing."""
        return pd.DataFrame({
            'store_id': [1],
            'date': ['2025-01-01'],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'product_name': ['Test Ürün'],
            'condition': ['New'],
            'price': [99.99],
            'mfn_listing_exists': [True],
            'mfn_fulfillable_quantity': [10],
            'afn_listing_exists': [True],
            'afn_warehouse_quantity': [50],
            'afn_fulfillable_quantity': [45],
            'afn_unsellable_quantity': [2],
            'afn_reserved_quantity': [3],
            'afn_total_quantity': [100],
            'per_unit_volume': [1.5]
        })

    @pytest.fixture
    def invalid_inventory_data(self):
        """Invalid inventory data for testing."""
        return pd.DataFrame({
            'store_id': ['invalid'],  # Should be int
            'date': ['2025-13-01'],  # Invalid date
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'product_name': ['Test Ürün'],
            'condition': ['New'],
            'price': [-99.99],  # Negative price
            'mfn_listing_exists': ['invalid'],  # Should be bool
            'mfn_fulfillable_quantity': [10],
            'afn_listing_exists': [True],
            'afn_warehouse_quantity': [-50],  # Negative quantity
            'afn_fulfillable_quantity': [45],
            'afn_unsellable_quantity': [2],
            'afn_reserved_quantity': [3],
            'afn_total_quantity': [0],  # Incorrect total
            'per_unit_volume': [0]  # Should be > 0
        })

    def test_initialization(self):
        """Test processor initialization."""
        processor = InventoryCSVProcessor()
        assert processor.report_type == 'inventory_report'
        assert isinstance(processor.validator, InventoryCSVValidator)

    def test_validate_data_success(self, valid_inventory_data):
        """Test validation with valid data."""
        processor = InventoryCSVProcessor()
        success, errors = processor.validate_data(valid_inventory_data)
        assert success
        assert len(errors) == 0

    def test_validate_data_missing_columns(self):
        """Test validation with missing columns."""
        processor = InventoryCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'date': ['2025-01-01']
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert len(errors) > 0
        error_messages = "\n".join(errors)
        assert "Columns must be in the specified order" in error_messages

    def test_validate_data_invalid_types(self, invalid_inventory_data):
        """Test validation with invalid data types."""
        processor = InventoryCSVProcessor()
        success, errors = processor.validate_data(invalid_inventory_data)
        assert not success
        assert len(errors) > 0
        error_messages = "\n".join(errors)
        assert "Invalid value for Store ID" in error_messages
        assert "Invalid date format (YYYY-MM-DD)" in error_messages

    def test_validate_data_future_date(self):
        """Test validation with future dates."""
        processor = InventoryCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'date': ['2026-01-01'],  # Future date
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'product_name': ['Test Ürün'],
            'condition': ['New'],
            'price': [99.99],
            'mfn_listing_exists': [True],
            'mfn_fulfillable_quantity': [10],
            'afn_listing_exists': [True],
            'afn_warehouse_quantity': [50],
            'afn_fulfillable_quantity': [45],
            'afn_unsellable_quantity': [2],
            'afn_reserved_quantity': [3],
            'afn_total_quantity': [100],
            'per_unit_volume': [1.5]
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert "Future dates are not allowed" in errors

    def test_save_data_success(self, valid_inventory_data, app_context):
        """Test successful data save."""
        processor = InventoryCSVProcessor()
        success, message = processor.save_data(valid_inventory_data, user_id=1)
        assert success
        assert "Processed" in message
        assert "new records" in message

    def test_save_data_db_error(self, valid_inventory_data, app_context):
        """Test database error handling during save."""
        processor = InventoryCSVProcessor()
        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            success, message = processor.save_data(valid_inventory_data, user_id=1)
            assert not success
            assert "Error saving data" in message

    def test_get_template(self):
        """Test template retrieval."""
        processor = InventoryCSVProcessor()
        template = processor.get_template()
        assert template['name'] == 'Inventory Report'
        assert 'columns' in template
        assert 'sample_row' in template
        assert len(template['columns']) == len(template['sample_row'])

class TestReturnCSVProcessor:
    """Tests for ReturnCSVProcessor."""

    @pytest.fixture
    def valid_return_data(self):
        """Valid return data for testing."""
        return pd.DataFrame({
            'store_id': [1],
            'return_date': ['2025-01-01'],
            'order_id': ['123-4567890-1234567'],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'title': ['Test Ürün'],
            'quantity': [1],
            'return_reason': ['Damaged Product'],
            'status': ['Completed'],
            'refund_amount': [99.99],
            'return_center': ['FBA'],
            'return_carrier': ['Amazon Logistics'],
            'tracking_number': ['TBA123456789']
        })

    @pytest.fixture
    def invalid_return_data(self):
        """Invalid return data for testing."""
        return pd.DataFrame({
            'store_id': ['invalid'],
            'return_date': ['2025-13-01'],
            'order_id': ['123-4567890-1234567'],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'title': ['Test Ürün'],
            'quantity': [0],
            'return_reason': ['Damaged Product'],
            'status': ['Invalid'],
            'refund_amount': [-10.0],
            'return_center': ['Invalid'],
            'return_carrier': ['Invalid'],
            'tracking_number': ['Invalid']
        })

    def test_initialization(self):
        """Test processor initialization."""
        processor = ReturnCSVProcessor()
        assert processor.report_type == 'return_report'
        assert isinstance(processor.validator, ReturnCSVValidator)

    def test_validate_data_success(self, valid_return_data):
        """Test validation with valid data."""
        processor = ReturnCSVProcessor()
        success, errors = processor.validate_data(valid_return_data)
        assert success
        assert len(errors) == 0

    def test_validate_data_missing_columns(self):
        """Test validation with missing columns."""
        processor = ReturnCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'return_date': ['2025-01-01']
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert len(errors) > 0
        error_messages = "\n".join(errors)
        assert "Columns must be in the specified order" in error_messages

    def test_validate_data_invalid_types(self):
        """Test validation with invalid data types."""
        processor = ReturnCSVProcessor()
        df = pd.DataFrame({
            'store_id': ['invalid'],
            'return_date': ['2025-13-01'],
            'order_id': [123],
            'sku': [None],
            'asin': [None],
            'title': [None],
            'quantity': [0],
            'return_reason': [None],
            'status': ['Invalid'],
            'refund_amount': [-10.0],
            'return_center': ['Invalid'],
            'return_carrier': ['Invalid'],
            'tracking_number': ['Invalid']
        })
        success, errors = processor.validate_data(df)
        assert not success
        error_messages = "\n".join(errors)
        assert "Invalid value for Store ID" in error_messages
        assert "time data" in error_messages and "doesn't match format" in error_messages
        assert "Error during date comparison" in error_messages
        assert "Quantity must be greater than 0" in error_messages
        assert "Refund amount cannot be negative" in error_messages
        assert "Invalid status" in error_messages

    def test_validate_data_invalid_values(self):
        """Test validation with invalid values."""
        processor = ReturnCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'return_date': ['2025-01-01'],
            'order_id': ['123-4567890-1234567'],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'title': ['Test Product'],
            'quantity': [0],  # Invalid: should be > 0
            'return_reason': ['Damaged Product'],
            'status': ['Invalid'],  # Invalid status
            'refund_amount': [-10.0],  # Invalid: negative amount
            'return_center': ['Invalid Center'],  # Invalid: should be in VALID_RETURN_CENTERS
            'return_carrier': ['Invalid Carrier'],  # Invalid: should be in VALID_RETURN_CARRIERS
            'tracking_number': ['INVALID123']  # Invalid: should start with valid prefix
        })
        success, errors = processor.validate_data(df)
        assert not success
        error_messages = "\n".join(errors)
        assert "Quantity must be greater than 0" in error_messages
        assert "Refund amount cannot be negative" in error_messages
        assert "Invalid status. Valid values:" in error_messages
        assert "Invalid return center" in error_messages
        assert "Invalid return carrier" in error_messages
        assert "Invalid tracking number" in error_messages

    def test_validate_data_future_date(self):
        """Test validation with future dates."""
        processor = ReturnCSVProcessor()
        df = pd.DataFrame({
            'store_id': [1],
            'return_date': ['2026-01-01'],  # Future date
            'order_id': ['123-4567890-1234567'],
            'sku': ['ABC123'],
            'asin': ['B0123456789'],
            'title': ['Test Ürün'],
            'quantity': [1],
            'return_reason': ['Damaged Product'],
            'status': ['Completed'],
            'refund_amount': [99.99],
            'return_center': ['ABC Returns Center'],
            'return_carrier': ['XYZ Shipping'],
            'tracking_number': ['TR123456789']
        })
        success, errors = processor.validate_data(df)
        assert not success
        assert "Future dates are not allowed" in errors

    def test_save_data_success(self, valid_return_data, app_context):
        """Test successful data save."""
        processor = ReturnCSVProcessor()
        success, message = processor.save_data(valid_return_data, user_id=1)
        assert success
        assert "Processed" in message
        assert "new records" in message

    def test_save_data_db_error(self, valid_return_data, app_context):
        """Test database error handling during save."""
        processor = ReturnCSVProcessor()
        with patch('app.db.session.commit') as mock_commit:
            mock_commit.side_effect = Exception("Database error")
            success, message = processor.save_data(valid_return_data, user_id=1)
            assert not success
            assert "Error saving data" in message

    def test_get_template(self):
        """Test template retrieval."""
        processor = ReturnCSVProcessor()
        template = processor.get_template()
        assert template['name'] == 'Return Report'
        assert 'columns' in template
        assert 'sample_row' in template
        assert len(template['columns']) == len(template['sample_row'])
