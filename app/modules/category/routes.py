"""Category routes for Amazon Seller Support."""

from typing import Dict, Any
from flask import Blueprint, jsonify, request
from app.modules.category.services.category_service import CategoryService
from app.decorators import login_required

bp = Blueprint('category', __name__, url_prefix='/api/categories')

@bp.route('/', methods=['GET'])
@login_required
def get_categories():
    """Get category tree.
    
    Returns:
        JSON response with category tree.
    """
    try:
        service = CategoryService()
        categories = service.get_category_tree()
        return jsonify(categories)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@login_required
def create_category():
    """Create a new category.
    
    Request body:
        name: Category name
        code: Category code
        parent_code: Optional parent category code
        
    Returns:
        JSON response with created category.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'code']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        service = CategoryService()
        category = service.create_category(
            name=data['name'],
            code=data['code'],
            parent_code=data.get('parent_code')
        )
        return jsonify(category.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/asin/<asin>', methods=['GET'])
@login_required
def get_asin_category(asin: str):
    """Get category for an ASIN.
    
    Args:
        asin: Amazon Standard Identification Number
        
    Returns:
        JSON response with ASIN category information.
    """
    try:
        service = CategoryService()
        result = service.get_asin_category(asin)
        if not result:
            return jsonify({'error': 'ASIN not found'}), 404
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/asin', methods=['POST'])
@login_required
def assign_asin_category():
    """Assign category to an ASIN.
    
    Request body:
        asin: Amazon Standard Identification Number
        category_code: Category code to assign
        title: Optional product title
        
    Returns:
        JSON response with created mapping.
    """
    try:
        data = request.get_json()
        if not data or not all(k in data for k in ['asin', 'category_code']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        service = CategoryService()
        mapping = service.assign_asin_category(
            asin=data['asin'],
            category_code=data['category_code'],
            title=data.get('title')
        )
        return jsonify(mapping.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/asin/bulk', methods=['POST'])
@login_required
def bulk_assign_categories():
    """Bulk assign categories to ASINs.
    
    Request body:
        mappings: List of dictionaries with keys:
            - asin: Amazon Standard Identification Number
            - category_code: Category code to assign
            - title: Optional product title
            
    Returns:
        JSON response with created mappings.
    """
    try:
        data = request.get_json()
        if not data or 'mappings' not in data:
            return jsonify({'error': 'Missing mappings data'}), 400
            
        service = CategoryService()
        mappings = service.bulk_assign_categories(data['mappings'])
        return jsonify([m.to_dict() for m in mappings]), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500
