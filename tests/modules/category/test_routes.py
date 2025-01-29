"""Test cases for category routes."""

import json
import pytest
from flask import url_for
from flask_login import login_user
from app.modules.category.models.category import Category, ASINCategory

def login_test_user(client, user):
    """Helper function to login test user."""
    with client.application.test_request_context():
        login_user(user)

@pytest.mark.parametrize("user_fixture", ["admin_user", "regular_user"])
def test_get_categories(client, request, user_fixture):
    """Test getting categories."""
    user = request.getfixturevalue(user_fixture)
    login_test_user(client, user)

    response = client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = json.loads(response.data.decode())
    assert "data" in data

def test_get_categories_unauthorized(client):
    """Test GET /api/categories/ without authentication."""
    response = client.get("/api/v1/categories/")
    assert response.status_code == 401

def test_create_category_as_admin(client, admin_user):
    """Test POST /api/categories/ as admin."""
    login_test_user(client, admin_user)
    
    data = {
        "name": "Test Route Category",
        "code": "test_route_cat",
        "description": "Test Description"
    }
    
    response = client.post(
        "/api/v1/categories/",
        json=data
    )
    assert response.status_code == 201
    
    result = json.loads(response.data)
    assert result["data"]["name"] == "Test Route Category"
    assert result["data"]["code"] == "test_route_cat"

def test_create_category_as_regular_user(client, regular_user):
    """Test POST /api/categories/ as regular user."""
    login_test_user(client, regular_user)
    
    data = {
        "name": "Test Regular User Category",
        "code": "test_regular_cat"
    }
    
    response = client.post(
        "/api/v1/categories/",
        json=data
    )
    assert response.status_code == 403  # Forbidden

def test_create_category_validation(client, admin_user):
    """Test category creation validation."""
    login_test_user(client, admin_user)

    # Test missing required fields
    response = client.post(
        "/api/v1/categories/",
        json={}
    )
    assert response.status_code == 400
    data = json.loads(response.data.decode())
    assert "error" in data

    # Test invalid parent code
    data = {
        "name": "Test Invalid Parent",
        "code": "test_invalid_parent",
        "parent_code": "nonexistent"
    }
    response = client.post(
        "/api/v1/categories/",
        json=data
    )
    assert response.status_code == 400

def test_get_asin_categories(client, regular_user, sample_asins):
    """Test GET /api/categories/asin/{asin} endpoint."""
    login_test_user(client, regular_user)
    
    # Test existing ASIN
    asin = sample_asins[0].asin
    response = client.get(f"/api/v1/categories/asin/{asin}")
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert len(data["data"]) == 1
    
    # Test non-existent ASIN
    response = client.get("/api/v1/categories/asin/NONEXISTENT")
    assert response.status_code == 404
    data = json.loads(response.data)
    assert "error" in data

def test_assign_asin_category(client, admin_user, category_tree):
    """Test POST /api/categories/asin endpoint."""
    login_test_user(client, admin_user)
    
    data = {
        "asin": "B00ROUTE123",
        "category_code": category_tree.code,
        "title": "Test Product Route",
        "description": "Test Description"
    }
    
    response = client.post(
        "/api/v1/categories/asin",
        json=data
    )
    assert response.status_code == 201
    
    result = json.loads(response.data)
    assert result["data"]["asin"] == "B00ROUTE123"
    assert result["data"]["title"] == "Test Product Route"

def test_bulk_assign_categories(client, admin_user, category_tree):
    """Test POST /api/categories/asin/bulk endpoint."""
    login_test_user(client, admin_user)
    
    data = {
        "mappings": [
            {
                "asin": "B00BULK1",
                "category_code": category_tree.code,
                "title": "Test Bulk Product 1"
            },
            {
                "asin": "B00BULK2",
                "category_code": category_tree.code,
                "title": "Test Bulk Product 2"
            }
        ]
    }
    
    response = client.post(
        "/api/v1/categories/asin/bulk",
        json=data
    )
    assert response.status_code == 201
    
    result = json.loads(response.data)
    assert len(result["data"]) == 2

def test_bulk_assign_categories_validation(client, admin_user):
    """Test bulk assignment validation."""
    login_test_user(client, admin_user)
    
    # Missing mappings
    response = client.post(
        "/api/v1/categories/asin/bulk",
        json={}
    )
    assert response.status_code == 400
    
    # Invalid category code
    data = {
        "mappings": [
            {
                "asin": "B00INVALID1",
                "category_code": "nonexistent",
                "title": "Test Invalid"
            }
        ]
    }
    response = client.post(
        "/api/v1/categories/asin/bulk",
        json=data
    )
    assert response.status_code == 400
