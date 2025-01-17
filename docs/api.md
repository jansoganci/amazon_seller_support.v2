# Amazon Seller Support API Documentation

## Overview
This API provides endpoints for managing Amazon seller reports, including business reports, inventory reports, advertising reports, and return reports.

## Authentication
All API endpoints require authentication. Use the following headers:
```
Authorization: Bearer <your_token>
```

## Endpoints

### Store Management

#### GET /api/stores
Get all stores for the authenticated user.

**Response**
```json
{
    "stores": [
        {
            "id": 1,
            "name": "My Store",
            "seller_id": "A2XYZ123",
            "marketplace": "US"
        }
    ]
}
```

### Report Management

#### POST /api/reports/upload
Upload a new report CSV file.

**Request**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - `store_id`: Integer
  - `report_type`: String (business|inventory|advertising|return)
  - `file`: CSV File

**Response**
```json
{
    "success": true,
    "message": "Report uploaded successfully",
    "report_count": 10
}
```

#### GET /api/reports/{report_type}
Get reports by type.

**Parameters**
- `report_type`: String (business|inventory|advertising|return)
- `store_id`: Integer (query parameter)
- `start_date`: Date (optional, query parameter)
- `end_date`: Date (optional, query parameter)

**Response**
```json
{
    "reports": [
        {
            "id": 1,
            "store_id": 1,
            "asin": "B001TEST1",
            "title": "Test Product",
            // Other fields specific to report type
        }
    ]
}
```

#### GET /api/reports/export/{report_type}
Export reports to CSV.

**Parameters**
- `report_type`: String (business|inventory|advertising|return)
- `store_id`: Integer (query parameter)
- `start_date`: Date (optional, query parameter)
- `end_date`: Date (optional, query parameter)

**Response**
- Content-Type: text/csv
- File download with reports data

### Analytics

#### GET /api/analytics/summary
Get analytics summary for a store.

**Parameters**
- `store_id`: Integer (query parameter)
- `period`: String (daily|weekly|monthly, optional)

**Response**
```json
{
    "total_sales": 10000.50,
    "total_orders": 500,
    "average_order_value": 20.00,
    "return_rate": 0.05,
    "advertising_cost": 500.25,
    "acos": 0.05
}
```

### Seasonal Analytics API

#### Analyze Seasonal Trends

Analyze sales patterns and trends across different time periods.

```http
GET /api/v1/analytics/seasonal/{store_id}
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| store_id | integer | Yes | Store ID to analyze |
| season_type | string | Yes | Analysis type: 'weekly', 'monthly', 'quarterly', 'yearly' |
| base_year | integer | Yes | Base year for analysis |
| comparison_years | array | No | Years to compare against base_year |
| include_special_periods | boolean | No | Include holiday analysis (default: true) |

#### Response

```json
{
    "periodic_sales": [
        {
            "period": "2025-01",
            "revenue": 50000.00,
            "units_sold": 1000,
            "growth_rate": 0.15,
            "is_peak": true
        }
    ],
    "year_over_year": {
        "growth_rate": 0.25,
        "peak_months": ["July", "December"],
        "strongest_quarter": "Q4"
    },
    "special_periods": {
        "black_friday": {
            "revenue": 15000.00,
            "growth_rate": 0.30
        },
        "christmas": {
            "revenue": 20000.00,
            "growth_rate": 0.25
        }
    },
    "growth_patterns": {
        "seasonal_peaks": ["Summer", "Winter"],
        "consistent_growth": true,
        "trend_strength": 0.8
    }
}
```

#### Example Request

```bash
curl -X GET "https://api.example.com/v1/analytics/seasonal/123?season_type=monthly&base_year=2025" \
     -H "Authorization: Bearer YOUR_TOKEN"
```

#### Get Peak Periods

Retrieve peak sales periods for a store.

```http
GET /api/v1/analytics/peaks/{store_id}
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| store_id | integer | Yes | Store ID to analyze |
| year | integer | No | Specific year (default: current year) |
| threshold | float | No | Peak detection threshold (default: 0.1) |

#### Response

```json
{
    "peaks": [
        {
            "period": "2025-07",
            "revenue": 75000.00,
            "type": "seasonal",
            "significance": 0.25
        }
    ],
    "total_peaks": 3,
    "average_peak_revenue": 70000.00
}
```

