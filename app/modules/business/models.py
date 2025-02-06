"""Business report models."""
from datetime import datetime
from typing import Optional, List
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from app.extensions import db
from app.modules.category.models.category import Category

class BusinessReport(db.Model):
    """Business report model for storing Amazon seller business data."""
    __tablename__ = 'business_reports'

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    store_id: Mapped[int] = mapped_column(db.Integer, ForeignKey('stores.id'), nullable=False)
    date: Mapped[datetime] = mapped_column(db.DateTime, nullable=False)
    sku: Mapped[str] = mapped_column(db.String(50), nullable=False)
    asin: Mapped[str] = mapped_column(db.String(20), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    sessions: Mapped[int] = mapped_column(db.Integer, default=0)
    units_ordered: Mapped[int] = mapped_column(db.Integer, default=0)
    ordered_product_sales: Mapped[float] = mapped_column(db.Numeric(10, 2), default=0)
    total_order_items: Mapped[int] = mapped_column(db.Integer, default=0)
    conversion_rate: Mapped[float] = mapped_column(db.Numeric(5, 2), default=0)
    
    # Metadata
    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    store: Mapped['Store'] = relationship('Store', back_populates='business_reports')
    categories: Mapped[List[Category]] = relationship(
        Category,
        secondary='asin_categories',
        primaryjoin='BusinessReport.asin == asin_categories.c.asin',
        secondaryjoin='asin_categories.c.category_id == Category.id',
        viewonly=True
    )

    def __repr__(self) -> str:
        """String representation."""
        return f'<BusinessReport {self.id} - Store {self.store_id} - {self.date} - {self.sku}>'

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        # Get category info from the relationship
        categories = [cat for cat in self.categories if cat.parent_id is None]
        subcategories = [cat for cat in self.categories if cat.parent_id is not None]

        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.isoformat(),
            'sku': self.sku,
            'asin': self.asin,
            'title': self.title,
            'category': categories[0].name if categories else None,
            'subcategory': subcategories[0].name if subcategories else None,
            'sessions': self.sessions,
            'units_ordered': self.units_ordered,
            'ordered_product_sales': float(self.ordered_product_sales),
            'total_order_items': self.total_order_items,
            'conversion_rate': float(self.conversion_rate),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

        return {
            'id': self.id,
            'store_id': self.store_id,
            'date': self.date.isoformat(),
            'sku': self.sku,
            'asin': self.asin,
            'title': self.title,
            'category': category_info.categories.split(',')[0] if category_info and category_info.categories else None,
            'subcategory': category_info.subcategories.split(',')[0] if category_info and category_info.subcategories else None,
            'sessions': self.sessions,
            'units_ordered': self.units_ordered,
            'ordered_product_sales': float(self.ordered_product_sales),
            'total_order_items': self.total_order_items,
            'conversion_rate': float(self.conversion_rate),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
