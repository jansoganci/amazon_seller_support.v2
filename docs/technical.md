# Technical Documentation

## Architecture

### Technology Stack
- Backend: Flask (Python)
- Database: SQLite (Development) / PostgreSQL (Production)
- Frontend: HTML, TailwindCSS, JavaScript
- Testing: Pytest

### Project Structure
```
amazon_seller_support/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── store.py
│   │   └── reports.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── csv_processor.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── stores.py
│   │   └── reports.py
│   └── templates/
│       ├── base.html
│       └── dashboard/
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
├── docs/
│   ├── api.md
│   ├── user_guide.md
│   └── technical.md
└── migrations/
```

## Database Schema

### Users
```sql
CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL
);
```

### Stores
```sql
CREATE TABLE store (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(200) NOT NULL,
    seller_id VARCHAR(50) NOT NULL,
    marketplace VARCHAR(10) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user (id)
);
```

### Reports
```sql
-- Business Reports
CREATE TABLE business_report (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    asin VARCHAR(10) NOT NULL,
    title VARCHAR(200) NOT NULL,
    units_sold INTEGER NOT NULL,
    revenue NUMERIC(10,2) NOT NULL,
    returns INTEGER NOT NULL,
    conversion_rate NUMERIC(5,4) NOT NULL,
    page_views INTEGER NOT NULL,
    sessions INTEGER NOT NULL,
    created_at DATETIME NOT NULL,
    report_period VARCHAR(20) NOT NULL,
    FOREIGN KEY (store_id) REFERENCES store (id)
);

-- Advertising Reports
CREATE TABLE advertising_report (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    date DATE NOT NULL,
    campaign_name VARCHAR(100) NOT NULL,
    ad_group_name VARCHAR(100) NOT NULL,
    targeting_type VARCHAR(50) NOT NULL,
    match_type VARCHAR(50) NOT NULL,
    search_term VARCHAR(200) NOT NULL,
    impressions INTEGER NOT NULL,
    clicks INTEGER NOT NULL,
    ctr NUMERIC(7,4) NOT NULL,
    cpc NUMERIC(10,2) NOT NULL,
    spend NUMERIC(10,2) NOT NULL,
    total_sales NUMERIC(10,2) NOT NULL,
    acos NUMERIC(7,4) NOT NULL,
    total_orders INTEGER NOT NULL,
    total_units INTEGER NOT NULL,
    conversion_rate NUMERIC(7,4) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES store (id)
);

-- Similar tables for inventory_report and return_report
```

## Key Components

### CSVProcessor
Handles CSV file processing:
- Validation
- Import
- Export
- Data transformation

```python
class CSVProcessor:
    def validate_csv(self, file_path: str, report_type: str) -> bool
    def import_data(self, file_path: str, report_type: str) -> List[BaseReport]
    def export_data(self, store_id: int, report_type: str, file_path: str) -> bool
```

### Analytics Engine
Processes report data for insights:
- Sales analysis
- Inventory optimization
- Advertising performance
- Return patterns

```python
class AnalyticsEngine:
    def calculate_sales_metrics(self, store_id: int, period: str) -> Dict
    def analyze_inventory(self, store_id: int) -> Dict
    def evaluate_advertising(self, store_id: int) -> Dict
    def assess_returns(self, store_id: int) -> Dict
```

## Seasonal Analytics Engine

### Architecture

The seasonal analytics engine is built on top of SQLAlchemy and provides sophisticated analysis of sales patterns. Here's how it works:

#### Data Flow
1. Raw sales data from `BusinessReport` model
2. Aggregation and analysis in `AnalyticsEngine`
3. Results returned as structured dictionaries

#### Key Components

##### AnalyticsEngine
Main class that handles all analytics operations:
```python
class AnalyticsEngine:
    def analyze_seasonal_trends(
        self,
        store_id: int,
        season_type: SeasonType,
        base_year: int,
        comparison_years: Optional[List[int]] = None,
        include_special_periods: bool = True
    ) -> Dict
```

