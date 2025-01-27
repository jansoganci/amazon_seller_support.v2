"""Returns module constants."""

# Required columns for CSV validation
REQUIRED_COLUMNS = [
    'return_date',
    'order_id',
    'sku',
    'asin',
    'title',
    'quantity',
    'return_reason',
    'status',
    'refund_amount',
    'return_center',
    'return_carrier',
    'tracking_number'
]

# Valid values for return fields
VALID_RETURN_CENTERS = [
    'FBA',  # Fulfillment by Amazon
    'AMZ-NYC-01',  # Amazon New York Center
    'AMZ-LAX-02',  # Amazon Los Angeles Center
    'AMZ-CHI-03'   # Amazon Chicago Center
]

# Valid carriers for returns
VALID_RETURN_CARRIERS = [
    'Amazon Logistics',
    'UPS',
    'FedEx',
    'USPS'
]

# Valid tracking number prefixes
VALID_TRACKING_PREFIXES = [
    'TBA',  # Amazon Logistics
    '1Z',   # UPS
    '7',    # FedEx
    '9'     # USPS
]

# Error messages
ERROR_MESSAGES = {
    'NO_DATA': 'No data found for the specified period',
    'INVALID_DATE': 'Invalid date format',
    'MISSING_COLUMNS': 'Missing required columns',
    'INVALID_NUMERIC': 'Invalid numeric value',
    'NO_STORE_ACCESS': 'No access to the specified store',
    'UNKNOWN_ERROR': 'An unknown error occurred',
    'INVALID_RETURN_CENTER': 'Invalid return center. Valid values: {}'.format(', '.join(VALID_RETURN_CENTERS)),
    'INVALID_RETURN_CARRIER': 'Invalid return carrier. Valid values: {}'.format(', '.join(VALID_RETURN_CARRIERS)),
    'INVALID_TRACKING_NUMBER': 'Invalid tracking number format'
}