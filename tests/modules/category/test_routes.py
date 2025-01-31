"""Test category routes."""

import json
import pytest
from flask import url_for
from flask_login import login_user
from app.modules.category.models.category import Category, ASINCategory

def login_test_user(client, user):
    """Log in test user."""
    with client:
        with client.session_transaction() as sess:
            sess['_user_id'] = user.get_id()
            sess['_fresh'] = True

@pytest.mark.parametrize('user_fixture', ['admin_user', 'regular_user'])
def test_get_categories(client, request, user_fixture):
    """Test getting categories."""
    user = request.getfixturevalue(user_fixture)
    login_test_user(client, user)
    
    response = client.get('/api/v1/categories/')
    
    if user_fixture == 'admin_user':
        assert response.status_code == 200
        assert 'data' in response.json
    else:
        # Regular users should not have access to category management
        assert response.status_code == 403
        assert response.json is not None
        assert 'error' in response.json

def test_get_categories_unauthorized(client):
    """Test getting categories without authentication."""
    response = client.get('/api/v1/categories/')
    assert response.status_code == 401
    assert response.json is not None
    assert 'error' in response.json

def test_create_category_as_admin(client, admin_user):
    """Test creating category as admin."""
    login_test_user(client, admin_user)
    
    data = {
        'name': 'Test Category',
        'code': 'test_category',
        'description': 'Test category description'
    }
    
    response = client.post('/api/v1/categories/', 
                          json=data)
    
    assert response.status_code == 201
    assert response.json is not None
    assert 'data' in response.json

def test_create_category_as_regular_user(client, regular_user):
    """Test creating category as regular user."""
    login_test_user(client, regular_user)
    
    data = {
        'name': 'Test Category',
        'code': 'test_category',
        'description': 'Test category description'
    }
    
    response = client.post('/api/v1/categories/', 
                          json=data)
    
    assert response.status_code == 403
    assert response.json is not None
    assert 'error' in response.json

def test_create_category_validation(client, admin_user):
    """Test category creation validation."""
    login_test_user(client, admin_user)
    
    # Test missing required fields
    response = client.post('/api/v1/categories/', 
                          json={})
    assert response.status_code == 400
    assert response.json is not None
    assert 'error' in response.json
    
    # Test missing code
    response = client.post('/api/v1/categories/', 
                          json={'name': 'Test Category'})
    assert response.status_code == 400
    assert response.json is not None
    assert 'error' in response.json

def test_get_asin_categories(client, regular_user):
    """Test getting ASIN categories."""
    login_test_user(client, regular_user)
    
    response = client.get('/api/v1/categories/asin/B01EXAMPLE')
    
    # Regular users should not have access to category management
    assert response.status_code == 403
    assert response.json is not None
    assert 'error' in response.json

def test_assign_asin_category(client, admin_user):
    """Test assigning category to ASIN."""
    login_test_user(client, admin_user)
    
    data = {
        'asin': 'B01EXAMPLE',
        'category_code': 'test_category',
        'title': 'Test Product'
    }
    
    # First create the category
    category_data = {
        'name': 'Test Category',
        'code': 'test_category',
        'description': 'Test category description'
    }
    client.post('/api/v1/categories/', json=category_data)
    
    # Then assign ASIN to category
    response = client.post('/api/v1/categories/asin', 
                          json=data)
    
    assert response.status_code == 201
    assert response.json is not None
    assert 'data' in response.json

def test_bulk_assign_categories(client, admin_user):
    """Test bulk assigning categories."""
    login_test_user(client, admin_user)
    
    # First create the category
    category_data = {
        'name': 'Test Category',
        'code': 'test_category',
        'description': 'Test category description'
    }
    client.post('/api/v1/categories/', json=category_data)
    
    data = {
        'mappings': [
            {
                'asin': 'B01EXAMPLE1',
                'category_code': 'test_category',
                'title': 'Test Product 1'
            },
            {
                'asin': 'B01EXAMPLE2',
                'category_code': 'test_category',
                'title': 'Test Product 2'
            }
        ]
    }
    
    response = client.post('/api/v1/categories/asin/bulk', 
                          json=data)
    
    assert response.status_code == 201
    assert response.json is not None
    assert 'data' in response.json

def test_bulk_assign_categories_validation(client, admin_user):
    """Test bulk assignment validation."""
    login_test_user(client, admin_user)
    
    # Test missing mappings
    response = client.post('/api/v1/categories/asin/bulk', 
                          json={})
    assert response.status_code == 400
    assert response.json is not None
    assert 'error' in response.json
    
    # Test invalid mappings format
    response = client.post('/api/v1/categories/asin/bulk', 
                          json={'mappings': {}})
    assert response.status_code == 400
    assert response.json is not None
    assert 'error' in response.json