##### Analysis Types
1. Periodic Analysis
   - Weekly: 7-day patterns
   - Monthly: Month-over-month trends
   - Quarterly: Seasonal patterns
   - Yearly: Annual comparisons

2. Special Period Analysis
   - Holiday detection
   - Growth rate calculation
   - Year-over-year comparison

3. Growth Pattern Detection
   - Local peak detection (neighbor comparison)
   - Global significance (yearly average)
   - Trend identification

### Database Schema

#### BusinessReport
```sql
CREATE TABLE business_report (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    units_sold INTEGER NOT NULL,
    revenue DECIMAL NOT NULL,
    conversion_rate FLOAT,
    report_period VARCHAR(10) NOT NULL,
    FOREIGN KEY (store_id) REFERENCES store (id)
);
```

### API Reference

#### analyze_seasonal_trends
```python
def analyze_seasonal_trends(
    store_id: int,
    season_type: SeasonType,
    base_year: int,
    comparison_years: Optional[List[int]] = None,
    include_special_periods: bool = True
) -> Dict:
    """
    Analyze seasonal trends and patterns.
    
    Returns:
    {
        'periodic_sales': List[Dict],  # Period-specific data
        'year_over_year': Dict,        # Comparison data
        'special_periods': Dict,        # Holiday analysis
        'growth_patterns': Dict         # Trend analysis
    }
    """
```

### Performance Considerations

1. Query Optimization
   - Uses SQLAlchemy's bulk operations
   - Efficient date filtering
   - Proper indexing on created_at and store_id

2. Memory Management
   - Streaming large datasets
   - Efficient data structures
   - Proper cleanup of temporary objects

3. Error Handling
   - Graceful handling of NULL values
   - Proper exception handling
   - Detailed error logging

## Authentication & Authorization

### JWT Authentication
- Token-based authentication
- Refresh token mechanism
- Role-based access control

### Store Access Control
- Users can only access their own stores
- Store-level permissions
- API key management

## Testing

### Test Structure
```
tests/
├── conftest.py          # Test fixtures
├── test_models.py       # Model tests
├── test_routes.py       # API tests
└── test_utils.py        # Utility tests
```

### Test Data
Sample CSV files in `tests/test_data/`:
- business_report.csv
- inventory_report.csv
- advertising_report.csv
- return_report.csv

### Running Tests
```bash
pytest                   # Run all tests
pytest -v               # Verbose output
pytest tests/test_*.py  # Specific test file
pytest -k "test_name"   # Specific test function
```

## Deployment

### Development
```bash
flask run --debug
```

### Production
Using Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### Environment Variables
```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
```

## Performance Considerations

### Database Optimization
- Indexed fields: store_id, asin, created_at
- Partitioned tables for large datasets
- Query optimization

### CSV Processing
- Batch processing for large files
- Background tasks for import/export
- Memory efficient streaming

### Caching
- Redis for session storage
- Query result caching
- API response caching

### CSV Format Specifications

#### Business Report
- Required columns: store_id, date, sku, asin, title, sessions, units_ordered, ordered_product_sales, total_order_items, conversion_rate
- Date format: YYYY-MM-DD
- Numeric precision: 2 decimal places for monetary values, 4 decimal places for rates

#### Advertising Report
- Required columns: store_id, date, campaign_name, ad_group_name, targeting_type, match_type, search_term, impressions, clicks, ctr, cpc, spend, total_sales, acos, total_orders, total_units, conversion_rate
- Date format: YYYY-MM-DD
- Numeric precision:
  - 4 decimal places: ctr, acos, conversion_rate
  - 2 decimal places: cpc, spend, total_sales
  - Integer: impressions, clicks, total_orders, total_units

#### Data Validation Rules
1. Store ID must exist and belong to the current user
2. Date must be a valid date in YYYY-MM-DD format
3. Numeric fields must be non-negative
4. Text fields must not exceed their maximum lengths
5. Required fields must not be empty
6. Decimal precision must match the specified format

### Store Management
- User-Store relationship implemented
- Auto-incrementing store IDs
- Store detail page with performance metrics
- Store-level permissions and access control

