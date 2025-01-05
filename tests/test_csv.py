import pytest
from io import StringIO
import pandas as pd
from app.services.csv_validator import CSVValidator
from app.models.store import Store
from app.models.reports import BusinessReport, AdvertisingReport, ReturnReport, InventoryReport

def create_test_csv(data, report_type):
    """Test için CSV dosyası oluştur"""
    df = pd.DataFrame(data)
    csv_buffer = StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_buffer.seek(0)
    return csv_buffer

def test_validate_business_report(client):
    """Business report validasyonunu test et"""
    # Test verisi
    data = {
        'store_id': [1],
        'asin': ['B00TEST123'],
        'title': ['Test Product'],
        'units_sold': [10],
        'revenue': [199.90],
        'returns': [2],
        'conversion_rate': [0.15],
        'page_views': [100],
        'sessions': [50]
    }
    
    csv_file = create_test_csv(data, 'business_report')
    
    # Validasyon testi
    is_valid, error_message, metadata = CSVValidator.validate_csv(csv_file, 'business_report')
    assert is_valid == True, f"Validation failed: {error_message}"
    assert 'transformed_data' in metadata
    assert len(metadata['transformed_data']) == 1

def test_validate_advertising_report(client):
    """Advertising report validasyonunu test et"""
    data = {
        'store_id': [1],
        'store_name': ['Test Store'],
        'campaign_name': ['Test Campaign'],
        'impressions': [1000],
        'clicks': [100],
        'cost': [50.00],
        'sales': [200.00],
        'acos': [0.25],
        'roi': [4.00]
    }
    
    csv_file = create_test_csv(data, 'advertising_report')
    
    is_valid, error_message, metadata = CSVValidator.validate_csv(csv_file, 'advertising_report')
    assert is_valid == True, f"Validation failed: {error_message}"
    assert 'transformed_data' in metadata
    assert len(metadata['transformed_data']) == 1

def test_validate_return_report(client):
    """Return report validasyonunu test et"""
    data = {
        'store_id': [1],
        'store_name': ['Test Store'],
        'asin': ['B00TEST123'],
        'title': ['Test Product'],
        'return_reason': ['Size Issue'],
        'return_count': [5],
        'total_units_sold': [100],
        'return_rate': [0.05],
        'customer_feedback': ['Too small']
    }
    
    csv_file = create_test_csv(data, 'return_report')
    
    is_valid, error_message, metadata = CSVValidator.validate_csv(csv_file, 'return_report')
    assert is_valid == True, f"Validation failed: {error_message}"
    assert 'transformed_data' in metadata
    assert len(metadata['transformed_data']) == 1

def test_validate_inventory_report(client):
    """Inventory report validasyonunu test et"""
    data = {
        'store_id': [1],
        'store_name': ['Test Store'],
        'asin': ['B00TEST123'],
        'title': ['Test Product'],
        'units_available': [50],
        'units_inbound': [20],
        'units_reserved': [5],
        'units_total': [75],
        'reorder_required': ['true']
    }
    
    csv_file = create_test_csv(data, 'inventory_report')
    
    is_valid, error_message, metadata = CSVValidator.validate_csv(csv_file, 'inventory_report')
    assert is_valid == True, f"Validation failed: {error_message}"
    assert 'transformed_data' in metadata
    assert len(metadata['transformed_data']) == 1

def test_invalid_numeric_values(client):
    """Geçersiz sayısal değerleri test et"""
    data = {
        'store_id': [1],
        'asin': ['B00TEST123'],
        'title': ['Test Product'],
        'units_sold': ['invalid'],  # Geçersiz sayısal değer
        'revenue': [199.90],
        'returns': [2],
        'conversion_rate': [0.15],
        'page_views': [100],
        'sessions': [50]
    }
    
    csv_file = create_test_csv(data, 'business_report')
    
    is_valid, error_message, metadata = CSVValidator.validate_csv(csv_file, 'business_report')
    assert is_valid == False, "Should fail with invalid numeric value"

def test_duplicate_upload(client):
    """Duplike yüklemeyi test et"""
    # İlk yükleme
    data = {
        'store_id': [1],
        'asin': ['B00TEST123'],
        'title': ['Test Product'],
        'units_sold': [10],
        'revenue': [199.90],
        'returns': [2],
        'conversion_rate': [0.15],
        'page_views': [100],
        'sessions': [50],
        'created_at': ['2025-01-05']  # Tarih eklendi
    }
    
    # İlk yükleme
    csv_file = create_test_csv(data, 'business_report')
    is_valid, _, metadata = CSVValidator.validate_csv(csv_file, 'business_report')
    assert is_valid == True
    
    # İlk veriyi kaydet
    from app.routes.csv import save_report_data
    success, error = save_report_data(metadata['transformed_data'], 'business_report')
    assert success == True, f"İlk kayıt başarısız: {error}"
    
    # Aynı veriyi tekrar yükle
    csv_file = create_test_csv(data, 'business_report')
    is_valid, _, metadata = CSVValidator.validate_csv(csv_file, 'business_report')
    assert is_valid == True  # Validasyon başarılı olmalı
    
    # İkinci kayıt denemesi başarısız olmalı
    success, error = save_report_data(metadata['transformed_data'], 'business_report')
    assert success == False, "Should fail on duplicate upload"
    assert "rapor zaten yüklenmiş" in error
