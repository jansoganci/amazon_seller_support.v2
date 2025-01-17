from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, render_template
from flask_login import login_required, current_user
from app.utils.analytics_engine import AnalyticsEngine, TimeGrouping
from app.models import Store, BusinessReport
from app.utils.constants import get_category_by_asin
from sqlalchemy import text
from app import db
import pandas as pd
from flask_cors import CORS
import sqlite3
import os
import json
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import redis

bp = Blueprint('analytics', __name__, url_prefix='/api/analytics')
analytics_engine = AnalyticsEngine()

# Redis bağlantısı (Caching için)
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Rate Limiting için Flask-Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@bp.route('/revenue-trends')
@login_required
def revenue_trends():
    """Revenue trends page."""
    analytics = AnalyticsEngine()
    store_id = 1  # TODO: Get from current user's store
    
    try:
        categories = analytics.get_available_categories(store_id)
        asins = analytics.get_available_asins(store_id)
        return render_template(
            'analytics/revenue_trends.html',
            store_id=store_id,
            categories=categories,
            asins=asins
        )
    except Exception as e:
        print(f"Error in revenue_trends: {str(e)}")
        return render_template(
            'analytics/revenue_trends.html',
            error=str(e)
        )

@bp.route('/api/revenue/trends')
@login_required
def get_revenue_trends():
    """Revenue trends API endpoint."""
    try:
        store_id = request.args.get('store_id', type=int)
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        group_by = request.args.get('group_by', 'daily')
        category = request.args.get('category')
        asin = request.args.get('asin')

        # Log incoming request parameters for debugging
        print(f"Revenue trends request - Parameters:")
        print(f"store_id: {store_id}")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")
        print(f"group_by: {group_by}")
        print(f"category: {category}")
        print(f"asin: {asin}")

        # Set default date range if not provided (last 30 days)
        if not start_date or not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        # Validate required parameters
        if not store_id:
            return jsonify({'error': 'Store ID is required'}), 400

        try:
            # Parse and validate dates
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')
            
            # Add time components for proper range (start of day to end of day)
            start_date = start_datetime.strftime('%Y-%m-%d 00:00:00')
            end_date = end_datetime.strftime('%Y-%m-%d 23:59:59')
            
            print(f"Parsed dates - start: {start_date}, end: {end_date}")

        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400

        # Base query for revenue trends based on group_by
        if group_by == 'daily':
            date_format = "DATE(date)"
            base_select = f"""
                WITH RECURSIVE dates(date) AS (
                    SELECT date(?)
                    UNION ALL
                    SELECT date(date, '+1 day')
                    FROM dates
                    WHERE date < date(?)
                )
                SELECT 
                    dates.date as date_group,
                    COALESCE(SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)), 0) as revenue,
                    COALESCE(SUM(units_ordered), 0) as units,
                    COALESCE(SUM(sessions), 0) as sessions,
                    CASE 
                        WHEN COALESCE(SUM(sessions), 0) = 0 THEN 0 
                        ELSE CAST(COALESCE(SUM(units_ordered), 0) AS FLOAT) / COALESCE(SUM(sessions), 0) * 100 
                    END as conversion_rate
                FROM dates
                LEFT JOIN business_report ON 
                    DATE(business_report.date) = dates.date
                    AND business_report.store_id = ?
            """
        elif group_by == 'weekly':
            date_format = "strftime('%Y-W%W', date)"
            base_select = f"""
                SELECT 
                    {date_format} as date_group,
                    SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                    SUM(units_ordered) as units,
                    SUM(sessions) as sessions,
                    CASE 
                        WHEN SUM(sessions) = 0 THEN 0 
                        ELSE CAST(SUM(units_ordered) AS FLOAT) / SUM(sessions) * 100 
                    END as conversion_rate
                FROM business_report
                WHERE date BETWEEN ? AND ?
                AND store_id = ?
            """
        elif group_by == 'monthly':
            date_format = "strftime('%Y-%m', date)"
            base_select = f"""
                SELECT 
                    {date_format} as date_group,
                    SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                    SUM(units_ordered) as units,
                    SUM(sessions) as sessions,
                    CASE 
                        WHEN SUM(sessions) = 0 THEN 0 
                        ELSE CAST(SUM(units_ordered) AS FLOAT) / SUM(sessions) * 100 
                    END as conversion_rate
                FROM business_report
                WHERE date BETWEEN ? AND ?
                AND store_id = ?
            """
        elif group_by == 'quarterly':
            date_format = "strftime('%Y', date) || '-Q' || ((CAST(strftime('%m', date) AS INTEGER) + 2) / 3)"
            base_select = f"""
                SELECT 
                    {date_format} as date_group,
                    SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                    SUM(units_ordered) as units,
                    SUM(sessions) as sessions,
                    CASE 
                        WHEN SUM(sessions) = 0 THEN 0 
                        ELSE CAST(SUM(units_ordered) AS FLOAT) / SUM(sessions) * 100 
                    END as conversion_rate
                FROM business_report
                WHERE date BETWEEN ? AND ?
                AND store_id = ?
            """
        else:  # yearly
            date_format = "strftime('%Y', date)"
            base_select = f"""
                SELECT 
                    {date_format} as date_group,
                    SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue,
                    SUM(units_ordered) as units,
                    SUM(sessions) as sessions,
                    CASE 
                        WHEN SUM(sessions) = 0 THEN 0 
                        ELSE CAST(SUM(units_ordered) AS FLOAT) / SUM(sessions) * 100 
                    END as conversion_rate
                FROM business_report
                WHERE date BETWEEN ? AND ?
                AND store_id = ?
            """

        # Set base parameters based on group_by
        if group_by == 'daily':
            params = [start_date, end_date, store_id]
        else:
            params = [start_date, end_date, store_id]

        # Add category and ASIN filters
        if category and category != "All Categories":
            category_query = """
                SELECT DISTINCT asin 
                FROM business_report 
                WHERE store_id = ?
            """
            conn = sqlite3.connect('instance/app.db')
            df_asins = pd.read_sql(category_query, conn, params=(store_id,))
            category_asins = [
                asin for asin in df_asins['asin'] 
                if get_category_by_asin(asin)[0] == category
            ]
            conn.close()

            if not category_asins:
                return jsonify({
                    'labels': [],
                    'values': [],
                    'units': [],
                    'sessions': [],
                    'conversion_rates': [],
                    'total_revenue': 0,
                    'total_units': 0,
                    'total_sessions': 0,
                    'average_order_value': 0,
                    'growth_rate': 0,
                    'previous_period': 0
                })

            if asin and asin != "All ASINs":
                if asin in category_asins:
                    if group_by == 'daily':
                        base_select += " AND business_report.asin = ?"
                    else:
                        base_select += " AND asin = ?"
                    params.append(asin)
                else:
                    return jsonify({
                        'labels': [],
                        'values': [],
                        'units': [],
                        'sessions': [],
                        'conversion_rates': [],
                        'total_revenue': 0,
                        'total_units': 0,
                        'total_sessions': 0,
                        'average_order_value': 0,
                        'growth_rate': 0,
                        'previous_period': 0
                    })
            else:
                placeholders = ','.join(['?' for _ in category_asins])
                if group_by == 'daily':
                    base_select += f" AND business_report.asin IN ({placeholders})"
                else:
                    base_select += f" AND asin IN ({placeholders})"
                params.extend(category_asins)
        else:
            if asin and asin != "All ASINs":
                if group_by == 'daily':
                    base_select += " AND business_report.asin = ?"
                else:
                    base_select += " AND asin = ?"
                params.append(asin)

        # Add group by and order by
        base_select += """
            GROUP BY date_group
            ORDER BY date_group
        """

        # Get SQLite connection directly
        conn = sqlite3.connect('instance/app.db')

        # Debug: Print query and params
        print(f"Query: {base_select}")
        print(f"Params: {params}")

        # Execute query and convert to DataFrame
        df = pd.read_sql(base_select, conn, params=params)
        
        # Debug: Print raw results
        print(f"Raw query results:")
        print(df)
        
        # Close connection
        conn.close()

        if df.empty:
            return jsonify({
                'labels': [],
                'values': [],
                'units': [],
                'sessions': [],
                'conversion_rates': [],
                'total_revenue': 0,
                'total_units': 0,
                'total_sessions': 0,
                'average_order_value': 0,
                'growth_rate': 0,
                'previous_period': 0
            })

        # Calculate total metrics
        total_revenue = float(df['revenue'].sum())
        total_units = int(df['units'].sum())
        total_sessions = int(df['sessions'].sum())
        average_order_value = total_revenue / total_units if total_units > 0 else 0

        # Get previous period revenue for growth rate
        previous_start = start_datetime - timedelta(days=30)
        previous_end = end_datetime - timedelta(days=30)
        
        # Query for previous period
        if category:
            prev_query = """
                SELECT SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue
                FROM business_report 
                WHERE store_id = ?
                AND date BETWEEN ? AND ?
                AND asin IN ({})
            """.format(','.join(['?'] * len(category_asins)))
            prev_params = [store_id, 
                         previous_start.strftime('%Y-%m-%d 00:00:00'),
                         previous_end.strftime('%Y-%m-%d 23:59:59')] + category_asins
        else:
            prev_query = """
                SELECT SUM(CAST(REPLACE(REPLACE(ordered_product_sales, '$', ''), ',', '') AS FLOAT)) as revenue
                FROM business_report 
                WHERE store_id = ?
                AND date BETWEEN ? AND ?
                AND (? IS NULL OR asin = ?)
            """
            prev_params = (store_id, 
                         previous_start.strftime('%Y-%m-%d 00:00:00'),
                         previous_end.strftime('%Y-%m-%d 23:59:59'),
                         asin, asin)

        # Get previous period revenue
        conn = sqlite3.connect('instance/app.db')
        prev_df = pd.read_sql(prev_query, conn, params=prev_params)
        conn.close()
        
        previous_revenue = float(prev_df['revenue'].iloc[0]) if not prev_df.empty and prev_df['revenue'].iloc[0] else 0
        growth_rate = ((total_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0

        # Debug: Print final response
        response_data = {
            'labels': df['date_group'].tolist(),
            'values': df['revenue'].tolist(),
            'units': df['units'].tolist(),
            'sessions': df['sessions'].tolist(),
            'conversion_rates': df['conversion_rate'].tolist(),
            'total_revenue': total_revenue,
            'total_units': total_units,
            'total_sessions': total_sessions,
            'average_order_value': average_order_value,
            'growth_rate': growth_rate,
            'previous_period': previous_revenue
        }
        print("API Response:", response_data)

        return jsonify(response_data)
    except Exception as e:
        print(f"Error in get_revenue_trends API: {str(e)}")
        return jsonify({'error': str(e)}), 500

@bp.route('/business-reports')
@login_required
def list_business_reports():
    """Business report verilerini listele."""
    reports = BusinessReport.query.filter_by(store_id=1).order_by(BusinessReport.date.desc()).all()
    return render_template('analytics/business_reports.html', 
                         reports=reports,
                         get_category=get_category_by_asin)

@bp.route('/dashboard')
def dashboard():
    """Analytics dashboard page."""
    analytics = AnalyticsEngine()
    
    try:
        # Get total number of business reports
        total_reports_query = text("""
            SELECT COUNT(*) as count 
            FROM business_report 
            WHERE store_id = :store_id
        """)
        result = db.session.execute(total_reports_query, {'store_id': 1}).first()
        total_reports = result.count if result else 0
        
        # Get last update time
        last_update_query = text("""
            SELECT MAX(created_at) as last_update 
            FROM business_report 
            WHERE store_id = :store_id
        """)
        result = db.session.execute(last_update_query, {'store_id': 1}).first()
        
        # Handle last_update date formatting safely
        last_update = None
        if result and result.last_update:
            if isinstance(result.last_update, str):
                # If last_update is already a string, use as-is
                last_update = result.last_update
            else:
                # If it's a datetime object, format it
                last_update = result.last_update.strftime('%Y-%m-%d %H:%M')
        
        return render_template('analytics/dashboard.html',
                             total_reports=total_reports,
                             last_update=last_update or 'Never')
    except Exception as e:
        print(f"Error in dashboard route: {str(e)}")
        return render_template('analytics/dashboard.html',
                             total_reports=0,
                             last_update='Error loading data')

@bp.route('/advertisement-report')
@login_required
def advertisement_report():
    """Advertisement report page."""
    try:
        # Get unique campaigns and ad groups for filters
        campaigns_query = text("""
            SELECT DISTINCT campaign_name 
            FROM advertising_report 
            WHERE store_id = :store_id
            ORDER BY campaign_name
        """)
        ad_groups_query = text("""
            SELECT DISTINCT ad_group_name 
            FROM advertising_report 
            WHERE store_id = :store_id
            ORDER BY ad_group_name
        """)
        
        campaigns = db.session.execute(campaigns_query, {'store_id': 1}).scalars().all()
        ad_groups = db.session.execute(ad_groups_query, {'store_id': 1}).scalars().all()
        
        return render_template(
            'analytics/advertisement_report.html',
            campaigns=campaigns,
            ad_groups=ad_groups
        )
    except Exception as e:
        print(f"Error in advertisement_report route: {str(e)}")
        return render_template(
            'analytics/advertisement_report.html',
            error=str(e)
        )

@bp.route('/advertisement', methods=['GET'])
@login_required
def get_advertisement_analytics():
    """Advertisement analytics API endpoint."""
    try:
        # Get request parameters
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        campaign = request.args.get('campaign')
        ad_group = request.args.get('ad_group')
        targeting_type = request.args.get('targeting_type')
        store_id = current_user.active_store_id

        # Log incoming request parameters for debugging
        print(f"Advertisement analytics request - Parameters:")
        print(f"store_id: {store_id}")
        print(f"start_date: {start_date}")
        print(f"end_date: {end_date}")
        print(f"campaign: {campaign}")
        print(f"ad_group: {ad_group}")
        print(f"targeting_type: {targeting_type}")

        # Validate required parameters
        if not start_date or not end_date:
            return jsonify({'error': 'Date range is required'}), 400

        if not store_id:
            return jsonify({'error': 'Store ID is required'}), 400

        try:
            # Parse and validate dates
            start_datetime = datetime.strptime(start_date, '%Y-%m-%d')
            end_datetime = datetime.strptime(end_date, '%Y-%m-%d')

            # Check if start_date is greater than end_date
            if start_datetime > end_datetime:
                return jsonify({'error': 'Start date cannot be greater than end date'}), 400

            # Add time components for proper range
            start_date = start_datetime.strftime('%Y-%m-%d 00:00:00')
            end_date = end_datetime.strftime('%Y-%m-%d 23:59:59')

            if DEBUG:
                print(f"Parsed dates - start: {start_date}, end: {end_date}")

        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400

        # Cache key oluştur
        cache_key = f"advertisement_analytics:{store_id}:{start_date}:{end_date}:{campaign}:{ad_group}:{targeting_type}"
        cached_data = redis_client.get(cache_key)

        # Eğer cache'de veri varsa, cached veriyi döndür
        if cached_data:
            if DEBUG:
                print("Cache hit! Returning cached data.")
            return jsonify(json.loads(cached_data))

        # Base query for advertisement metrics (Tarih tablosu kullanılıyor)
        base_query = """
            WITH date_range AS (
                SELECT date
                FROM date_table
                WHERE date BETWEEN ? AND ?
            )
            SELECT 
                date_range.date as date,
                COALESCE(SUM(CAST(REPLACE(REPLACE(spend, '$', ''), ',', '') AS FLOAT)), 0) as spend,
                COALESCE(SUM(CAST(REPLACE(REPLACE(total_sales, '$', ''), ',', '') AS FLOAT)), 0) as sales,
                COALESCE(SUM(clicks), 0) as clicks,
                COALESCE(SUM(impressions), 0) as impressions,
                COALESCE(SUM(total_orders), 0) as orders,
                COALESCE(SUM(total_units), 0) as units,
                CASE 
                    WHEN COALESCE(SUM(impressions), 0) = 0 THEN 0 
                    ELSE CAST(COALESCE(SUM(clicks), 0) AS FLOAT) / COALESCE(SUM(impressions), 0) * 100 
                END as ctr,
                CASE 
                    WHEN COALESCE(SUM(clicks), 0) = 0 THEN 0 
                    ELSE CAST(COALESCE(SUM(CAST(REPLACE(REPLACE(spend, '$', ''), ',', '') AS FLOAT)), 0) AS FLOAT) / COALESCE(SUM(clicks), 0)
                END as cpc,
                CASE 
                    WHEN COALESCE(SUM(clicks), 0) = 0 THEN 0 
                    ELSE CAST(COALESCE(SUM(total_orders), 0) AS FLOAT) / COALESCE(SUM(clicks), 0) * 100 
                END as conversion_rate,
                CASE 
                    WHEN COALESCE(SUM(CAST(REPLACE(REPLACE(total_sales, '$', ''), ',', '') AS FLOAT)), 0) = 0 THEN 0 
                    ELSE CAST(COALESCE(SUM(CAST(REPLACE(REPLACE(spend, '$', ''), ',', '') AS FLOAT)), 0) AS FLOAT) / 
                         COALESCE(SUM(CAST(REPLACE(REPLACE(total_sales, '$', ''), ',', '') AS FLOAT)), 0) * 100 
                END as acos
            FROM date_range
            LEFT JOIN advertising_report ON 
                DATE(advertising_report.date) = date_range.date
                AND advertising_report.store_id = ?
        """

        params = [start_date, end_date, store_id]

        # Add filters
        if campaign:
            base_query += " AND campaign_name = ?"
            params.append(campaign)
        
        if ad_group:
            base_query += " AND ad_group_name = ?"
            params.append(ad_group)
        
        if targeting_type:
            base_query += " AND targeting_type = ?"
            params.append(targeting_type)

        # Add group by and order by
        base_query += """
            GROUP BY date_range.date
            ORDER BY date_range.date
        """

        # Execute query (Pandas kullanmadan saf SQL)
        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        cursor.execute(base_query, params)
        rows = cursor.fetchall()
        conn.close()

        # Eğer veri yoksa, default değerlerle döndür
        if not rows:
            response_data = {
                'labels': [],
                'spend': [],
                'sales': [],
                'ctr': [],
                'cpc': [],
                'conversion_rates': [],
                'total_spend': 0,
                'total_sales': 0,
                'total_clicks': 0,
                'total_impressions': 0,
                'total_orders': 0,
                'total_units': 0,
                'acos': 0,
                'average_ctr': 0,
                'average_cpc': 0,
                'average_conversion_rate': 0
            }
            return jsonify(response_data)

        # Verileri manuel olarak işle
        data = {
            'labels': [],
            'spend': [],
            'sales': [],
            'ctr': [],
            'cpc': [],
            'conversion_rates': [],
            'acos_trend': []
        }

        for row in rows:
            data['labels'].append(row[0])
            data['spend'].append(row[1])
            data['sales'].append(row[2])
            data['ctr'].append(row[3])
            data['cpc'].append(row[4])
            data['conversion_rates'].append(row[5])
            data['acos_trend'].append(row[6])

        # Metrikleri hesapla
        total_spend = sum(row[1] for row in rows)
        total_sales = sum(row[2] for row in rows)
        total_clicks = sum(row[3] for row in rows)
        total_impressions = sum(row[4] for row in rows)
        total_orders = sum(row[5] for row in rows)
        total_units = sum(row[6] for row in rows)

        average_ctr = sum(row[3] for row in rows) / len(rows) if rows else 0
        average_cpc = sum(row[4] for row in rows) / len(rows) if rows else 0
        average_conversion_rate = sum(row[5] for row in rows) / len(rows) if rows else 0
        acos = sum(row[6] for row in rows) / len(rows) if rows else 0

        # Önceki dönem verilerini hesapla
        previous_start = start_datetime - timedelta(days=(end_datetime - start_datetime).days)
        previous_end = start_datetime - timedelta(days=1)

        prev_query = base_query
        prev_params = [
            previous_start.strftime('%Y-%m-%d 00:00:00'),
            previous_end.strftime('%Y-%m-%d 23:59:59'),
            store_id
        ]
        if campaign:
            prev_params.append(campaign)
        if ad_group:
            prev_params.append(ad_group)
        if targeting_type:
            prev_params.append(targeting_type)

        conn = sqlite3.connect('instance/app.db')
        cursor = conn.cursor()
        cursor.execute(prev_query, prev_params)
        prev_rows = cursor.fetchall()
        conn.close()

        previous_spend = sum(row[1] for row in prev_rows) if prev_rows else 0
        previous_sales = sum(row[2] for row in prev_rows) if prev_rows else 0

        # Büyüme oranlarını hesapla
        spend_growth = ((total_spend - previous_spend) / previous_spend * 100) if previous_spend > 0 else 0
        sales_growth = ((total_sales - previous_sales) / previous_sales * 100) if previous_sales > 0 else 0

        # Response data hazırla
        response_data = {
            'labels': data['labels'],
            'spend': data['spend'],
            'sales': data['sales'],
            'ctr': data['ctr'],
            'cpc': data['cpc'],
            'conversion_rates': data['conversion_rates'],
            'acos_trend': data['acos_trend'],
            'total_spend': total_spend,
            'total_sales': total_sales,
            'total_clicks': total_clicks,
            'total_impressions': total_impressions,
            'total_orders': total_orders,
            'total_units': total_units,
            'acos': acos,
            'average_ctr': average_ctr,
            'average_cpc': average_cpc,
            'average_conversion_rate': average_conversion_rate,
            'spend_growth': spend_growth,
            'sales_growth': sales_growth,
            'previous_spend': previous_spend,
            'previous_sales': previous_sales
        }

        # Cache'e kaydet (10 dakika boyunca)
        redis_client.setex(cache_key, 600, json.dumps(response_data))

        if DEBUG:
            print("API Response:", response_data)

        return jsonify(response_data)

    except Exception as e:
        print(f"Error in get_advertisement_analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500