"""Test cases for Category models."""

import pytest
from datetime import datetime, timezone
from app.modules.category.models.category import Category, ASINCategory
from app.extensions import db

def test_category_creation(database):
    """Test basic category creation."""
    category = Category(
        name="Test Category Creation",
        code="test_creation"
    )
    database.session.add(category)
    database.session.commit()
    
    assert category.id is not None
    assert category.name == "Test Category Creation"
    assert category.code == "test_creation"

def test_category_parent_child_relationship(database):
    """Test parent-child relationship between categories."""
    parent = Category(
        name="Test Parent Category",
        code="test_parent"
    )
    child = Category(
        name="Test Child Category",
        code="test_child"
    )
    
    child.parent = parent
    database.session.add_all([parent, child])
    database.session.commit()
    
    assert child.parent_id == parent.id
    assert child in parent.children

def test_category_unique_code(database):
    """Test that category codes must be unique."""
    category1 = Category(
        name="Test Category 1",
        code="test_unique"
    )
    database.session.add(category1)
    database.session.commit()
    
    category2 = Category(
        name="Test Category 2",
        code="test_unique"
    )
    database.session.add(category2)
    with pytest.raises(Exception):
        database.session.commit()

def test_asin_category_mapping(database):
    """Test ASIN to category mapping."""
    category = Category(
        name="Test ASIN Category",
        code="test_asin"
    )
    database.session.add(category)
    database.session.flush()
    
    asin_category = ASINCategory(
        asin="B00TEST123",
        category_id=category.id,
        title="Test Product",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    database.session.add(asin_category)
    database.session.commit()
    
    assert len(category.asin_categories) == 1
    assert category.asin_categories[0].asin == "B00TEST123"

def test_category_to_dict(database):
    """Test category to dictionary conversion."""
    electronics = Category(
        name="Test Dict Electronics",
        code="test_dict_electronics"
    )
    database.session.add(electronics)
    database.session.flush()
    
    phones = Category(
        name="Test Dict Phones",
        code="test_dict_phones",
        parent_id=electronics.id
    )
    database.session.add(phones)
    database.session.commit()
    
    result = electronics.to_dict()
    assert result["name"] == "Test Dict Electronics"
    assert result["code"] == "test_dict_electronics"
    assert len(result["children"]) == 1
    assert result["children"][0]["name"] == "Test Dict Phones"

def test_asin_category_unique_constraint(database):
    """Test ASIN category constraints."""
    category = Category(
        name="Test Constraint Category",
        code="test_constraint"
    )
    database.session.add(category)
    database.session.flush()
    
    asin_category = ASINCategory(
        asin="B01UNIQUE123",
        category_id=category.id,
        title="Test Product",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    database.session.add(asin_category)
    database.session.commit()
    
    # Same ASIN can be added to different categories
    category2 = Category(
        name="Test Constraint Category 2",
        code="test_constraint2"
    )
    database.session.add(category2)
    database.session.flush()
    
    asin_category2 = ASINCategory(
        asin="B01UNIQUE123",
        category_id=category2.id,
        title="Test Product 2",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc)
    )
    database.session.add(asin_category2)
    database.session.commit()
    
    assert ASINCategory.query.filter_by(asin="B01UNIQUE123").count() == 2