### CSV Processing
- Return Report integration completed
  - Return rate calculation
  - Customer feedback analysis
  - Return reason categorization
- Inventory Report integration completed
  - Stock level monitoring
  - Reorder point calculation
  - Warehouse distribution tracking

### Database Schema Updates
```sql
-- Return Reports
CREATE TABLE return_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    return_date DATE NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    asin VARCHAR(10) NOT NULL,
    title VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL,
    return_reason TEXT,
    status VARCHAR(50),
    refund_amount DECIMAL(10,2),
    return_center VARCHAR(100),
    return_carrier VARCHAR(100),
    tracking_number VARCHAR(100),
    FOREIGN KEY (store_id) REFERENCES store (id)
);

-- Inventory Reports
CREATE TABLE inventory_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    date DATE NOT NULL,
    sku VARCHAR(50) NOT NULL,
    asin VARCHAR(10) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    condition VARCHAR(50),
    price DECIMAL(10,2),
    mfn_listing_exists BOOLEAN,
    mfn_fulfillable_quantity INTEGER,
    afn_listing_exists BOOLEAN,
    afn_warehouse_quantity INTEGER,
    afn_fulfillable_quantity INTEGER,
    afn_unsellable_quantity INTEGER,
    afn_reserved_quantity INTEGER,
    afn_total_quantity INTEGER,
    per_unit_volume DECIMAL(10,2),
    FOREIGN KEY (store_id) REFERENCES store (id)
);
```

### Performance Optimizations
- Added indexes for return_date and asin in return_reports
- Added indexes for date and sku in inventory_reports
- Optimized CSV validation process

## Database Access
### SQL Query Structure
- Direct SQL queries are used instead of SQLAlchemy ORM for better performance with pandas
- All SQL queries are parameterized using SQLAlchemy text() to prevent SQL injection
- Query parameters are always bound using dictionary format

Example:
```sql
sql = text("""
    SELECT date, ordered_product_sales
    FROM business_report
    WHERE store_id = :store_id
    AND date >= :start_date
    AND date <= :end_date
    ORDER BY date
""")

df = pd.read_sql(
    sql,
    db.session.bind,
    params={
        'store_id': store_id,
        'start_date': start_date,
        'end_date': end_date
    }
)
```

## Category Management
### ASIN-Category Mapping
- Categories are managed through a JSON file (`data/asin_categories.json`)
- No database storage for categories to reduce customer input requirements
- Categories are dynamically mapped using ASIN lookup
- Two-level category structure: Main Category and Subcategory

Example JSON structure:
```json
{
    "B07EXAMPLE1": {
        "main_category": "ELECTRONICS",
        "sub_category": "PC"
    }
}
```

### Category Retrieval Process
1. Get ASIN from Business Report
2. Look up category in JSON file
3. Default to ELECTRONICS/ALL_ELECTRONICS if ASIN not found
4. Cache frequently accessed mappings for performance

## Analytics Engine

### Revenue Trends API

#### Date Filtering
The revenue trends API now uses proper date filtering with the following improvements:
- Uses the `date` column instead of `created_at` for all queries
- Handles days with no sales using recursive CTE
- Supports daily, weekly, monthly, quarterly, and yearly grouping
- Properly formats dates for SQL queries

Example SQL query for daily revenue trends:
```sql
WITH RECURSIVE dates(date) AS (
    SELECT date(:start_date)
    UNION ALL
    SELECT date(date, '+1 day')
    FROM dates
    WHERE date < date(:end_date)
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
    AND business_report.store_id = :store_id
GROUP BY date_group
ORDER BY date_group
```

#### Category and ASIN Filtering
- Category filtering is done by matching ASINs to categories
- ASIN filtering supports both single ASIN and category-based ASIN lists
- Proper SQL parameter binding for security

#### Metrics Calculation
- Revenue: Sum of ordered product sales
- Units: Sum of units ordered
- Sessions: Sum of sessions
- Conversion Rate: (Units / Sessions) * 100
- Growth Rate: ((Current Period Revenue - Previous Period Revenue) / Previous Period Revenue) * 100
