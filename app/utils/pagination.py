"""Pagination utilities."""

from typing import Dict, Any
from sqlalchemy.orm import Query

def paginate_query(query: Query, page: int = 1, per_page: int = 50) -> Dict[str, Any]:
    """Paginate a SQLAlchemy query.
    
    Args:
        query: SQLAlchemy query to paginate
        page: Page number (default: 1)
        per_page: Items per page (default: 50)
        
    Returns:
        Dict with pagination info and items
    """
    page = int(page)
    per_page = int(per_page)
    
    # Calculate offset and limit
    offset = (page - 1) * per_page
    
    # Get total count
    total = query.count()
    
    # Get paginated items
    items = query.offset(offset).limit(per_page).all()
    
    # Calculate total pages
    pages = (total + per_page - 1) // per_page
    
    return {
        'items': items,
        'page': page,
        'per_page': per_page,
        'total': total,
        'pages': pages
    }
