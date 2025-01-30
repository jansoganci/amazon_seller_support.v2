"""Category models for Amazon Seller Support."""

from app.extensions import db
from datetime import datetime

class Category(db.Model):
    """Category model."""
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text)
    parent_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    children = db.relationship('Category', 
                             backref=db.backref('parent', remote_side=[id]),
                             lazy='dynamic')
    asins = db.relationship('CategoryAsin', back_populates='category')

    def __repr__(self):
        """String representation."""
        return f'<Category {self.name}>'

class CategoryAsin(db.Model):
    """CategoryAsin model for mapping ASINs to categories."""
    __tablename__ = 'category_asins'

    id = db.Column(db.Integer, primary_key=True)
    asin = db.Column(db.String(10), nullable=False, index=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    category = db.relationship('Category', back_populates='asins')

    def __repr__(self):
        """String representation."""
        return f'<CategoryAsin {self.asin}>'
