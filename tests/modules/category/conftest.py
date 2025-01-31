"""Test fixtures for category module."""

import pytest
import uuid
from datetime import datetime, UTC
from app.extensions import db, bcrypt
from app.modules.auth.models import User
from app.modules.category.models.category import Category, ASINCategory

@pytest.fixture
def category_tree(database):
    """Create a sample category tree."""
    # Create root category with unique code
    code_suffix = str(uuid.uuid4())[:8]
    electronics = Category(
        name=f"Test Electronics {code_suffix}",
        code=f"test_electronics_{code_suffix}"
    )
    database.session.add(electronics)
    database.session.flush()  # Get ID before creating children
    
    # Create child categories with unique codes
    smartphones = Category(
        name=f"Test Smartphones {code_suffix}",
        code=f"test_smartphones_{code_suffix}",
        parent_id=electronics.id
    )
    laptops = Category(
        name=f"Test Laptops {code_suffix}",
        code=f"test_laptops_{code_suffix}",
        parent_id=electronics.id
    )
    database.session.add_all([smartphones, laptops])
    
    # Create smartphone subcategories with unique codes
    iphone = Category(
        name=f"Test iPhone {code_suffix}",
        code=f"test_iphone_{code_suffix}",
        parent_id=smartphones.id
    )
    android = Category(
        name=f"Test Android {code_suffix}",
        code=f"test_android_{code_suffix}",
        parent_id=smartphones.id
    )
    database.session.add_all([iphone, android])
    database.session.commit()
    
    return electronics

@pytest.fixture
def sample_asins(database, category_tree):
    """Create sample ASIN categories."""
    code_suffix = str(uuid.uuid4())[:8]
    asins = [
        ASINCategory(
            asin=f"B00TEST{code_suffix}{i}",
            category_id=category_tree.id,
            title=f"Test Product {i} {code_suffix}",
            description=f"Test Description {i}",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        for i in range(5)
    ]
    database.session.add_all(asins)
    database.session.commit()
    return asins

@pytest.fixture
def admin_user(database):
    """Create an admin user."""
    code_suffix = str(uuid.uuid4())[:8]
    user = User(
        username=f"test_admin_{code_suffix}",
        email=f"test_admin_{code_suffix}@example.com",
        role="admin",
        is_active=True
    )
    user.set_password("admin123")
    database.session.add(user)
    database.session.commit()
    return user

@pytest.fixture
def regular_user(database):
    """Create a regular user."""
    code_suffix = str(uuid.uuid4())[:8]
    user = User(
        username=f"test_user_{code_suffix}",
        email=f"test_user_{code_suffix}@example.com",
        role="user",
        is_active=True
    )
    user.set_password("user123")
    database.session.add(user)
    database.session.commit()
    return user
