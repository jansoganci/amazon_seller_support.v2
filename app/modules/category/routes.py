"""Category routes for Amazon Seller Support."""

from typing import Dict, Any
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required
from werkzeug.exceptions import BadRequest, Unauthorized, Forbidden
from app.modules.category.services.category_service import CategoryService
from app.decorators import admin_required
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
@admin_required
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
@login_required
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

@bp.route('/asin/<string:asin>', methods=['GET'])
@login_required
@admin_required
def get_asin_categories(asin: str):
    """Get categories for an ASIN.
    
    Args:
        asin (str): Amazon Standard Identification Number
        
    Returns:
        JSON response with categories for the ASIN.
    """
    try:
        service = CategoryService()
        categories = service.get_asin_categories(asin)
        return jsonify({"data": [c.to_dict() for c in categories]})
    except Exception as e:
        current_app.logger.error(f"Error getting ASIN categories: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/asin', methods=['POST'])
@login_required
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
            return jsonify({"error": "Missing request body"}), 400
        
        required_fields = ['asin', 'category_code', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"{field} is required"}), 400
        
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
@login_required
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
        if not data or 'mappings' not in data:
            return jsonify({"error": "Missing mappings in request body"}), 400
        
        if not isinstance(data['mappings'], list):
            return jsonify({"error": "Mappings must be a list"}), 400
        
        service = CategoryService()
        mappings = service.bulk_assign_categories(data['mappings'])
        return jsonify({"data": [m.to_dict() for m in mappings]}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error bulk assigning categories: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/asin/uncategorized', methods=['GET'])
@login_required
@admin_required
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
        asins = service.get_uncategorized_asins()
        paginated = paginate_results(asins, page, per_page)
        
        return jsonify({"data": paginated})
    except Exception as e:
        current_app.logger.error(f"Error getting uncategorized ASINs: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500
