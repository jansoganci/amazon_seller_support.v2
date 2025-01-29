"""Test cases for CategoryService."""

import pytest
from app.modules.category.services.category_service import CategoryService
from app.modules.category.models.category import Category, ASINCategory
from app import db
from datetime import datetime, UTC

def test_get_category_by_code(app, category_tree):
    """Test retrieving a category by its code."""
    with app.app_context():
        category = CategoryService.get_category_by_code(category_tree.code)
        assert category is not None
        assert category.name == category_tree.name

def test_get_category_tree(app, category_tree):
    """Test retrieving the full category tree."""
    with app.app_context():
        tree = CategoryService.get_category_tree()
        assert len(tree) > 0
        root = next(cat for cat in tree if cat["code"] == category_tree.code)
        assert root is not None
        assert len(root["children"]) == 2

def test_create_category(app):
    """Test category creation through service."""
    with app.app_context():
        category = CategoryService.create_category(
            name="Test Service Category",
            code="test_service_cat",
            description="Test Description"
        )
        assert category.name == "Test Service Category"
        assert category.code == "test_service_cat"
        assert category.description == "Test Description"

def test_create_subcategory(app, category_tree):
    """Test subcategory creation."""
    with app.app_context():
        subcategory = CategoryService.create_category(
            name="Test Service Subcategory",
            code="test_service_subcat",
            description="Test Subcategory",
            parent_code=category_tree.code
        )
        assert subcategory.parent.code == category_tree.code
        assert subcategory in subcategory.parent.children

def test_get_asin_categories(app, category_tree):
    """Test retrieving ASIN categories."""
    with app.app_context():
        # Create test data
        category = Category(name="Smartphones", code="service_asin_smartphones")
        db.session.add(category)
        db.session.commit()

        asin = "B123456789"
        mapping = ASINCategory(
            asin=asin,
            category=category,
            title="Test Phone",
            description="Test Description"
        )
        db.session.add(mapping)
        db.session.commit()

        # Test retrieval
        categories = CategoryService.get_asin_categories(asin)
        assert len(categories) == 1
        assert categories[0]["category"] == "Smartphones"

def test_assign_asin_category(app, category_tree):
    """Test assigning an ASIN to a category."""
    with app.app_context():
        asin_data = {
            "asin": "B00TESTX1",
            "title": "Test Product X1",
            "description": "Test Description"
        }
        result = CategoryService.assign_asin_category(
            asin=asin_data["asin"],
            category_code=category_tree.code,
            title=asin_data["title"],
            description=asin_data["description"]
        )
        
        # Verify assignment
        mapping = ASINCategory.query.filter_by(asin=asin_data["asin"]).first()
        assert mapping is not None
        assert mapping.category.code == category_tree.code
        assert mapping.title == asin_data["title"]

def test_bulk_assign_categories(app, category_tree):
    """Test bulk assignment of ASINs to categories."""
    with app.app_context():
        assignments = [
            {
                "asin": f"B01BULK{i}",
                "category_code": category_tree.code,
                "title": f"Test Product {i}",
                "description": f"Test Description {i}"
            }
            for i in range(3)
        ]
        
        result = CategoryService.bulk_assign_categories(assignments)
        assert len(result) == 3
        
        # Verify assignments
        for i, mapping in enumerate(result):
            assert mapping.asin == f"B01BULK{i}"
            assert mapping.category.code == category_tree.code
            assert mapping.title == f"Test Product {i}"
