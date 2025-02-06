import sqlite3
import csv
from datetime import datetime, timedelta
import random

def get_realistic_metrics(category_name):
    """Generate realistic metrics based on category"""
    metrics = {
        'Electronics': {
            'sessions': (100, 500),
            'conversion_rate': (2, 8),
            'price_range': (50, 500)
        },
        'Home & Kitchen': {
            'sessions': (80, 300),
            'conversion_rate': (3, 10),
            'price_range': (20, 200)
        },
        'Clothing': {
            'sessions': (150, 400),
            'conversion_rate': (4, 12),
            'price_range': (15, 80)
        },
        'Sports & Outdoors': {
            'sessions': (50, 200),
            'conversion_rate': (2, 7),
            'price_range': (20, 150)
        },
        'Beauty & Personal Care': {
            'sessions': (200, 600),
            'conversion_rate': (5, 15),
            'price_range': (10, 100)
        },
        'Office Products': {
            'sessions': (30, 150),
            'conversion_rate': (3, 8),
            'price_range': (5, 50)
        },
        'Toys & Games': {
            'sessions': (100, 400),
            'conversion_rate': (4, 10),
            'price_range': (15, 100)
        },
        'Video Games': {
            'sessions': (200, 800),
            'conversion_rate': (3, 8),
            'price_range': (40, 400)
        },
        'Health & Household': {
            'sessions': (150, 500),
            'conversion_rate': (4, 12),
            'price_range': (10, 80)
        },
        'Pet Supplies': {
            'sessions': (80, 300),
            'conversion_rate': (3, 9),
            'price_range': (15, 120)
        },
        'Tools & Home Improvement': {
            'sessions': (40, 200),
            'conversion_rate': (2, 7),
            'price_range': (10, 150)
        }
    }
    
    return metrics.get(category_name, {
        'sessions': (50, 300),
        'conversion_rate': (2, 8),
        'price_range': (10, 100)
    })

def generate_daily_data(conn, asin, title, category_name, date):
    """Generate realistic daily data for a product"""
    metrics = get_realistic_metrics(category_name)
    
    # Generate realistic numbers
    sessions = random.randint(*metrics['sessions'])
    conversion_rate = random.uniform(*metrics['conversion_rate'])
    avg_price = random.uniform(*metrics['price_range'])
    
    # Calculate derived metrics
    units_ordered = int((sessions * conversion_rate) / 100)
    ordered_product_sales = round(units_ordered * avg_price, 2)
    
    return {
        'store_id': 1,  # Using the existing store
        'date': date,
        'sku': f"SKU-{asin}",
        'asin': asin,
        'title': title,
        'sessions': sessions,
        'units_ordered': units_ordered,
        'ordered_product_sales': ordered_product_sales,
        'total_order_items': units_ordered,  # Simplified: 1 item per order
        'conversion_rate': round(conversion_rate, 2)
    }

def update_business_reports():
    conn = sqlite3.connect('instance/amazon_seller.db')
    cursor = conn.cursor()
    
    # Clear existing recent data (keep historical data)
    cursor.execute("""
        DELETE FROM business_reports 
        WHERE date >= date('now', '-30 days')
    """)
    
    # Get our products with their categories
    cursor.execute("""
        SELECT ac.asin, ac.title, c2.name as main_category
        FROM asin_categories ac
        JOIN categories c1 ON ac.category_id = c1.id
        JOIN categories c2 ON c1.parent_id = c2.id
    """)
    products = cursor.fetchall()
    
    # Generate 30 days of data
    for days_ago in range(30, 0, -1):
        date = datetime.now() - timedelta(days=days_ago)
        
        for asin, title, category in products:
            data = generate_daily_data(conn, asin, title, category, date)
            
            cursor.execute("""
                INSERT INTO business_reports (
                    store_id, date, sku, asin, title, 
                    sessions, units_ordered, ordered_product_sales,
                    total_order_items, conversion_rate, created_at, updated_at
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
                )
            """, (
                data['store_id'], data['date'], data['sku'],
                data['asin'], data['title'], data['sessions'],
                data['units_ordered'], data['ordered_product_sales'],
                data['total_order_items'], data['conversion_rate']
            ))
    
    conn.commit()
    
    # Print summary
    cursor.execute("SELECT COUNT(*) FROM business_reports")
    total_records = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT COUNT(*) FROM business_reports 
        WHERE date >= date('now', '-30 days')
    """)
    new_records = cursor.fetchone()[0]
    
    print(f"Total records in business_reports: {total_records}")
    print(f"New records added: {new_records}")
    
    conn.close()

if __name__ == '__main__':
    update_business_reports()
