"""Script to load sample business report data."""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.store import Store
from app.modules.business.models import BusinessReport
from app.extensions import db

# Sample categories and subcategories
CATEGORIES = {
    1: {
        'name': 'Electronics',
        'subcategories': {
            10: 'Smartphones',
            11: 'Laptops',
            12: 'Accessories'
        }
    },
    2: {
        'name': 'Home & Kitchen',
        'subcategories': {
            20: 'Appliances',
            21: 'Furniture',
            22: 'Decor'
        }
    },
    3: {
        'name': 'Sports',
        'subcategories': {
            30: 'Fitness',
            31: 'Outdoor',
            32: 'Equipment'
        }
    }
}

# Sample ASINs
ASINS = {
    # Electronics
    'B01EXAMPLE1': {'title': 'Premium Smartphone X', 'category_id': 1, 'subcategory_id': 10},
    'B01EXAMPLE2': {'title': 'Laptop Pro 15"', 'category_id': 1, 'subcategory_id': 11},
    'B01EXAMPLE3': {'title': 'Wireless Earbuds', 'category_id': 1, 'subcategory_id': 12},
    
    # Home & Kitchen
    'B02EXAMPLE1': {'title': 'Smart Coffee Maker', 'category_id': 2, 'subcategory_id': 20},
    'B02EXAMPLE2': {'title': 'Modern Sofa Set', 'category_id': 2, 'subcategory_id': 21},
    'B02EXAMPLE3': {'title': 'Wall Art Collection', 'category_id': 2, 'subcategory_id': 22},
    
    # Sports
    'B03EXAMPLE1': {'title': 'Smart Fitness Watch', 'category_id': 3, 'subcategory_id': 30},
    'B03EXAMPLE2': {'title': 'Camping Tent', 'category_id': 3, 'subcategory_id': 31},
    'B03EXAMPLE3': {'title': 'Exercise Bike', 'category_id': 3, 'subcategory_id': 32}
}

def generate_sample_data(store_id: int, days: int = 90):
    """Generate sample business report data.
    
    Args:
        store_id: Store ID to generate data for
        days: Number of days of data to generate
    
    Returns:
        List of BusinessReport objects
    """
    reports = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    current_date = start_date
    while current_date <= end_date:
        for asin, info in ASINS.items():
            # Base metrics
            base_sessions = np.random.randint(100, 1000)
            conversion_rate = np.random.uniform(1.5, 4.5)
            units_per_order = np.random.uniform(1.0, 3.0)
            price_range = {
                1: (500, 1500),  # Electronics
                2: (50, 300),    # Home & Kitchen
                3: (100, 500)    # Sports
            }
            
            # Calculate metrics
            min_price, max_price = price_range[info['category_id']]
            avg_price = np.random.uniform(min_price, max_price)
            units_ordered = int(base_sessions * (conversion_rate / 100) * units_per_order)
            total_orders = int(units_ordered / units_per_order)
            revenue = units_ordered * avg_price
            
            # Create report
            report = BusinessReport(
                store_id=store_id,
                date=current_date,
                asin=asin,
                title=info['title'],
                category_id=info['category_id'],
                category=CATEGORIES[info['category_id']]['name'],
                subcategory_id=info['subcategory_id'],
                subcategory=CATEGORIES[info['category_id']]['subcategories'][info['subcategory_id']],
                sessions=base_sessions,
                units_ordered=units_ordered,
                total_order_items=total_orders,
                ordered_product_sales=revenue,
                conversion_rate=conversion_rate
            )
            reports.append(report)
        
        current_date += timedelta(days=1)
    
    return reports

def main():
    """Main function to load sample data."""
    # Create app context
    app = create_app()
    with app.app_context():
        try:
            # Create store if it doesn't exist
            store = Store.query.filter_by(id=1).first()
            if not store:
                store = Store(id=1, name="Sample Store")
                db.session.add(store)
                db.session.commit()
            
            # Generate and save sample data
            print("Generating sample data...")
            reports = generate_sample_data(store.id)
            
            print(f"Saving {len(reports)} reports...")
            db.session.bulk_save_objects(reports)
            db.session.commit()
            
            print("Sample data loaded successfully!")
            
        except Exception as e:
            print(f"Error loading sample data: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    main()
