# Report Templates Technical Documentation

## 1. Template Structure

### 1.1 Base Components

#### Header Section
```html
<div class="mb-6">
    <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">[Report Title]</h1>
    <p class="mt-1 text-sm text-gray-600 dark:text-gray-400">[Report Description]</p>
</div>
```

#### Filter Section
```html
<div class="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
    <!-- Date Range Filter -->
    <!-- Group By Filter -->
    <!-- Category Filter -->
    <!-- ASIN Filter -->
    <!-- Apply/Clear Buttons -->
</div>
```

#### Metric Cards Section
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
    <!-- Metric Cards -->
</div>
```

#### Charts Grid Section
```html
<div class="grid grid-cols-1 gap-6 mb-6">
    <!-- Charts -->
</div>
```

### 1.2 Reusable Components

#### Metric Card Component
```html
{% macro metric_card(icon, title, value_id, default_value, extra_info=None) %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
    <div class="flex items-center">
        <div class="flex-shrink-0">
            <i class="fas fa-{{ icon }} text-2xl text-primary-600 dark:text-primary-400"></i>
        </div>
        <div class="ml-4">
            <p class="text-sm font-medium text-gray-600 dark:text-gray-400">{{ title }}</p>
            <p class="text-lg font-semibold text-gray-900 dark:text-white" id="{{ value_id }}">{{ default_value }}</p>
            {% if extra_info %}
            <p class="text-sm text-gray-600 dark:text-gray-400">{{ extra_info | safe }}</p>
            {% endif %}
        </div>
    </div>
</div>
{% endmacro %}
```

#### Chart Component
```html
{% macro chart_container(title, chart_id, height='h-96') %}
<div class="bg-white dark:bg-gray-800 rounded-lg shadow p-4">
    <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-4">{{ title }}</h3>
    <div class="{{ height }}">
        <canvas id="{{ chart_id }}"></canvas>
    </div>
</div>
{% endmacro %}
```

## 2. Data Flow

### 2.1 Initial Data Load

```python
@app.route('/module/<module_name>/report')
@login_required
def module_report(module_name):
    # Default date range (last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # Get initial data
    initial_data = get_report_data(
        store_id=current_user.store_id,
        start_date=start_date,
        end_date=end_date,
        group_by='daily',
        module=module_name
    )
    
    return render_template(
        f'{module_name}/report.html',
        initial_data=initial_data,
        store_id=current_user.store_id
    )
```

### 2.2 Data Processing Pipeline

```python
def get_report_data(store_id, start_date, end_date, group_by='daily', category=None, asin=None):
    """
    Generic data processing pipeline for reports
    """
    try:
        # 1. Validate parameters
        validate_report_params(store_id, start_date, end_date, group_by)
        
        # 2. Build base query
        query = build_base_query(store_id, start_date, end_date)
        
        # 3. Apply filters
        if category:
            query = apply_category_filter(query, category)
        if asin:
            query = apply_asin_filter(query, asin)
            
        # 4. Group data
        grouped_data = group_data_by(query, group_by)
        
        # 5. Calculate metrics
        metrics = calculate_metrics(grouped_data)
        
        # 6. Format response
        return format_report_response(grouped_data, metrics)
        
    except Exception as e:
        log_error(e)
        return {"error": str(e)}
```

### 2.3 API Endpoints

```python
@app.route('/analytics/api/<module>/trends')
@login_required
def get_trends(module):
    # Get parameters
    params = get_validated_params(request.args)
    
    # Get data
    data = get_report_data(
        store_id=params['store_id'],
        start_date=params['start_date'],
        end_date=params['end_date'],
        group_by=params['group_by'],
        category=params.get('category'),
        asin=params.get('asin')
    )
    
    return jsonify(data)
```

## 3. Module-Specific Implementations

### 3.1 Business Report
- Metrics: Revenue, Orders, Sessions, AOV
- Charts: Revenue Trend, Conversion Rate, Units, Sessions

### 3.2 Advertising Report
- Metrics: Spend, ACOS, CTR, CPC
- Charts: Spend Trend, ACOS Trend, Clicks, Impressions

### 3.3 Inventory Report
- Metrics: Total Stock, Reserved, Available, Reorder Points
- Charts: Stock Level Trend, Reserved vs Available, Reorder Status

### 3.4 Returns Report
- Metrics: Return Rate, Total Returns, Return Value, Top Reasons
- Charts: Return Trend, Return Reasons, Return Value Trend

## 4. JavaScript Implementation

### 4.1 Chart Factory
```javascript
const ChartFactory = {
    createChart(type, context, config) {
        return new Chart(context, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: config.label,
                    data: [],
                    borderColor: config.color,
                    backgroundColor: config.bgColor,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                // ... other options
            }
        });
    }
};
```

### 4.2 Filter Management
```javascript
const FilterManager = {
    defaultFilters: {
        startDate: moment().subtract(30, 'days').format('YYYY-MM-DD'),
        endDate: moment().format('YYYY-MM-DD'),
        groupBy: 'daily',
        category: '',
        asin: ''
    },

    saveFilters(filters) {
        Object.entries(filters).forEach(([key, value]) => {
            localStorage.setItem(`${this.prefix}${key}`, value);
        });
    },

    loadFilters() {
        return {
            startDate: localStorage.getItem(`${this.prefix}StartDate`) || this.defaultFilters.startDate,
            endDate: localStorage.getItem(`${this.prefix}EndDate`) || this.defaultFilters.endDate,
            groupBy: localStorage.getItem(`${this.prefix}GroupBy`) || this.defaultFilters.groupBy,
            category: localStorage.getItem(`${this.prefix}Category`) || this.defaultFilters.category,
            asin: localStorage.getItem(`${this.prefix}Asin`) || this.defaultFilters.asin
        };
    },

    clearFilters() {
        Object.keys(this.defaultFilters).forEach(key => {
            localStorage.removeItem(`${this.prefix}${key}`);
        });
        return this.defaultFilters;
    }
};
```

### 4.3 Data Loading
```javascript
const DataLoader = {
    async loadData(params) {
        try {
            showToast('Loading data...', 'info');
            const response = await fetch(`/analytics/api/${this.module}/trends?${new URLSearchParams(params)}`);
            const data = await response.json();
            
            if (data.error) {
                throw new Error(data.error);
            }
            
            this.updateCharts(data);
            showToast('Data updated successfully', 'success');
            
        } catch (error) {
            showToast(error.message, 'error');
        }
    }
};
```

## 5. Best Practices

### 5.1 Performance Optimization
- Use appropriate indexes on date, store_id, category, and ASIN columns
- Implement query result caching
- Lazy load charts and data
- Use date-based partitioning for large datasets

### 5.2 Error Handling
- Implement comprehensive error logging
- Show user-friendly error messages
- Handle network errors gracefully
- Validate all user inputs

### 5.3 User Experience
- Show loading states during data fetch
- Provide clear feedback for user actions
- Remember user preferences
- Ensure responsive design works on all devices

### 5.4 Code Organization
- Use consistent naming conventions
- Implement modular components
- Follow DRY principles
- Document complex logic
``` 