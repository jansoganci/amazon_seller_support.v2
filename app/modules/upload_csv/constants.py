"""
Constants for CSV processing and validation.
"""

from decimal import Decimal

# CSV Column Definitions
CSV_COLUMNS = {
    'business_report': {
        'required': [
            'store_id', 'date', 'sku', 'asin', 'title',
            'sessions', 'units_ordered', 'ordered_product_sales',
            'total_order_items', 'conversion_rate'
        ],
        'numeric': {
            'units_ordered': int,
            'ordered_product_sales': Decimal,
            'sessions': int,
            'total_order_items': int,
            'conversion_rate': Decimal
        },
        'date': ['date']
    },
    
    'advertising_report': {
        'required': [
            'store_id', 'date', 'campaign_name', 'ad_group_name',
            'targeting_type', 'match_type', 'search_term',
            'impressions', 'clicks', 'ctr', 'cpc', 'spend',
            'total_sales', 'acos', 'total_orders', 'total_units',
            'conversion_rate'
        ],
        'numeric': {
            'impressions': int,
            'clicks': int,
            'ctr': Decimal,
            'cpc': Decimal,
            'spend': Decimal,
            'total_sales': Decimal,
            'acos': Decimal,
            'total_orders': int,
            'total_units': int,
            'conversion_rate': Decimal
        },
        'date': ['date']
    },

    'inventory_report': {
        'required': [
            'store_id', 'date', 'sku', 'asin', 'product_name',
            'condition', 'price', 'mfn_listing_exists',
            'mfn_fulfillable_quantity', 'afn_listing_exists',
            'afn_warehouse_quantity', 'afn_fulfillable_quantity',
            'afn_unsellable_quantity', 'afn_reserved_quantity',
            'afn_total_quantity', 'per_unit_volume'
        ],
        'numeric': {
            'price': Decimal,
            'mfn_fulfillable_quantity': int,
            'afn_warehouse_quantity': int,
            'afn_fulfillable_quantity': int,
            'afn_unsellable_quantity': int,
            'afn_reserved_quantity': int,
            'afn_total_quantity': int,
            'per_unit_volume': Decimal
        },
        'boolean': ['mfn_listing_exists', 'afn_listing_exists'],
        'date': ['date']
    },

    'return_report': {
        'required': [
            'store_id', 'return_date', 'order_id', 'sku', 'asin',
            'title', 'quantity', 'return_reason', 'status',
            'refund_amount', 'return_center', 'return_carrier',
            'tracking_number'
        ],
        'numeric': {
            'quantity': int,
            'refund_amount': Decimal
        },
        'date': ['return_date']
    }
}

# Error Messages
ERROR_MESSAGES = {
    'file_required': 'No file was uploaded',
    'invalid_file_type': 'Invalid file type. Please upload a CSV file',
    'decode_error': 'Unable to decode CSV file. Please ensure it is properly encoded',
    'missing_columns': 'Missing required columns: {}',
    'invalid_data': 'Invalid data in column: {}',
    'store_not_found': 'Store not found or access denied: {}',
    'duplicate_data': 'Duplicate entries detected for store_id: {} on date: {}',
    'boolean_error': 'Invalid boolean value in column: {}. Use True/False or 1/0',
    'date_error': 'Invalid date format in column: {}. Use YYYY-MM-DD format'
} 