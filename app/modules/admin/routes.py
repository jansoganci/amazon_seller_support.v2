"""Admin routes for Amazon Seller Support."""

from typing import Dict, Any
from flask import Blueprint, render_template, jsonify, request
from app.decorators import admin_required
from app.models import User
from app.modules.category.services.category_service import CategoryService

bp = Blueprint('admin', __name__, 
               url_prefix='/admin',
               template_folder='templates')

@bp.route('/categories', methods=['GET'])
@admin_required
def category_management():
    """Admin category management page."""
    return render_template('category-management.html')

@bp.route('/users', methods=['GET'])
@admin_required
def user_management():
    """Admin user management page."""
    users = User.query.all()
    return render_template('user-management.html', users=users)

@bp.route('/categories/bulk-update', methods=['POST'])
@admin_required
def bulk_update_categories():
    """Bulk update categories and their ASINs."""
    data = request.get_json()
    categories = data.get('categories', [])
    
    try:
        mappings = []
        for item in categories:
            # Ana kategoriyi oluştur
            main_category_code = item['category'].lower().replace(' ', '_')
            try:
                main_category = CategoryService.get_category_by_code(main_category_code)
                if not main_category:
                    main_category = CategoryService.create_category(
                        name=item['category'],
                        code=main_category_code
                    )
            except ValueError as e:
                return jsonify({'error': f"Error creating main category: {str(e)}"}), 400
            
            # Alt kategoriyi oluştur
            sub_category_code = item['subcategory'].lower().replace(' ', '_')
            try:
                sub_category = CategoryService.get_category_by_code(sub_category_code)
                if not sub_category:
                    sub_category = CategoryService.create_category(
                        name=item['subcategory'],
                        code=sub_category_code,
                        parent_code=main_category_code
                    )
            except ValueError as e:
                return jsonify({'error': f"Error creating subcategory: {str(e)}"}), 400
            
            # ASIN-Kategori eşleşmesi için mapping hazırla
            mappings.append({
                'asin': item['asin'],
                'category_code': sub_category_code,
                'title': f"Product {item['asin']}"  # Gerçek başlık daha sonra güncellenebilir
            })
        
        # Bulk assignment yap
        try:
            CategoryService.bulk_assign_categories(mappings)
            return jsonify({'message': 'Categories updated successfully'}), 200
        except ValueError as e:
            return jsonify({'error': f"Error assigning categories: {str(e)}"}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
