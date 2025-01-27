# Database Architecture

## Core Models

### User Model
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(64) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    is_active BOOLEAN DEFAULT TRUE,
    active_store_id INTEGER REFERENCES stores(id),
    preferences JSON,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (active_store_id) REFERENCES stores(id),
    INDEX idx_users_email (email),
    INDEX idx_users_username (username)
);
```

### Store Model
```sql
CREATE TABLE stores (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    name VARCHAR(128) NOT NULL,
    seller_id VARCHAR(64) UNIQUE,
    marketplace VARCHAR(64) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    INDEX idx_stores_seller (seller_id),
    INDEX idx_stores_user (user_id)
);
```

### User-Store Association
```sql
CREATE TABLE user_stores (
    user_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, store_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    INDEX idx_user_stores_user (user_id),
    INDEX idx_user_stores_store (store_id)
);
```

## Report Models

### Business Report
```sql
CREATE TABLE business_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    date DATE NOT NULL,
    sku VARCHAR(50),
    asin VARCHAR(10) NOT NULL,
    title VARCHAR(255) NOT NULL,
    sessions INTEGER NOT NULL DEFAULT 0,
    session_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    page_views INTEGER NOT NULL DEFAULT 0,
    page_views_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    buy_box_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    units_ordered INTEGER NOT NULL DEFAULT 0,
    units_ordered_b2b INTEGER NOT NULL DEFAULT 0,
    unit_session_percentage NUMERIC(5, 2) NOT NULL DEFAULT 0,
    unit_session_percentage_b2b NUMERIC(5, 2) NOT NULL DEFAULT 0,
    ordered_product_sales NUMERIC(10, 2) NOT NULL DEFAULT 0,
    ordered_product_sales_b2b NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_order_items INTEGER NOT NULL DEFAULT 0,
    total_order_items_b2b INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    INDEX idx_business_store_date (store_id, date),
    INDEX idx_business_asin (asin),
    INDEX idx_business_sku (sku)
);
```

### Advertising Report
```sql
CREATE TABLE advertising_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    campaign_name VARCHAR(100) NOT NULL,
    ad_group_name VARCHAR(100) NOT NULL,
    targeting_type VARCHAR(50) NOT NULL,
    match_type VARCHAR(50) NOT NULL,
    search_term VARCHAR(200) NOT NULL,
    impressions INTEGER NOT NULL DEFAULT 0,
    clicks INTEGER NOT NULL DEFAULT 0,
    ctr NUMERIC(7, 4) NOT NULL DEFAULT 0,
    cpc NUMERIC(10, 2) NOT NULL DEFAULT 0,
    spend NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_sales NUMERIC(10, 2) NOT NULL DEFAULT 0,
    acos NUMERIC(7, 4) NOT NULL DEFAULT 0,
    total_orders INTEGER NOT NULL DEFAULT 0,
    total_units INTEGER NOT NULL DEFAULT 0,
    conversion_rate NUMERIC(7, 4) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id)
);
```

### Inventory Report
```sql
CREATE TABLE inventory_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    sku VARCHAR(50) NOT NULL,
    asin VARCHAR(50) NOT NULL,
    product_name VARCHAR(200) NOT NULL,
    condition VARCHAR(50) NOT NULL,
    price NUMERIC(10, 2) NOT NULL,
    mfn_listing_exists BOOLEAN NOT NULL,
    mfn_fulfillable_quantity INTEGER NOT NULL,
    afn_listing_exists BOOLEAN NOT NULL,
    afn_warehouse_quantity INTEGER NOT NULL,
    afn_fulfillable_quantity INTEGER NOT NULL,
    afn_unsellable_quantity INTEGER NOT NULL,
    afn_reserved_quantity INTEGER NOT NULL,
    afn_total_quantity INTEGER NOT NULL,
    per_unit_volume NUMERIC(10, 4) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id)
);
```

### Return Report
```sql
CREATE TABLE return_reports (
    id INTEGER PRIMARY KEY,
    store_id INTEGER NOT NULL,
    return_date TIMESTAMP NOT NULL,
    order_id VARCHAR(50) NOT NULL,
    sku VARCHAR(50) NOT NULL,
    asin VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    return_reason VARCHAR(200) NOT NULL,
    status VARCHAR(50) NOT NULL,
    refund_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    return_center VARCHAR(200) NOT NULL,
    return_carrier VARCHAR(100) NOT NULL,
    tracking_number VARCHAR(100) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (store_id) REFERENCES stores(id),
    INDEX idx_return_store_date (store_id, return_date),
    INDEX idx_return_order (order_id),
    INDEX idx_return_sku (sku),
    INDEX idx_return_asin (asin),
    INDEX idx_return_status (status)
);
```

## File Management Models

### CSV File
```sql
CREATE TABLE csv_files (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    store_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_path VARCHAR(512) NOT NULL,
    row_count INTEGER,
    processed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (store_id) REFERENCES stores(id),
    INDEX idx_csv_files_user_store (user_id, store_id),
    INDEX idx_csv_files_type_date (file_type, created_at)
);
```

### Upload History
```sql
CREATE TABLE upload_history (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    csv_file_id INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (csv_file_id) REFERENCES csv_files(id)
);
```

## Database Relationships

### One-to-Many Relationships
- User -> Stores (one user can have multiple stores)
- Store -> CSV Files (one store can have multiple CSV files)
- Store -> Business Reports (one store can have multiple business reports)
- Store -> Advertising Reports (one store can have multiple advertising reports)
- Store -> Inventory Reports (one store can have multiple inventory reports)
- Store -> Return Reports (one store can have multiple return reports)
- User -> CSV Files (one user can upload multiple CSV files)
- User -> Upload History (one user can have multiple upload histories)

### Many-to-Many Relationships
- Users <-> Stores (through user_stores table)

### One-to-One Relationships
- CSV File <-> Upload History (each CSV file has one upload history record)

## Indexes and Performance Optimizations

### Core Tables
- users: username, email (unique indexes)
- stores: seller_id (unique index)
- user_stores: (user_id, store_id) composite primary key

### Report Tables
- business_reports: (store_id, date), asin
- return_reports: (store_id, return_date), order_id, sku
- advertising_reports: (store_id, date), campaign_name
- inventory_reports: (store_id, date), sku, asin

### File Management
- csv_files: (user_id, store_id), (file_type, created_at)
- upload_history: user_id, csv_file_id

## Data Types and Constraints

### Numeric Fields
- All monetary values: NUMERIC(10, 2)
- Percentages and rates: NUMERIC(7, 4)
- Quantities: INTEGER
- IDs: INTEGER

### String Fields
- Short identifiers: VARCHAR(50)
- Names and titles: VARCHAR(200)
- File paths: VARCHAR(512)
- Status and types: VARCHAR(20-50)

### Date and Time
- All timestamps use UTC timezone
- Created/Updated timestamps auto-update
- Report dates use appropriate precision (DATE or TIMESTAMP)

### Constraints
- NOT NULL on critical fields
- DEFAULT values for status fields
- FOREIGN KEY constraints with appropriate actions
- UNIQUE constraints on business identifiers

## Database Optimizations

### Indexing Strategy
1. **Primary Keys**: All tables have integer primary keys for efficient joins
2. **Foreign Keys**: All foreign keys are indexed for faster joins
3. **Search Fields**: Common search fields have dedicated indexes:
   - `users`: email, username
   - `stores`: seller_id
   - `business_reports`: store_id + date, asin, sku
   - `return_reports`: store_id + return_date, order_id, sku, asin, status

### Default Values
- Added appropriate DEFAULT values for numeric fields (0)
- All timestamp fields default to CURRENT_TIMESTAMP

### Field Constraints
- Added NOT NULL constraints where appropriate
- Defined field sizes based on actual data requirements:
  - ASIN: 10 characters (Amazon standard)
  - SKU: 50 characters
  - Order ID: 50 characters
  - Title: 200-255 characters

### Performance Considerations
1. **Composite Indexes**:
   - (store_id, date) for efficient date range queries per store
   - (user_id, store_id) for quick user-store lookups

2. **Numeric Precision**:
   - Money values: NUMERIC(10,2) for amounts up to 99,999,999.99
   - Percentages: NUMERIC(5,2) for values up to 100.00%

3. **JSON Storage**:
   - User preferences stored as JSON for flexibility
   - Indexed JSON fields where needed

## Database Migrations
All changes are tracked in migrations:
1. Initial schema creation
2. Added indexes for performance
3. Updated field constraints and defaults
4. Added new columns for B2B data
5. Changed date to return_date in return_reports
