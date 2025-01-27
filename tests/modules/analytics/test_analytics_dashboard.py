"""Test analytics dashboard functionality."""

import pytest
from flask import url_for
from http import HTTPStatus

def test_analytics_dashboard_access_unauthorized(client):
    """Test that unauthorized users are redirected to login."""
    response = client.get(url_for('analytics.dashboard'))
    assert response.status_code == HTTPStatus.FOUND
    assert '/auth/login' in response.headers['Location']

def test_analytics_dashboard_access_authorized(authenticated_client):
    """Test that authorized users can access the dashboard."""
    response = authenticated_client.get(url_for('analytics.dashboard'))
    assert response.status_code == HTTPStatus.OK
    assert b'Analytics Overview' in response.data

def test_analytics_dashboard_content(authenticated_client):
    """Test that dashboard contains all required report cards."""
    response = authenticated_client.get(url_for('analytics.dashboard'))
    assert response.status_code == HTTPStatus.OK
    
    # Check for report card titles
    assert b'Business Reports' in response.data
    assert b'Advertisement Reports' in response.data
    assert b'Inventory Reports' in response.data
    assert b'Return Reports' in response.data

def test_analytics_dashboard_report_links(authenticated_client):
    """Test that all report links are present and valid."""
    response = authenticated_client.get(url_for('analytics.dashboard'))
    assert response.status_code == HTTPStatus.OK
    
    # Check for report links
    assert url_for('business.report') in response.data.decode()
    assert url_for('advertising.advertising_report') in response.data.decode()
    assert url_for('inventory.inventory_report') in response.data.decode()
    assert url_for('returns.return_report') in response.data.decode()

def test_analytics_dashboard_store_selection(authenticated_client, test_store):
    """Test store selection functionality."""
    response = authenticated_client.get(
        url_for('analytics.dashboard'),
        data={'store_id': test_store.id}
    )
    assert response.status_code == HTTPStatus.OK
    # Add store-specific assertions here

def test_analytics_dashboard_no_store_selected(authenticated_client):
    """Test dashboard behavior when no store is selected."""
    response = authenticated_client.get(url_for('analytics.dashboard'))
    assert response.status_code == HTTPStatus.OK
    # Add assertions for no-store state
