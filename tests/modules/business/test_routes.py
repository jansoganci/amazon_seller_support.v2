"""Test business routes."""

import pytest
from datetime import datetime, UTC
from decimal import Decimal
import json
from flask_login import current_user
from flask import url_for

from app.modules.business.models import BusinessReport
from app.core.models.store import Store
from app.core.models.user import User
from app.extensions import db

@pytest.fixture
def auth_headers(app, test_user):
    """Get authentication headers."""
    with app.test_client() as client:
        response = client.post('/auth/login', json={
            'email': 'test@example.com',
            'password': 'password'
        })
        token = response.json['access_token']
        return {'Authorization': f'Bearer {token}'}

def test_get_business_reports(client, test_business_report, auth_headers):
    """Test getting business reports."""
    response = client.get('/business/reports', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['reports']) == 1
    assert data['reports'][0]['id'] == test_business_report.id

def test_get_business_report_detail(client, test_business_report, auth_headers):
    """Test getting a specific business report."""
    response = client.get(f'/business/reports/{test_business_report.id}', headers=auth_headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['id'] == test_business_report.id
    assert Decimal(str(data['total_sales'])) == test_business_report.total_sales

def test_create_business_report(client, test_store, auth_headers):
    """Test creating a business report."""
    data = {
        'store_id': test_store.id,
        'date': datetime.now(UTC).isoformat(),
        'total_sales': '1000.00',
        'total_orders': 100,
        'total_units': 150,
        'average_selling_price': '10.00',
        'gross_profit': '500.00',
        'profit_margin': '50.00'
    }
    response = client.post('/business/reports', json=data, headers=auth_headers)
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['store_id'] == test_store.id

def test_update_business_report(client, test_business_report, auth_headers):
    """Test updating a business report."""
    data = {
        'total_sales': '2000.00',
        'total_orders': 200
    }
    response = client.put(
        f'/business/reports/{test_business_report.id}',
        json=data,
        headers=auth_headers
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert Decimal(str(data['total_sales'])) == Decimal('2000.00')
    assert data['total_orders'] == 200

def test_delete_business_report(client, test_business_report, auth_headers):
    """Test deleting a business report."""
    response = client.delete(
        f'/business/reports/{test_business_report.id}',
        headers=auth_headers
    )
    assert response.status_code == 204
    assert BusinessReport.query.get(test_business_report.id) is None

def test_unauthorized_access(client, test_business_report):
    """Test unauthorized access to business reports."""
    response = client.get('/business/reports')
    assert response.status_code == 401

def test_business_report_not_found(client, auth_headers):
    """Test accessing non-existent business report."""
    response = client.get('/business/reports/999', headers=auth_headers)
    assert response.status_code == 404

def test_invalid_report_data(client, test_store, auth_headers):
    """Test creating report with invalid data."""
    data = {
        'store_id': test_store.id,
        'date': 'invalid-date',  # Invalid date format
        'total_sales': 'not-a-number'  # Invalid decimal
    }
    response = client.post('/business/reports', json=data, headers=auth_headers)
    assert response.status_code == 400
