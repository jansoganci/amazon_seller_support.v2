"""Advertising module constants."""

# Required columns for CSV validation
REQUIRED_COLUMNS = [
    'date',
    'campaign_name',
    'ad_group_name',
    'impressions',
    'clicks',
    'spend',
    'sales',
    'acos',
    'roas'
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