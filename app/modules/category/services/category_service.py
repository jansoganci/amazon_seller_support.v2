"""Category service layer for Amazon Seller Support."""

from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.modules.category.models.category import Category, ASINCategory

class CategoryService:
    """Service class for category operations."""
    
    DEFAULT_CATEGORY = "#N/A"
    
    @staticmethod
    def get_category_by_code(code: str) -> Optional[Category]:
        """Get category by its code.
        
        Args:
            code: Category code (e.g., 'electronics', 'books')
            
        Returns:
            Category object if found, None otherwise
        """
        return Category.query.filter_by(code=code).first()
    
    @staticmethod
    def get_category_tree() -> List[Dict[str, Any]]:
        """Get complete category tree.
        
        Returns:
            List of top-level categories with their subcategories
        """
        root_categories = Category.query.filter_by(parent_id=None).all()
        return [cat.to_dict() for cat in root_categories]
    
    @staticmethod
    def get_category_info(category_id: Optional[int] = None) -> Tuple[str, str]:
        """Get category name and code.
        
        Args:
            category_id: Category ID, if None returns default category
            
        Returns:
            Tuple of (category_name, category_code)
        """
        if category_id is None:
            return (CategoryService.DEFAULT_CATEGORY, CategoryService.DEFAULT_CATEGORY)
            
        category = Category.query.get(category_id)
        if not category:
            return (CategoryService.DEFAULT_CATEGORY, CategoryService.DEFAULT_CATEGORY)
            
        return (category.name, category.code)
    
    @staticmethod
    def get_asin_categories(asin: str) -> List[Dict[str, Any]]:
        """Get all categories for an ASIN.
        
        Args:
            asin: Amazon Standard Identification Number
            
        Returns:
            List of category information including parent categories
        """
        mappings = ASINCategory.query.filter_by(asin=asin).all()
        if not mappings:
            return []
            
        result = []
        for mapping in mappings:
            category = mapping.category
            result.append({
                'category': category.name,
                'category_code': category.code,
                'parent_category': category.parent.name if category.parent else CategoryService.DEFAULT_CATEGORY,
                'parent_code': category.parent.code if category.parent else CategoryService.DEFAULT_CATEGORY,
                'title': mapping.title
            })
        return result
    
    @staticmethod
    def create_category(
        name: str,
        code: str,
        description: Optional[str] = None,
        parent_code: Optional[str] = None
    ) -> Category:
        """Create a new category.
        
        Args:
            name: Category name
            code: Category code
            description: Optional category description
            parent_code: Optional parent category code
            
        Returns:
            Created category object
            
        Raises:
            ValueError: If category code already exists or parent not found
        """
        if CategoryService.get_category_by_code(code):
            raise ValueError(f"Category with code {code} already exists")
            
        category = Category(
            name=name,
            code=code,
            description=description
        )
        
        if parent_code:
            parent = CategoryService.get_category_by_code(parent_code)
            if not parent:
                raise ValueError(f"Parent category with code {parent_code} not found")
            category.parent_id = parent.id
            
        db.session.add(category)
        db.session.commit()
        return category
    
    @staticmethod
    def assign_asin_category(
        asin: str,
        category_code: str,
        title: str,
        description: Optional[str] = None
    ) -> ASINCategory:
        """Assign category to an ASIN.
        
        Args:
            asin: Amazon Standard Identification Number
            category_code: Category code to assign
            title: Product title
            description: Optional product description
            
        Returns:
            Created ASIN-Category mapping
            
        Raises:
            ValueError: If category not found
        """
        category = CategoryService.get_category_by_code(category_code)
        if not category:
            raise ValueError(f"Category with code {category_code} not found")
            
        # Check if mapping already exists
        existing = ASINCategory.query.filter_by(
            asin=asin,
            category_id=category.id
        ).first()
        
        if existing:
            # Update existing mapping
            existing.title = title
            existing.description = description
            db.session.commit()
            return existing
            
        # Create new mapping
        mapping = ASINCategory(
            asin=asin,
            category_id=category.id,
            title=title,
            description=description
        )
        
        db.session.add(mapping)
        db.session.commit()
        return mapping
    
    @staticmethod
    def bulk_assign_categories(mappings: List[Dict[str, Any]]) -> List[ASINCategory]:
        """Bulk assign categories to ASINs.
        
        Args:
            mappings: List of dictionaries with keys:
                - asin: Amazon Standard Identification Number
                - category_code: Category code
                - title: Product title
                - description: Optional product description
                
        Returns:
            List of created/updated ASIN-Category mappings
            
        Note:
            If any mapping fails, the entire operation is rolled back
        """
        results = []
        try:
            for mapping in mappings:
                result = CategoryService.assign_asin_category(
                    asin=mapping['asin'],
                    category_code=mapping['category_code'],
                    title=mapping['title'],
                    description=mapping.get('description')
                )
                results.append(result)
            return results
        except Exception as e:
            db.session.rollback()
            raise ValueError(f"Error in bulk assignment: {str(e)}")
            
    @staticmethod
    def get_uncategorized_asins() -> List[str]:
        """Get list of ASINs without any category assignment.
        
        Returns:
            List of ASINs that need categorization
        """
        # This query needs to be customized based on how you store ASINs
        # For now, we'll return an empty list
        return []  # TODO: Implement based on ASIN storage strategy
