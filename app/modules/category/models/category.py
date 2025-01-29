"""Category models for Amazon Seller Support."""

from datetime import datetime
from typing import List, Optional
from app.extensions import db

class Category(db.Model):
    """Category model for organizing products.
    
    Attributes:
        id: Primary key.
        name: Category name.
        code: Category code (e.g., 'electronics', 'books').
        parent_id: ID of parent category if any.
        created_at: Creation timestamp.
        parent: Parent category relationship.
        subcategories: Child categories relationship.
    """
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(50), nullable=False, unique=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    parent = db.relationship('Category', remote_side=[id], backref='subcategories')
    
    def __repr__(self) -> str:
        return f'<Category {self.name}>'
    
    def to_dict(self) -> dict:
        """Convert category to dictionary.
        
        Returns:
            Dictionary representation of category.
        """
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'parent_id': self.parent_id,
            'created_at': self.created_at.isoformat(),
            'subcategories': [sub.to_dict() for sub in self.subcategories]
        }

class ASINCategory(db.Model):
    """ASIN-Category mapping model.
    
    Attributes:
        id: Primary key.
        asin: Amazon Standard Identification Number.
        category_id: Foreign key to Category.
        title: Product title.
        created_at: Creation timestamp.
        category: Category relationship.
    """
    __tablename__ = 'asin_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(10), unique=True, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    title = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    category = db.relationship('Category', backref='asins')
    
    def __repr__(self) -> str:
        return f'<ASINCategory {self.asin}>'
    
    def to_dict(self) -> dict:
        """Convert ASIN-Category mapping to dictionary.
        
        Returns:
            Dictionary representation of ASIN-Category mapping.
        """
        return {
            'id': self.id,
            'asin': self.asin,
            'category_id': self.category_id,
            'title': self.title,
            'created_at': self.created_at.isoformat(),
            'category': self.category.to_dict() if self.category else None
        }