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
