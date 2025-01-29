"""Category service layer for Amazon Seller Support."""

from typing import List, Optional, Dict, Any
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.category.models.category import Category, ASINCategory

class CategoryService:
    """Service class for category operations."""
    
    def get_category_by_code(self, code: str) -> Optional[Category]:
        """Get category by its code.
        
        Args:
            code: Category code.
            
        Returns:
            Category object if found, None otherwise.
        """
        return Category.query.filter_by(code=code).first()
    
    def get_category_tree(self) -> List[Dict[str, Any]]:
        """Get complete category tree.
        
        Returns:
            List of top-level categories with their subcategories.
        """
        root_categories = Category.query.filter_by(parent_id=None).all()
        return [cat.to_dict() for cat in root_categories]
    
    def create_category(self, name: str, code: str, parent_code: Optional[str] = None) -> Category:
        """Create a new category.
        
        Args:
            name: Category name.
            code: Category code.
            parent_code: Optional parent category code.
            
        Returns:
            Created category object.
            
        Raises:
            ValueError: If category code already exists.
        """
        if self.get_category_by_code(code):
            raise ValueError(f"Category with code {code} already exists")
            
        category = Category(name=name, code=code)
        
        if parent_code:
            parent = self.get_category_by_code(parent_code)
            if not parent:
                raise ValueError(f"Parent category with code {parent_code} not found")
            category.parent_id = parent.id
            
        db.session.add(category)
        db.session.commit()
        return category
    
    def assign_asin_category(self, asin: str, category_code: str, title: Optional[str] = None) -> ASINCategory:
        """Assign category to an ASIN.
        
        Args:
            asin: Amazon Standard Identification Number.
            category_code: Category code to assign.
            title: Optional product title.
            
        Returns:
            Created ASIN-Category mapping.
            
        Raises:
            ValueError: If category not found or ASIN already mapped.
        """
        category = self.get_category_by_code(category_code)
        if not category:
            raise ValueError(f"Category with code {category_code} not found")
            
        existing = ASINCategory.query.filter_by(asin=asin).first()
        if existing:
            raise ValueError(f"ASIN {asin} already mapped to category {existing.category.code}")
            
        mapping = ASINCategory(
            asin=asin,
            category_id=category.id,
            title=title
        )
        
        db.session.add(mapping)
        db.session.commit()
        return mapping
    
    def get_asin_category(self, asin: str) -> Optional[Dict[str, Any]]:
        """Get category information for an ASIN.
        
        Args:
            asin: Amazon Standard Identification Number.
            
        Returns:
            Dictionary with ASIN category information if found, None otherwise.
        """
        mapping = ASINCategory.query.filter_by(asin=asin).first()
        return mapping.to_dict() if mapping else None
    
    def bulk_assign_categories(self, mappings: List[Dict[str, str]]) -> List[ASINCategory]:
        """Bulk assign categories to ASINs.
        
        Args:
            mappings: List of dictionaries with keys: asin, category_code, title (optional)
            
        Returns:
            List of created ASIN-Category mappings.
            
        Raises:
            ValueError: If any category not found or ASIN already mapped.
        """
        results = []
        for mapping in mappings:
            try:
                result = self.assign_asin_category(
                    asin=mapping['asin'],
                    category_code=mapping['category_code'],
                    title=mapping.get('title')
                )
                results.append(result)
            except ValueError as e:
                db.session.rollback()
                raise ValueError(f"Error processing ASIN {mapping['asin']}: {str(e)}")
                
        return results
