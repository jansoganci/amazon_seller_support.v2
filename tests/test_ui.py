import pytest
from flask import url_for
from io import BytesIO

def test_homepage_redirect(client, auth):
    """Test ana sayfaya yönlendirmenin doğru çalıştığını kontrol et"""
    # Giriş yapmamış kullanıcı ana sayfada kalmalı
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    
    # Giriş yapmış kullanıcı dashboard'a yönlendirilmeli
    auth.login()
    response = client.get('/', follow_redirects=True)
    assert b'Dashboard' in response.data

def test_upload_progress(client, auth):
    """Test upload progress bar'ın çalıştığını kontrol et"""
    auth.login()
    response = client.get('/csv/upload', follow_redirects=True)
    assert response.status_code == 200
    assert b'progress-container' in response.data

def test_upload_success_message(client, auth):
    """Test upload başarı mesajının gösterildiğini kontrol et"""
    auth.login()
    response = client.get('/csv/upload', follow_redirects=True)
    assert response.status_code == 200
    
    data = {
        'file': (BytesIO(b'store_id,store_name,store_region\n1,Test Store,US'), 'test.csv'),
        'report_type': 'store'
    }
    response = client.post('/csv/upload',
                         data=data,
                         content_type='multipart/form-data',
                         follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_upload_error_message(client, auth):
    """Test upload hata mesajının gösterildiğini kontrol et"""
    auth.login()
    response = client.get('/csv/upload', follow_redirects=True)
    assert response.status_code == 200
    
    data = {
        'file': (BytesIO(b'invalid data'), 'invalid.txt'),
        'report_type': 'business_report'
    }
    response = client.post('/csv/upload',
                         data=data,
                         content_type='multipart/form-data',
                         follow_redirects=True)
    assert response.status_code == 200
    assert b'error' in response.data.lower() or b'danger' in response.data.lower()

def test_file_size_limit(client, auth):
    """Test dosya boyutu limitinin kontrol edildiğini test et"""
    auth.login()
    response = client.get('/csv/upload', follow_redirects=True)
    assert response.status_code == 200
    
    large_file = BytesIO(b'x' * (6 * 1024 * 1024))  # 6MB dosya
    data = {
        'file': (large_file, 'large.csv'),
        'report_type': 'business_report'
    }
    response = client.post('/csv/upload',
                         data=data,
                         content_type='multipart/form-data',
                         follow_redirects=True)
    assert response.status_code == 200
    assert b'5mb' in response.data.lower() or b'boyut' in response.data.lower()

def test_file_type_validation(client, auth):
    """Test dosya tipinin kontrol edildiğini test et"""
    auth.login()
    response = client.get('/csv/upload', follow_redirects=True)
    assert response.status_code == 200
    
    data = {
        'file': (BytesIO(b'test'), 'test.txt'),
        'report_type': 'business_report'
    }
    response = client.post('/csv/upload',
                         data=data,
                         content_type='multipart/form-data',
                         follow_redirects=True)
    assert response.status_code == 200
    assert b'csv' in response.data.lower()
