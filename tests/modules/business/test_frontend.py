"""Test cases for the business report frontend."""

import pytest
from bs4 import BeautifulSoup
from flask import url_for

def test_business_report_page_load(client, auth_headers, test_store):
    """Test business report page loads correctly."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'Business Report' in response.data

def test_metric_card_rendering(client, auth_headers, test_store, sample_business_report):
    """Test metric cards render correctly."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'Revenue' in response.data
    assert b'Orders' in response.data
    assert b'Average Order Value' in response.data

def test_chart_container_rendering(client, auth_headers, test_store, sample_business_report):
    """Test chart containers render correctly."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'chart-container' in response.data

def test_filter_controls(client, auth_headers, test_store):
    """Test filter controls are present."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'dateRangePicker' in response.data
    assert b'filterControls' in response.data

def test_api_endpoints(client, auth_headers, test_store, sample_business_report):
    """Test API endpoints return correct data."""
    response = client.get(f'/business/{test_store.id}/api/report-data', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'ordered_product_sales' in data
    assert 'total_order_items' in data
    assert 'conversion_rate' in data

def test_filter_application(client, auth_headers, test_store, sample_business_report):
    """Test filter application works."""
    response = client.get(
        f'/business/{test_store.id}/api/report-data?start_date=2025-01-01&end_date=2025-01-31',
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)

def test_error_handling(client, auth_headers, test_store):
    """Test error handling."""
    response = client.get(f'/business/{test_store.id}/api/report-data', headers=auth_headers)
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data

def test_responsive_layout(client, auth_headers, test_store):
    """Test responsive layout classes."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'grid' in response.data
    assert b'flex' in response.data

def test_chart_interactions(client, auth_headers, test_store, sample_business_report):
    """Test chart interaction endpoints."""
    response = client.get(f'/business/{test_store.id}/api/chart-data/daily', headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, dict)
    assert 'labels' in data
    assert 'datasets' in data

def test_accessibility(client, auth_headers, test_store):
    """Test accessibility attributes."""
    response = client.get(f'/business/{test_store.id}/report', headers=auth_headers)
    assert response.status_code == 200
    assert b'aria-label' in response.data
    assert b'role=' in response.data
