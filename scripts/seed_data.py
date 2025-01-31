from datetime import datetime, timedelta
import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.modules.auth.models import User
from app.modules.business.models import Store, Category, BusinessReport
from app.extensions import db

def seed_data():
    app = create_app()
    
    with app.app_context():
        # Create test user
        test_user = User(
            email="test@example.com",
            username="test_user",
            password="test123"  # In production, use proper password hashing
        )
        db.session.add(test_user)
        db.session.flush()

        # Create test store
        test_store = Store(
            name="Test Amazon Store",
            marketplace="amazon.com",
            user_id=test_user.id
        )
        db.session.add(test_store)
        db.session.flush()

        # Create test categories
        categories = [
            Category(name="Electronics", code="ELECT", description="Electronic items"),
            Category(name="Books", code="BOOKS", description="Books and literature"),
            Category(name="Home", code="HOME", description="Home and kitchen items")
        ]
        for category in categories:
            db.session.add(category)
        db.session.flush()

        # Create sample business reports
        start_date = datetime.now() - timedelta(days=30)
        for i in range(30):
            report_date = start_date + timedelta(days=i)
            report = BusinessReport(
                store_id=test_store.id,
                date=report_date,
                sku=f"SKU-{i+1}",
                asin=f"B00{i:05d}",
                title=f"Test Product {i+1}",
                sessions=100 + i,
                units_ordered=10 + i,
                ordered_product_sales=99.99 + i,
                total_order_items=10 + i,
                conversion_rate=0.1 + (i/100)
            )
            db.session.add(report)

        # Commit all changes
        db.session.commit()
        print("Sample data has been successfully loaded!")

if __name__ == "__main__":
    seed_data()
