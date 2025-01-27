"""Test cases for business report CSV processor."""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from decimal import Decimal

from app.modules.business.processors.csv import BusinessCSVProcessor
from app.modules.business.models import BusinessReport
from app.core.csv.exceptions import CSVError
from app.modules.business.constants import ERROR_MESSAGES

@pytest.fixture
def processor(test_user):
    """Create a processor instance with test user."""
    processor = BusinessCSVProcessor()
    processor.user_id = test_user.id
    return processor

def test_processor_initialization(processor):
    """Test processor initialization."""
    assert processor.user_id is not None
    assert processor.db is not None
    assert processor._required_columns is not None

def test_process_data_invalid_columns(processor):
    """Test processing data with invalid columns."""
    df = pd.DataFrame({
        'invalid_column': [1, 2, 3]
    })
    
    success, message, metadata = processor.process_data(df)
    assert not success
    assert message == ERROR_MESSAGES['INVALID_COLUMNS']
    assert metadata == {}

def test_process_data_new_records(processor, test_store, sample_business_df, db_session):
    """Test processing new records."""
    # Set correct store_id
    sample_business_df['store_id'] = test_store.id
    processor.store_id = test_store.id
    
    # Process data
    success, message, metadata = processor.process_data(sample_business_df)
    
    # Verify success
    assert success
    assert "Successfully processed" in message
    assert metadata['processed'] == len(sample_business_df)
    assert metadata['errors'] == 0
    
    # Verify database records
    reports = BusinessReport.query.filter_by(store_id=test_store.id).all()
    assert len(reports) == len(sample_business_df)

def test_process_data_update_existing(processor, test_store, sample_business_df, db_session):
    """Test updating existing records."""
    # Create initial records
    sample_business_df['store_id'] = test_store.id
    processor.store_id = test_store.id
    processor.process_data(sample_business_df)
    
    # Modify some values
    sample_business_df.loc[0, 'ordered_product_sales'] = '200.00'
    sample_business_df.loc[0, 'units_ordered'] = 20
    
    # Process updated data
    success, message, metadata = processor.process_data(sample_business_df)
    
    # Verify success
    assert success
    assert "Successfully processed" in message
    
    # Verify updated records
    report = BusinessReport.query.filter_by(
        store_id=test_store.id,
        asin=sample_business_df.loc[0, 'asin']
    ).first()
    
    assert float(report.ordered_product_sales) == 200.00
    assert report.units_ordered == 20

def test_process_data_invalid_values(processor, test_store, sample_business_df):
    """Test processing data with invalid values."""
    # Set invalid value
    sample_business_df.loc[0, 'ordered_product_sales'] = 'invalid'
    processor.store_id = test_store.id
    
    success, message, metadata = processor.process_data(sample_business_df)
    
    assert not success
    assert metadata['errors'] > 0
    assert len(metadata['error_details']) > 0

def test_process_data_batch_commit(processor, test_store, db_session):
    """Test batch processing with commits."""
    # Create large dataset
    large_df = pd.concat([sample_business_df] * 40)  # 200 rows
    large_df['store_id'] = test_store.id
    processor.store_id = test_store.id
    
    success, message, metadata = processor.process_data(large_df)
    
    assert success
    assert metadata['processed'] == len(large_df)
    assert metadata['errors'] == 0

def test_export_data_no_data(processor, test_store):
    """Test exporting when no data exists."""
    start_date = datetime.now().date()
    end_date = start_date + timedelta(days=7)
    
    success, message, df = processor.export_data(test_store.id, start_date, end_date)
    
    assert not success
    assert message == ERROR_MESSAGES['NO_DATA']
    assert df is None

def test_export_data_with_data(processor, test_store, sample_business_report):
    """Test exporting existing data."""
    start_date = datetime.now().date() - timedelta(days=7)
    end_date = datetime.now().date() + timedelta(days=7)
    
    success, message, df = processor.export_data(test_store.id, start_date, end_date)
    
    assert success
    assert "Successfully exported" in message
    assert isinstance(df, pd.DataFrame)
    assert len(df) > 0
    
    # Verify exported data
    first_row = df.iloc[0]
    assert float(first_row['ordered_product_sales']) == float(sample_business_report.ordered_product_sales)
    assert first_row['asin'] == sample_business_report.asin

def test_export_data_date_filter(processor, test_store, db_session, sample_business_data):
    """Test exporting data with date filtering."""
    # Create reports with different dates
    dates = [
        datetime.now().date() - timedelta(days=i)
        for i in range(5)
    ]
    
    for date in dates:
        report_data = sample_business_data.copy()
        report_data['date'] = date
        report = BusinessReport(**report_data)
        db_session.add(report)
    db_session.commit()
    
    # Export with date range
    start_date = dates[-2]  # Second to last date
    end_date = dates[0]     # Most recent date
    
    success, message, df = processor.export_data(test_store.id, start_date, end_date)
    
    assert success
    assert len(df) == 3  # Should include 3 days of data

@pytest.mark.integration
def test_full_process_flow(processor, test_store, sample_business_df, db_session):
    """Test full process flow: upload, update, and export."""
    # Initial upload
    sample_business_df['store_id'] = test_store.id
    processor.store_id = test_store.id
    
    success, message, metadata = processor.process_data(sample_business_df)
    assert success
    assert metadata['processed'] == len(sample_business_df)
    
    # Update some records
    sample_business_df.loc[0, 'ordered_product_sales'] = '300.00'
    success, message, metadata = processor.process_data(sample_business_df)
    assert success
    
    # Export and verify
    start_date = datetime.now().date() - timedelta(days=7)
    end_date = datetime.now().date() + timedelta(days=7)
    
    success, message, df = processor.export_data(test_store.id, start_date, end_date)
    assert success
    assert len(df) == len(sample_business_df)
    assert float(df.loc[0, 'ordered_product_sales']) == 300.00 