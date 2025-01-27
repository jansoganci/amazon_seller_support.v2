"""Test fixtures for CSV upload module."""

import pytest
import pandas as pd
import os
from io import BytesIO
from werkzeug.datastructures import FileStorage

@pytest.fixture
def sample_csv_file():
    """Create a sample CSV file for testing."""
    csv_content = """store_id,date,sku,asin,title,sessions,units_ordered,ordered_product_sales,total_order_items,conversion_rate
1,2025-01-01,SKU001,B000000001,Test Product 1,100,10,500.00,15,0.15
1,2025-01-01,SKU002,B000000002,Test Product 2,200,20,1000.00,25,0.20"""
    
    return FileStorage(
        stream=BytesIO(csv_content.encode()),
        filename="test.csv",
        content_type="text/csv"
    )

@pytest.fixture
def large_csv_file():
    """Create a large CSV file for testing chunked processing."""
    # Create DataFrame with 2500 rows (more than CHUNK_SIZE)
    data = []
    for i in range(2500):
        data.append({
            'store_id': 1,
            'date': '2025-01-01',
            'sku': f'SKU{i:03d}',
            'asin': f'B{i:09d}',
            'title': f'Test Product {i}',
            'sessions': 100 + i,
            'units_ordered': 10 + i,
            'ordered_product_sales': 500.00 + (i * 10),
            'total_order_items': 15 + i,
            'conversion_rate': 0.15 + (i * 0.01)
        })
    
    df = pd.DataFrame(data)
    csv_content = df.to_csv(index=False)
    
    return FileStorage(
        stream=BytesIO(csv_content.encode()),
        filename="large_test.csv",
        content_type="text/csv"
    )

@pytest.fixture
def invalid_csv_file():
    """Create an invalid CSV file for testing error handling."""
    csv_content = """invalid_column,another_invalid
1,2,3
4,5,6"""
    
    return FileStorage(
        stream=BytesIO(csv_content.encode()),
        filename="invalid.csv",
        content_type="text/csv"
    )

@pytest.fixture
def malformed_csv_file():
    """Create a malformed CSV file for testing error handling."""
    csv_content = """store_id,date,sku,asin,title,sessions,units_ordered,ordered_product_sales,total_order_items,conversion_rate
1,invalid_date,SKU001,invalid_asin,Test Product,invalid,invalid,invalid,invalid,invalid"""
    
    return FileStorage(
        stream=BytesIO(csv_content.encode()),
        filename="malformed.csv",
        content_type="text/csv"
    )

@pytest.fixture
def temp_upload_dir(tmpdir):
    """Create a temporary upload directory."""
    upload_dir = tmpdir.mkdir("uploads")
    return str(upload_dir)
