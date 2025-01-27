"""Business module constants."""

from decimal import Decimal
from typing import Dict

# CSV file constants
DATE_FORMAT = '%Y-%m-%d'

# Maximum field lengths
MAX_ASIN_LENGTH = 10
MAX_SKU_LENGTH = 40
MAX_TITLE_LENGTH = 200

# Required columns and their types
REQUIRED_COLUMNS = [
    'store_id',
    'date',
    'sku',
    'asin',
    'title',
    'sessions',
    'units_ordered',
    'ordered_product_sales',
    'total_order_items',
    'conversion_rate'
]

COLUMN_TYPES: Dict[str, type] = {
    'store_id': int,
    'date': str,
    'sku': str,
    'asin': str,
    'title': str,
    'sessions': int,
    'units_ordered': int,
    'ordered_product_sales': Decimal,
    'total_order_items': int,
    'conversion_rate': Decimal
}

# Error messages
ERROR_MESSAGES = {
    'EMPTY_FILE': 'CSV file is empty',
    'MISSING_COLUMNS': 'Missing required columns: {}',
    'MISSING_REQUIRED_FIELD': 'Missing required field: {}',
    'DUPLICATE_ENTRY': 'Duplicate entries found in CSV file',
    'INVALID_DATE_FORMAT': f'Invalid date format. Expected format: {DATE_FORMAT}',
    'ASIN_TOO_LONG': f'ASIN length exceeds maximum of {MAX_ASIN_LENGTH} characters',
    'SKU_TOO_LONG': f'SKU length exceeds maximum of {MAX_SKU_LENGTH} characters',
    'TITLE_TOO_LONG': f'Title length exceeds maximum of {MAX_TITLE_LENGTH} characters',
    'INVALID_NUMERIC': 'Invalid numeric value for field: {}',
    'NEGATIVE_VALUE': 'Negative value not allowed for field: {}',
    'INVALID_CONVERSION_RATE': 'Conversion rate must be between 0 and 100'
}

# Time-based grouping options
GROUPING_OPTIONS = {
    'daily': 'Daily',
    'weekly': 'Weekly',
    'monthly': 'Monthly',
    'quarterly': 'Quarterly',
    'yearly': 'Yearly'
}

DEFAULT_GROUP_BY = 'daily'
DEFAULT_PAGE_SIZE = 50
DEFAULT_SORT_ORDER = 'desc'

# CSV Export Constants
EXPORT_COLUMNS = [
    'store_id',
    'date',
    'sku',
    'asin',
    'title',
    'sessions',
    'units_ordered',
    'ordered_product_sales',
    'total_order_items',
    'conversion_rate'
]

# Database Constants
DB_TABLE_NAME = 'business_reports'
DB_COLUMNS = {
    'id': 'SERIAL PRIMARY KEY',
    'store_id': 'INTEGER NOT NULL',
    'date': 'DATE NOT NULL',
    'sku': 'VARCHAR(40) NOT NULL',
    'asin': 'VARCHAR(10) NOT NULL',
    'title': 'VARCHAR(200) NOT NULL',
    'sessions': 'INTEGER NOT NULL',
    'units_ordered': 'INTEGER NOT NULL',
    'ordered_product_sales': 'NUMERIC(10, 2) NOT NULL',
    'total_order_items': 'INTEGER NOT NULL',
    'conversion_rate': 'NUMERIC(5, 2) NOT NULL',
    'created_at': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP',
    'updated_at': 'TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP'
}

# Export settings
EXPORT_CHUNK_SIZE = 1000
MAX_EXPORT_ROWS = 50000

# Chart Types
CHART_TYPES = {
    'revenue': {
        'title': 'Revenue Over Time',
        'type': 'line',
        'data_key': 'ordered_product_sales',
        'format': 'currency'
    },
    'units': {
        'title': 'Units Ordered Over Time',
        'type': 'bar',
        'data_key': 'units_ordered',
        'format': 'number'
    },
    'sessions': {
        'title': 'Sessions Over Time',
        'type': 'line',
        'data_key': 'sessions',
        'format': 'number'
    },
    'conversion': {
        'title': 'Conversion Rate Over Time',
        'type': 'line',
        'data_key': 'conversion_rate',
        'format': 'percentage'
    }
}

# Date Ranges
DATE_RANGES = {
    'today': 'Today',
    'yesterday': 'Yesterday',
    'last_7_days': 'Last 7 Days',
    'last_30_days': 'Last 30 Days',
    'this_month': 'This Month',
    'last_month': 'Last Month',
    'this_year': 'This Year',
    'last_year': 'Last Year',
    'custom': 'Custom Range'
}