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

-- Similar tables for inventory_report, advertising_report, and return_report
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
