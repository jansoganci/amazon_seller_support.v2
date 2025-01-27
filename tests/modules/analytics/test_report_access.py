"""Test access to individual report types."""

import pytest
from flask import url_for
from http import HTTPStatus

@pytest.mark.parametrize('report_route,report_title', [
    ('business.report', 'Business Reports'),
    ('advertising.advertising_report', 'Advertisement Reports'),
    ('inventory.inventory_report', 'Inventory Reports'),
    ('returns.return_report', 'Return Reports')
])
def test_report_access_unauthorized(client, report_route, report_title):
    """Test that unauthorized users cannot access reports."""
    response = client.get(url_for(report_route))
    assert response.status_code == HTTPStatus.FOUND
    assert '/auth/login' in response.headers['Location']

@pytest.mark.parametrize('report_route,report_title', [
    ('business.report', 'Business Reports'),
    ('advertising.advertising_report', 'Advertisement Reports'),
    ('inventory.inventory_report', 'Inventory Reports'),
    ('returns.return_report', 'Return Reports')
])
def test_report_access_authorized(authenticated_client, report_route, report_title):
    """Test that authorized users can access reports."""
    response = authenticated_client.get(url_for(report_route))
    assert response.status_code == HTTPStatus.OK
    assert report_title.encode() in response.data

def test_business_report_content(authenticated_client, test_business_report):
    """Test business report specific content."""
    response = authenticated_client.get(url_for('business.report'))
    assert response.status_code == HTTPStatus.OK
    assert str(test_business_report.total_sales).encode() in response.data
    assert str(test_business_report.total_orders).encode() in response.data

def test_advertising_report_content(authenticated_client, test_advertising_report):
    """Test advertising report specific content."""
    response = authenticated_client.get(url_for('advertising.advertising_report'))
    assert response.status_code == HTTPStatus.OK
    assert test_advertising_report.campaign_name.encode() in response.data
    assert str(test_advertising_report.impressions).encode() in response.data

def test_inventory_report_content(authenticated_client, test_inventory_report):
    """Test inventory report specific content."""
    response = authenticated_client.get(url_for('inventory.inventory_report'))
    assert response.status_code == HTTPStatus.OK
    assert test_inventory_report.sku.encode() in response.data
    assert str(test_inventory_report.quantity).encode() in response.data

def test_return_report_content(authenticated_client, test_return_report):
    """Test return report specific content."""
    response = authenticated_client.get(url_for('returns.return_report'))
    assert response.status_code == HTTPStatus.OK
    assert test_return_report.order_id.encode() in response.data
    assert test_return_report.return_reason.encode() in response.data
