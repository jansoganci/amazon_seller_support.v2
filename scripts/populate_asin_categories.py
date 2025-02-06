import csv
import sqlite3
from datetime import datetime

def populate_asin_categories():
    # Connect to the database
    conn = sqlite3.connect('instance/amazon_seller.db')
    cursor = conn.cursor()
    
    # Read the CSV file
    with open('data/product_categories.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        
        for row in csv_reader:
            # Get the subcategory ID
            cursor.execute("""
                SELECT c1.id 
                FROM categories c1
                JOIN categories c2 ON c1.parent_id = c2.id
                WHERE c1.name = ? AND c2.name = ?
            """, (row['subcategory'], row['main_category']))
            
            result = cursor.fetchone()
            if result:
                category_id = result[0]
                
                # Insert into asin_categories
                cursor.execute("""
                    INSERT INTO asin_categories (asin, category_id, title, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    row['asin'],
                    category_id,
                    row['title'],
                    datetime.now(),
                    datetime.now()
                ))
    
    # Commit the changes
    conn.commit()
    conn.close()

if __name__ == '__main__':
    populate_asin_categories()
