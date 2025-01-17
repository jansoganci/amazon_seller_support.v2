"""Test verisi oluşturma scripti."""
from datetime import datetime, timedelta
import random
from app import create_app, db
from app.models.reports import BusinessReport
from app.utils.constants import ASIN_CATEGORIES

def create_business_reports():
    """30 ASIN için son 30 günlük test verisi oluştur."""
    app = create_app()
    with app.app_context():
        # Son 30 gün için veri oluştur
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        # Her ASIN için
        for asin in ASIN_CATEGORIES.keys():
            current_date = start_date
            while current_date <= end_date:
                # Rastgele veriler oluştur
                sessions = random.randint(100, 1000)
                units_ordered = int(sessions * random.uniform(0.05, 0.15))  # %5-15 dönüşüm
                price = random.uniform(20, 200)
                ordered_product_sales = units_ordered * price
                
                report = BusinessReport(
                    store_id=1,
                    date=current_date,
                    sku=f"SKU-{asin}",
                    asin=asin,
                    title=f"Test Product {asin}",
                    sessions=sessions,
                    units_ordered=units_ordered,
                    ordered_product_sales=ordered_product_sales,
                    total_order_items=units_ordered,
                    conversion_rate=units_ordered/sessions if sessions > 0 else 0
                )
                
                db.session.add(report)
                current_date += timedelta(days=1)
        
        # Değişiklikleri kaydet
        db.session.commit()
        print("Test verileri başarıyla oluşturuldu!")

if __name__ == "__main__":
    create_business_reports() 