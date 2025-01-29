"""Category routes for Amazon Seller Support."""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest
from app.modules.category.services.category_service import CategoryService
from app.utils.decorators import login_required, admin_required
from app.utils.pagination import paginate_query
from app.utils.validation import validate_request_data

bp = Blueprint('category', __name__, url_prefix='/api/v1/categories')

def paginate_results(query, page=1, per_page=50):
    """Simple pagination helper."""
    page = int(page)
    per_page = int(per_page)
    paginated = query.paginate(page=page, per_page=per_page)
    return {
        'items': paginated.items,
        'page': page,
        'per_page': per_page,
        'total': paginated.total,
        'pages': paginated.pages
    }

@bp.route('/', methods=['GET'])
@login_required
def get_categories():
    """Get category tree.
    
    Returns:
        JSON response with category tree.
        
    Example response:
        {
            "data": [
                {
                    "id": 1,
                    "name": "Electronics",
                    "code": "electronics",
                    "children": [
                        {
                            "id": 2,
                            "name": "Smartphones",
                            "code": "smartphones"
                        }
                    ]
                }
            ]
        }
    """
    try:
        service = CategoryService()
        categories = service.get_category_tree()
        return jsonify({"data": categories})
    except Exception as e:
        current_app.logger.error(f"Error getting categories: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/', methods=['POST'])
@admin_required
def create_category():
    """Create a new category.
    
    Request body:
        {
            "name": "Electronics",
            "code": "electronics",
            "description": "Electronic devices and accessories",
            "parent_code": "optional_parent_code"
        }
        
    Returns:
        JSON response with created category.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        
        if 'name' not in data or 'code' not in data:
            return jsonify({"error": "Name and code are required"}), 400
        
        service = CategoryService()
        category = service.create_category(
            name=data['name'],
            code=data['code'],
            description=data.get('description'),
            parent_code=data.get('parent_code')
        )
        return jsonify({"data": category.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating category: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/asin/<asin>', methods=['GET'])
@login_required
def get_asin_categories(asin: str):
    """Get categories for an ASIN.
    
    Args:
        asin: Amazon Standard Identification Number
        
    Returns:
        JSON response with ASIN category information.
        
    Example response:
        {
            "data": [
                {
                    "category": "Electronics",
                    "category_code": "electronics",
                    "parent_category": "All",
                    "parent_code": "#N/A",
                    "title": "iPhone 13"
                }
            ]
        }
    """
    try:
        service = CategoryService()
        categories = service.get_asin_categories(asin)
        if not categories:
            return jsonify({"error": f"No categories found for ASIN {asin}"}), 404
        return jsonify({"data": categories})
    except Exception as e:
        current_app.logger.error(f"Error getting ASIN categories: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/asin', methods=['POST'])
@admin_required
def assign_asin_category():
    """Assign category to an ASIN.
    
    Request body:
        {
            "asin": "B01EXAMPLE",
            "category_code": "electronics",
            "title": "Product Title",
            "description": "Optional product description"
        }
        
    Returns:
        JSON response with created mapping.
    """
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Missing request body")
        
        if 'asin' not in data or 'category_code' not in data or 'title' not in data:
            raise BadRequest("ASIN, category code, and title are required")
        
        service = CategoryService()
        mapping = service.assign_asin_category(
            asin=data['asin'],
            category_code=data['category_code'],
            title=data['title'],
            description=data.get('description')
        )
        return jsonify({"data": mapping.to_dict()}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error assigning ASIN category: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/asin/bulk', methods=['POST'])
@admin_required
def bulk_assign_categories():
    """Bulk assign categories to ASINs.
    
    Request body:
        {
            "mappings": [
                {
                    "asin": "B01EXAMPLE1",
                    "category_code": "electronics",
                    "title": "Product 1",
                    "description": "Optional description"
                },
                {
                    "asin": "B01EXAMPLE2",
                    "category_code": "books",
                    "title": "Product 2"
                }
            ]
        }
        
    Returns:
        JSON response with created mappings.
    """
    try:
        data = request.get_json()
        if not data:
            raise BadRequest("Missing request body")
        
        if 'mappings' not in data:
            raise BadRequest("Mappings are required")
        
        for mapping in data['mappings']:
            if 'asin' not in mapping or 'category_code' not in mapping or 'title' not in mapping:
                raise BadRequest("Each mapping must contain asin, category_code, and title")
        
        service = CategoryService()
        mappings = service.bulk_assign_categories(data['mappings'])
        return jsonify({"data": [m.to_dict() for m in mappings]}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error in bulk assignment: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/uncategorized', methods=['GET'])
@login_required
def get_uncategorized_asins():
    """Get ASINs without category assignments.
    
    Query parameters:
        page: Page number (default: 1)
        per_page: Items per page (default: 50)
        
    Returns:
        JSON response with uncategorized ASINs.
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        
        service = CategoryService()
        query = service.get_uncategorized_asins()
        
        result = paginate_results(query, page, per_page)
        return jsonify({'data': result}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error getting uncategorized ASINs: {str(e)}")
        return jsonify({'error': str(e)}), 500