#### Compare Special Periods

Compare performance during special periods.

```http
GET /api/v1/analytics/special-periods/{store_id}
```

#### Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| store_id | integer | Yes | Store ID to analyze |
| period_type | string | Yes | 'black_friday', 'christmas', 'custom' |
| start_date | string | No | Start date for custom period |
| end_date | string | No | End date for custom period |

#### Response

```json
{
    "current": {
        "revenue": 25000.00,
        "units_sold": 500
    },
    "previous": {
        "revenue": 20000.00,
        "units_sold": 400
    },
    "growth_rate": 0.25,
    "recommendations": [
        "Consider increasing inventory by 30%",
        "Plan marketing campaign 2 weeks earlier"
    ]
}
```

### Seasonal Analytics

#### GET /api/v1/analytics/seasonal/<store_id>
Returns seasonal analytics data for the specified store.

**Parameters:**
- `store_id` (path parameter, integer): ID of the store

**Response:**
```json
{
  "status": "success",
  "data": {
    "seasonal_trends": [
      {
        "period": "2024-Q4",
        "trend": "up",
        "growth_rate": 15.5,
        "significance": "high"
      }
    ],
    "peak_periods": [
      {
        "start_date": "2024-11-25",
        "end_date": "2024-12-25",
        "type": "holiday_season",
        "sales_increase": 45.2
      }
    ],
    "special_periods": [
      {
        "date": "2024-11-24",
        "name": "Black Friday",
        "sales_volume": 12500,
        "yoy_growth": 22.5
      }
    ]
  }
}
```

### CSV Upload

#### POST /upload-csv
Uploads and processes a CSV report file.

**Request:**
- Content-Type: multipart/form-data

**Parameters:**
- `file` (file): CSV file to upload
- `report_type` (string): Type of report
  - Allowed values: 
    - business_report
    - inventory_report
    - advertising_report
    - return_report

**Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "data": {
    "file_id": "123",
    "filename": "business_report_2024.csv",
    "report_type": "business_report",
    "upload_date": "2025-01-05T21:16:06+07:00",
    "status": "processing"
  }
}
```

#### GET /api/v1/upload-history
Returns the upload history for the current user.

**Response:**
```json
{
  "status": "success",
  "data": {
    "uploads": [
      {
        "file_id": "123",
        "filename": "business_report_2024.csv",
        "report_type": "business_report",
        "upload_date": "2025-01-05T21:16:06+07:00",
        "status": "completed",
        "rows_processed": 1500
      }
    ]
  }
}
```

### Return Reports

#### GET /api/v1/stores/{store_id}/returns
Get return reports for a specific store.

**Parameters:**
- `store_id` (path parameter, integer): ID of the store
- `start_date` (query parameter, string): Start date in YYYY-MM-DD format
- `end_date` (query parameter, string): End date in YYYY-MM-DD format

**Response:**
```json
{
  "status": "success",
  "data": {
    "returns": [
      {
        "return_date": "2025-01-09",
        "order_id": "123-4567890-1234567",
        "asin": "B00TEST123",
        "title": "Test Product",
        "quantity": 1,
        "return_reason": "Size Issue",
        "status": "Completed",
        "refund_amount": 29.99
      }
    ],
    "summary": {
      "total_returns": 150,
      "total_refund_amount": 4500.50,
      "average_return_rate": 0.05
    }
  }
}
```

### Inventory Reports

#### GET /api/v1/stores/{store_id}/inventory
Get inventory reports for a specific store.

**Parameters:**
- `store_id` (path parameter, integer): ID of the store
- `date` (query parameter, string): Date in YYYY-MM-DD format

**Response:**
```json
{
  "status": "success",
  "data": {
    "inventory": [
      {
        "date": "2025-01-09",
        "asin": "B00TEST123",
        "product_name": "Test Product",
        "price": 29.99,
        "afn_fulfillable_quantity": 100,
        "afn_reserved_quantity": 10,
        "afn_total_quantity": 110,
        "reorder_required": false
      }
    ],
    "summary": {
      "total_products": 500,
      "total_value": 15000.50,
      "low_stock_items": 25
    }
  }
}
```

### Store Details

#### GET /api/v1/stores/{store_id}/details
Get detailed information about a specific store.

**Parameters:**
- `store_id` (path parameter, integer): ID of the store

**Response:**
```json
{
  "status": "success",
  "data": {
    "store_info": {
      "id": 1,
      "name": "My Store",
      "marketplace": "US",
      "created_at": "2025-01-09T13:51:43Z"
    },
    "performance_metrics": {
      "total_revenue": 50000.00,
      "total_orders": 1000,
      "return_rate": 0.05,
      "average_order_value": 50.00
    },
    "inventory_summary": {
      "total_products": 500,
      "low_stock_items": 25,
      "out_of_stock_items": 10
    }
  }
}
```

## Error Responses
All endpoints may return the following errors:

```json
{
    "error": "Error message",
    "code": "ERROR_CODE"
}
```

Common error codes:
- `INVALID_TOKEN`: Authentication failed
- `INVALID_STORE`: Store not found or access denied
- `INVALID_REPORT`: Report validation failed
- `INVALID_DATE`: Invalid date format
- `SERVER_ERROR`: Internal server error

## Analytics API

### Get Revenue Trends
Retrieve revenue trends for a specific store over a time period.

**Endpoint:** `/analytics/api/revenue/trends`

**Method:** GET

**Parameters:**
- `store_id` (integer, required): ID of the store
- `start_date` (string, required): Start date in YYYY-MM-DD format
- `end_date` (string, required): End date in YYYY-MM-DD format
- `group_by` (string, optional): Time grouping (daily, weekly, monthly, quarterly, yearly). Default: daily
- `category` (string, optional): Filter by main category

**Response:**
```json
{
    "labels": ["2024-01-01", "2024-01-02", ...],
    "values": [1000.50, 1200.75, ...],
    "total_revenue": 10000.00,
    "growth_rate": 15.5,
    "previous_period": {
        "total_revenue": 8500.00
    }
}
```

**Error Responses:**
- 400 Bad Request: Missing required parameters
- 500 Internal Server Error: Processing error

**Example Request:**
```
GET /analytics/api/revenue/trends?store_id=1&start_date=2024-01-01&end_date=2024-01-31&group_by=weekly&category=ELECTRONICS
```

## Revenue Trends API

### GET /api/revenue/trends

Get revenue trends data with various filtering and grouping options.

#### Request Parameters

| Parameter  | Type    | Required | Description                                           |
|-----------|---------|----------|-------------------------------------------------------|
| store_id  | integer | Yes      | Store ID to get data for                             |
| start_date| string  | No       | Start date in YYYY-MM-DD format (defaults to 30 days ago) |
| end_date  | string  | No       | End date in YYYY-MM-DD format (defaults to today)     |
| group_by  | string  | No       | Grouping interval: daily, weekly, monthly, quarterly, yearly (default: daily) |
| category  | string  | No       | Filter by category (use "All Categories" for no filter) |
| asin      | string  | No       | Filter by ASIN (use "All ASINs" for no filter)       |

#### Response Format

```json
{
    "labels": ["2024-12-14", "2024-12-15", ...],
    "values": [191979.16, 174633.93, ...],
    "units": [1500, 1200, ...],
    "sessions": [5000, 4800, ...],
    "conversion_rates": [30.0, 25.0, ...],
    "total_revenue": 366613.09,
    "total_units": 2700,
    "total_sessions": 9800,
    "average_order_value": 135.78,
    "growth_rate": 15.5,
    "previous_period": 317413.50
}
```

#### Notes
- All dates are handled in UTC
- Days with no sales will return 0 for all metrics
- Revenue values are in store's currency
- Conversion rates are percentages
- Growth rate compares current period with previous period of same length

#### Example Requests

```bash
# Get daily revenue for last 30 days
curl -X GET '/api/revenue/trends?store_id=1'

# Get weekly revenue for specific date range and category
curl -X GET '/api/revenue/trends?store_id=1&start_date=2024-12-01&end_date=2024-12-31&group_by=weekly&category=Electronics'

# Get monthly revenue for specific ASIN
curl -X GET '/api/revenue/trends?store_id=1&group_by=monthly&asin=B01234567'
```
