"""Test store validation functionality."""

import pytest
from flask import url_for
from http import HTTPStatus
from app.models import Store
from app.extensions import db
from app.exceptions import ValidationError
from app.models import User

def test_store_id_missing(authenticated_client):
    """Test accessing a route without store_id."""
    response = authenticated_client.get(url_for('analytics.business_report'))
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_invalid_store_id(authenticated_client):
    """Test accessing a route with invalid store_id."""
    response = authenticated_client.get(
        url_for('analytics.business_report', store_id=999)
    )
    assert response.status_code == HTTPStatus.NOT_FOUND


def test_store_id_validation(authenticated_client, test_store):
    """Test store_id validation."""
    response = authenticated_client.get(
        url_for('analytics.business_report', store_id=test_store.id)
    )
    assert response.status_code == HTTPStatus.OK


def test_store_ownership_validation(app, authenticated_client, test_user):
    """Test store ownership validation."""
    with app.app_context():
        # Create a store owned by another user
        other_user = User(
            email='other@example.com',
            username='other_user'
        )
        other_user.set_password('secure_password')
        db.session.add(other_user)
        db.session.commit()

        other_store = Store(
            name='Other Store',
            marketplace='US',
            user_id=other_user.id
        )
        db.session.add(other_store)
        db.session.commit()

        # Try to access other user's store
        response = authenticated_client.get(
            url_for('analytics.business_report', store_id=other_store.id)
        )
        assert response.status_code == HTTPStatus.FORBIDDEN


def test_multiple_stores_handling(app, authenticated_client, test_user):
    """Test handling multiple stores for a user."""
    with app.app_context():
        # Create additional stores for the test user
        store_1 = Store(
            name='Store 1',
            marketplace='US',
            user_id=test_user.id
        )
        store_2 = Store(
            name='Store 2',
            marketplace='DE',
            user_id=test_user.id
        )
        db.session.add_all([store_1, store_2])
        db.session.commit()

        # Test access to all stores
        for store in [store_1, store_2]:
            response = authenticated_client.get(
                url_for('analytics.business_report', store_id=store.id)
            )
            assert response.status_code == HTTPStatus.OK


def test_marketplace_validation(app, authenticated_client, test_user):
    """Test marketplace validation."""
    with app.app_context():
        # Create stores with different marketplaces
        store = Store(
            name='Test Store',
            marketplace='INVALID',
            user_id=test_user.id
        )
        db.session.add(store)
        
        # Should raise validation error
        with pytest.raises(ValidationError):
            db.session.commit()
