from datetime import datetime, timedelta
from db import get_db

def revenue_trends(store_id, start_date=None, end_date=None, category=None, asin=None):
    try:
        query = """
            WITH RECURSIVE dates(date) AS (
                SELECT DATE(:start_date)
                UNION ALL
                SELECT DATE(date, '+1 day')
                FROM dates
                WHERE date < DATE(:end_date)
            ),
            daily_revenue AS (
                SELECT 
                    DATE(date) as sale_date,
                    SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue
                FROM business_report
                WHERE store_id = :store_id
                    AND DATE(date) BETWEEN DATE(:start_date) AND DATE(:end_date)
                    AND (:category IS NULL OR category = :category)
                    AND (:asin IS NULL OR asin = :asin)
                GROUP BY DATE(date)
            )
            SELECT 
                dates.date as date,
                COALESCE(daily_revenue.revenue, 0) as revenue
            FROM dates
            LEFT JOIN daily_revenue ON dates.date = daily_revenue.sale_date
            ORDER BY dates.date;
        """
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        params = {
            'store_id': store_id,
            'start_date': start_date,
            'end_date': end_date,
            'category': category,
            'asin': asin
        }
        
        with get_db() as db:
            results = db.execute(query, params).fetchall()
            
        return {
            'dates': [row[0] for row in results],
            'revenue': [float(row[1]) for row in results]
        }
        
    except Exception as e:
        print(f"Error in revenue_trends: {str(e)}")
        return {'error': str(e)} 