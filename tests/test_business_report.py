"""Test business report upload functionality."""

import io
import pytest
from datetime import datetime
from decimal import Decimal
from app.modules.business.models import BusinessReport


def test_upload_business_report_success(client, auth_headers):
    """Test successful upload of business report CSV."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024-01-01,B00TEST123,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 200
    assert b'File uploaded successfully' in response.data

    # Verify data was saved
    report = session.query(BusinessReport).first()
    assert report is not None
    assert report.date == datetime(2024, 1, 1).date()
    assert report.asin == 'B00TEST123'
    assert report.title == 'Test Product'
    assert report.category == 'Electronics'
    assert report.subcategory == 'Gadgets'
    assert report.ordered_product_sales == Decimal('100.00')
    assert report.units_ordered == 10
    assert report.total_order_items == 12
    assert report.browser_sessions == 80
    assert report.mobile_app_sessions == 20
    assert report.browser_page_views == 120
    assert report.mobile_app_page_views == 30
    assert report.browser_session_percentage == Decimal('80.00')
    assert report.mobile_app_session_percentage == Decimal('20.00')
    assert report.page_views_per_session == Decimal('1.50')
    assert report.buy_box_percentage == Decimal('95.00')
    assert report.units_ordered_b2b == 2
    assert report.ordered_product_sales_b2b == Decimal('20.00')


def test_upload_business_report_invalid_format(client, auth_headers):
    """Test upload of invalid format business report CSV."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'invalid,csv,format\n1,2,3\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid CSV format' in response.data


def test_upload_business_report_no_authentication(client):
    """Test upload without authentication."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'test'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data')
    assert response.status_code == 401


def test_upload_business_report_duplicate_data(client, auth_headers):
    """Test upload of duplicate business report data."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024-01-01,B00TEST123,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    # First upload
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 200

    # Second upload with same data
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Duplicate data found' in response.data


def test_upload_business_report_invalid_date_format(client, auth_headers):
    """Test upload with invalid date format."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'invalid-date,B00TEST123,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid date format' in response.data


def test_upload_business_report_invalid_numeric_values(client, auth_headers):
    """Test upload with invalid numeric values."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024-01-01,B00TEST123,Test Product,Electronics,Gadgets,invalid,invalid,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid numeric values' in response.data


def test_upload_business_report_missing_required_fields(client, auth_headers):
    """Test upload with missing required fields."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin\n2024-01-01,B00TEST123\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Missing required columns' in response.data


def test_upload_business_report_different_date_formats(client, auth_headers):
    """Test upload with different date formats."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024/01/01,B00TEST123,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'
                           b'01-01-2024,B00TEST456,Test Product 2,Electronics,Gadgets,200.00,20,24,160,40,240,60,80.00,20.00,1.50,95.00,4,40.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid date format' in response.data


def test_upload_business_report_large_file(client, auth_headers):
    """Test upload of large file."""
    # Create a large CSV file (>10MB)
    large_data = b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
    row = b'2024-01-01,B00TEST123,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'
    # Repeat the row many times to create a large file
    large_data += row * 500000

    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(large_data), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 413  # Request Entity Too Large


def test_upload_business_report_invalid_asin_format(client, auth_headers):
    """Test upload with invalid ASIN format."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024-01-01,INVALID,Test Product,Electronics,Gadgets,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid ASIN format' in response.data


def test_upload_business_report_invalid_category(client, auth_headers):
    """Test upload with invalid category."""
    data = {
        'report_type': 'business_report',
        'file': (io.BytesIO(b'date,asin,title,category,subcategory,ordered_product_sales,units_ordered,total_order_items,browser_sessions,mobile_app_sessions,browser_page_views,mobile_app_page_views,browser_session_percentage,mobile_app_session_percentage,page_views_per_session,buy_box_percentage,units_ordered_b2b,ordered_product_sales_b2b\n'
                           b'2024-01-01,B00TEST123,Test Product,InvalidCategory,InvalidSubcategory,100.00,10,12,80,20,120,30,80.00,20.00,1.50,95.00,2,20.00\n'), 'report.csv')
    }
    response = client.post('/business/upload', data=data, content_type='multipart/form-data', headers=auth_headers)
    assert response.status_code == 400
    assert b'Invalid category or subcategory' in response.data 