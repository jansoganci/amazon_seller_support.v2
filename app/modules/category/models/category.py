"""Category models for Amazon Seller Support.

This module defines the database models for category management, including:
- Category: Main category model with hierarchical structure
- ASINCategory: Many-to-Many mapping between ASINs and categories
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import relationship
from app.extensions import db

class Category(db.Model):
    """Category model with hierarchical structure.
    
    Attributes:
        id: Primary key
        name: Human-readable category name (e.g., "Electronics", "Books")
        code: Machine-readable category code (e.g., "electronics", "books")
        description: Optional category description
        parent_id: ID of parent category (None for root categories)
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        parent: Parent category relationship
        children: Child categories relationship
        asin_categories: Related ASINCategory mappings
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship('Category', remote_side=[id], backref='children')
    asin_categories = relationship('ASINCategory', back_populates='category')
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'
    
    def to_dict(self, include_children: bool = True) -> Dict[str, Any]:
        """Convert category to dictionary.
        
        Args:
            include_children: Whether to include child categories in output
            
        Returns:
            Dictionary with category data including:
            - Basic info (id, name, code, description)
            - Timestamps (created_at, updated_at)
            - Relationships (parent_id, children if requested)
            - Stats (asin_count)
        """
        result = {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'description': self.description,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'asin_count': len(self.asin_categories)
        }
        
        if include_children:
            result['children'] = [child.to_dict(include_children=False) 
                                for child in self.children]
        
        return result

class ASINCategory(db.Model):
    """ASIN-Category mapping model for Many-to-Many relationships.
    
    This model allows:
    - One ASIN to be mapped to multiple categories
    - Both main categories and subcategories to have ASINs
    - Tracking of product details per category
    
    Attributes:
        id: Primary key
        asin: Amazon Standard Identification Number
        category_id: Foreign key to Category
        title: Product title from Amazon
        description: Optional product description
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
        category: Related Category
    """
    __tablename__ = 'asin_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    asin = db.Column(db.String(10), nullable=False, index=True)  # Removed unique constraint
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)  # Made required
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Add composite unique constraint for asin + category_id
    __table_args__ = (
        db.UniqueConstraint('asin', 'category_id', name='uix_asin_category'),
    )
    
    # Relationships
    category = relationship('Category', back_populates='asin_categories')
    
    def __repr__(self) -> str:
        return f'<ASINCategory {self.asin}>'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert ASIN-Category mapping to dictionary.
        
        Returns:
            Dictionary with mapping data including:
            - Basic info (id, asin, title, description)
            - Category info (id, name, code)
            - Timestamps (created_at, updated_at)
        """
        return {
            'id': self.id,
            'asin': self.asin,
            'category_id': self.category_id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'category': {
                'id': self.category.id,
                'name': self.category.name,
                'code': self.category.code
            } if self.category else None
        }