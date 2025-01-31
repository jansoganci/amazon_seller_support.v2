"""
Constants for CSV processing and validation.
"""

from decimal import Decimal

# Error Messages
ERROR_MESSAGES = {
    'file_not_found': 'File not found. Please select a valid CSV file.',
    'invalid_file_type': 'Invalid file type. Only CSV files are allowed.',
    'file_too_large': 'File size exceeds the maximum allowed limit.',
    'missing_columns': 'Required columns are missing in the CSV file.',
    'invalid_data': 'The CSV file contains invalid data.',
    'store_not_found': 'Store not found or access denied.',
    'processing_failed': 'Failed to process the CSV file.',
    'server_error': 'An unexpected error occurred while processing the file.',
    'empty_file': 'The CSV file is empty. Please upload a file with data.',
    'encoding_error': 'Unable to read the file encoding. Please ensure the file is properly encoded.',
    'validation_error': 'Data validation failed. Please check the file format and contents.',
    'permission_denied': 'You do not have permission to upload files for this store.',
    'duplicate_file': 'This file has already been uploaded.',
    'corrupted_file': 'The file appears to be corrupted or invalid.',
    'boolean_error': 'Invalid boolean value in column: {}. Use True/False or 1/0',
    'date_error': 'Invalid date format in column: {}. Use YYYY-MM-DD format',
    'duplicate_data': 'Duplicate entries detected for store_id: {} on date: {}'
} 

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