import pytest
from datetime import datetime, timedelta
from app.utils.analytics_engine import AnalyticsEngine, TimeGrouping
from app.models.reports import BusinessReport
from app.models.store import Store
from app import db

@pytest.fixture
def store(client):
    """Test store oluştur."""
    store = Store(name="Test Store", marketplace="US", user_id=1)
    db.session.add(store)
    db.session.commit()
    return store

@pytest.fixture
def sample_data(store):
    """Test verisi oluştur."""
    today = datetime.now()
    reports = []
    
    # Son 30 günlük test verisi
    for i in range(30):
        date = today - timedelta(days=i)
        report = BusinessReport(
            store_id=store.id,
            created_at=date,
            ordered_product_sales=1000 + (i * 100),  # Artan gelir trendi
            units_ordered=10 + i,
            category="Electronics" if i % 2 == 0 else "Books"
        )
        reports.append(report)
    
    db.session.bulk_save_objects(reports)
    db.session.commit()

def test_revenue_trends_endpoint(client, auth, store, app_context):
    """Revenue trends API testi."""
    auth.login()
    
    response = client.get('/api/analytics/revenue/trends', query_string={
        'store_id': store.id,
        'start_date': '2024-01-01',
        'end_date': '2024-01-07'
    })
    assert response.status_code == 200
    data = response.get_json()
    
    # Response yapısını kontrol et
    assert 'labels' in data
    assert 'values' in data
    assert 'units' in data
    assert 'sessions' in data
    assert 'conversion_rates' in data
    assert 'total_revenue' in data
    assert 'total_units' in data
    assert 'total_sessions' in data
    assert 'average_order_value' in data
    assert 'growth_rate' in data
    assert 'previous_period' in data

def test_revenue_trends_invalid_params(client, auth, store, app_context):
    """Geçersiz parametre testi."""
    auth.login()
    
    # Eksik store_id
    response = client.get('/api/analytics/revenue/trends', query_string={
        'start_date': '2024-01-01',
        'end_date': '2024-01-07'
    })
    assert response.status_code == 400
    assert b'Store ID is required' in response.data
    
    # Geçersiz tarih formatı
    response = client.get('/api/analytics/revenue/trends', query_string={
        'store_id': store.id,
        'start_date': 'invalid',
        'end_date': 'invalid'
    })
    assert response.status_code == 400
    assert b'Invalid date format' in response.data

def test_revenue_trends_with_category(client, auth, store, app_context):
    """Kategori filtreli test."""
    auth.login()
    
    response = client.get('/api/analytics/revenue/trends', query_string={
        'store_id': store.id,
        'start_date': '2024-01-01',
        'end_date': '2024-01-07',
        'category': 'Electronics'
    })
    assert response.status_code == 200
    data = response.get_json()
    
    # Electronics kategorisi için sadece çift günlerdeki veriler olmalı
    assert len(data['values']) <= 4  # 7 günün yarısı 

def test_advertisement_analytics_endpoint(client, auth, store, app_context):
    """Test advertisement analytics endpoint."""
    auth.login()
    
    # Test without date parameters
    response = client.get('/api/analytics/advertisement')
    assert response.status_code == 400
    assert b'Date range is required' in response.data
    
    # Test with invalid date format
    response = client.get('/api/analytics/advertisement?start_date=invalid&end_date=invalid')
    assert response.status_code == 400
    assert b'Invalid date format' in response.data
    
    # Test with valid parameters
    response = client.get(
        '/api/analytics/advertisement?'
        'start_date=2024-01-01&'
        'end_date=2024-01-15'
    )
    assert response.status_code == 200
    data = response.get_json()
    
    # Check response structure
    assert 'labels' in data
    assert 'spend' in data
    assert 'sales' in data
    assert 'ctr' in data
    assert 'cpc' in data
    assert 'conversion_rates' in data
    assert 'total_spend' in data
    assert 'total_sales' in data
    assert 'total_clicks' in data
    assert 'acos' in data
    
    # Test with filters
    response = client.get(
        '/api/analytics/advertisement?'
        'start_date=2024-01-01&'
        'end_date=2024-01-15&'
        'campaign=Test Campaign&'
        'ad_group=Test Ad Group&'
        'targeting_type=Keyword'
    )
    assert response.status_code == 200

def test_advertisement_report_page(client, auth, store, app_context):
    """Test advertisement report page."""
    auth.login()
    
    response = client.get('/analytics/advertisement-report')
    assert response.status_code == 200
    
    # Check if page contains required elements
    assert b'Advertisement Report' in response.data
    assert b'Monitor your advertising performance and metrics' in response.data
    assert b'Date Range' in response.data
    assert b'Campaign' in response.data
    assert b'Ad Group' in response.data
    assert b'Targeting Type' in response.data
    assert b'Total Spend' in response.data
    assert b'Total Sales' in response.data
    assert b'Total Clicks' in response.data
    assert b'ACOS' in response.data 