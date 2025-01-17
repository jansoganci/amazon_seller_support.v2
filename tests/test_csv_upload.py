import pytest
from flask import url_for
from io import BytesIO
import json

def create_csv_file(content):
    """Test için CSV dosyası oluştur"""
    return BytesIO(content.encode('utf-8'))

def test_upload_without_file(client, auth):
    """Dosya seçilmeden upload testi"""
    auth.login()
    response = client.post('/analytics/upload-csv', data={
        'report_type': 'business_report'
    }, follow_redirects=True)
    assert 'Dosya seçilmedi' in response.get_data(as_text=True)

def test_upload_without_report_type(client, auth):
    """Rapor tipi seçilmeden upload testi"""
    auth.login()
    csv_content = "store_id,date,sku,asin\n1,2024-01-01,SKU1,ASIN1"
    data = {
        'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }
    response = client.post('/analytics/upload-csv', data=data, follow_redirects=True)
    assert 'Lütfen bir rapor tipi seçin' in response.get_data(as_text=True)

def test_upload_invalid_file_type(client, auth):
    """CSV olmayan dosya upload testi"""
    auth.login()
    data = {
        'report_type': 'business_report',
        'file': (BytesIO(b'test content'), 'test.txt')
    }
    response = client.post('/analytics/upload-csv', data=data, follow_redirects=True)
    assert 'Sadece CSV dosyaları yüklenebilir' in response.get_data(as_text=True)

def test_upload_missing_columns(client, auth):
    """Eksik sütunlu CSV upload testi"""
    auth.login()
    csv_content = "store_id,date\n1,2024-01-01"  # Eksik sütunlar
    data = {
        'report_type': 'business_report',
        'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }
    response = client.post('/analytics/upload-csv', data=data, follow_redirects=True)
    assert 'Eksik sütunlar' in response.get_data(as_text=True)

def test_upload_invalid_store_id(client, auth):
    """Geçersiz store ID ile upload testi"""
    auth.login()
    csv_content = "store_id,date,sku,asin,title,sessions,units_ordered,ordered_product_sales,total_order_items,conversion_rate\n999,2024-01-01,SKU1,ASIN1,Test,10,5,100.00,5,0.5"
    data = {
        'report_type': 'business_report',
        'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }
    response = client.post('/analytics/upload-csv', data=data, follow_redirects=True)
    assert 'Store ID 999 bulunamadı' in response.get_data(as_text=True)

def test_flash_message_display(client, auth):
    """Flash mesajlarının görüntülenme testi"""
    auth.login()
    response = client.post('/analytics/upload-csv', data={}, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert 'flash-message-' in html
    assert 'bg-red-50' in html

def test_successful_upload(client, auth):
    """Başarılı CSV upload testi"""
    auth.login()
    csv_content = "store_id,date,sku,asin,title,sessions,units_ordered,ordered_product_sales,total_order_items,conversion_rate\n2,2024-01-01,SKU1,ASIN1,Test,10,5,100.00,5,0.5"
    data = {
        'report_type': 'business_report',
        'file': (BytesIO(csv_content.encode('utf-8')), 'test.csv')
    }
    response = client.post('/analytics/upload-csv', data=data, follow_redirects=True)
    html = response.get_data(as_text=True)
    assert 'CSV dosyası başarıyla yüklendi' in html
    assert 'bg-green-50' in html
