"""Inventory module constants."""

# Required columns for CSV validation
REQUIRED_COLUMNS = [
    'snapshot_date',
    'sku',
    'asin',
    'product_name',
    'condition',
    'sellable_quantity',
    'unsellable_quantity',
    'reserved_quantity',
    'warehouse',
    'restock_level',
    'inbound_quantity'
]

# Error messages
ERROR_MESSAGES = {
    'NO_DATA': 'No data found for the specified period',
    'INVALID_DATE': 'Invalid date format',
    'MISSING_COLUMNS': 'Missing required columns',
    'INVALID_NUMERIC': 'Invalid numeric value',
    'NO_STORE_ACCESS': 'No access to the specified store',
    'UNKNOWN_ERROR': 'An unknown error occurred'
} 