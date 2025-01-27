# Development Guide

## Development Environment Setup

### 1. Prerequisites

- Python 3.12+
- pip
- virtualenv
- Git
- Docker (optional, for containerized development)

### 2. Local Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/amazon_seller_support.git
cd amazon_seller_support

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks
pre-commit install

# Initialize database
flask db upgrade
```

### 3. Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_csv_processor.py
```

### 4. Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality. The following hooks are configured:

```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Available hooks
- black: Code formatting
- flake8: Style guide enforcement
- isort: Import sorting
- mypy: Static type checking
- pytest: Unit tests
- pylint: Code analysis
```

Configuration is in `.pre-commit-config.yaml`:

```yaml
repos:
-   repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
    -   id: black
        language_version: python3.12
-   repo: https://github.com/PyCQA/flake8
    rev: 7.0.0
    hooks:
    -   id: flake8
-   repo: https://github.com/PyCQA/isort
    rev: 5.13.2
    hooks:
    -   id: isort
-   repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
    -   id: mypy
        additional_dependencies: [types-all]
-   repo: local
    hooks:
    -   id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

### 5. CI/CD Pipeline

The project uses GitHub Actions for CI/CD. The pipeline includes:

#### Continuous Integration
```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Set up Python 3.12
      uses: actions/setup-python@v5
      with:
        python-version: "3.12"
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    - name: Run pre-commit hooks
      run: |
        pip install pre-commit
        pre-commit run --all-files
    - name: Run tests
      run: |
        pytest --cov=app tests/
    - name: Upload coverage
      uses: codecov/codecov-action@v3

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Security scan
      uses: snyk/actions/python@master
      env:
        SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

#### Continuous Deployment
```yaml
name: CD

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    needs: [test, security]
    steps:
    - uses: actions/checkout@v4
    - name: Build and push Docker image
      uses: docker/build-push-action@v5
      with:
        push: true
        tags: amazon-seller-support:latest
    - name: Deploy to production
      run: |
        # Deploy steps here
        echo "Deploying to production..."
```

## Development Workflow

### 1. Branching Strategy

- `main`: Production-ready code
- `develop`: Development branch
- Feature branches: `feature/feature-name`
- Bugfix branches: `bugfix/bug-description`
- Release branches: `release/version-number`

### 2. Commit Messages

Follow conventional commits:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Maintenance tasks

Example:

```
feat(csv): add support for advertising reports
```

### 3. Pull Request Process

1. Create feature branch
2. Implement changes
3. Write/update tests
4. Update documentation
5. Create pull request
6. Code review
7. Merge to develop

## Project Structure

### 1. Code Organization

```
app/
├── models/          # Database models
├── routes/          # Route handlers
├── utils/           # Utility functions
├── services/        # Business logic
└── templates/       # Jinja2 templates
```

### 2. Important Files

- `config.py`: Configuration settings
- `requirements.txt`: Python dependencies
- `.env`: Environment variables
- `.gitignore`: Git ignore rules

## Testing

### 1. Test Structure

```
tests/
├── conftest.py          # Test fixtures
├── test_models.py       # Model tests
├── test_routes.py       # Route tests
└── test_utils.py        # Utility tests
```

### 2. Test Data

Test data is stored in:

```
tests/test_data/
├── business_report.csv
├── inventory_report.csv
├── advertising_report.csv
└── return_report.csv
```

## Documentation

### 1. Code Documentation

- Use docstrings for classes and functions
- Follow Google Python Style Guide
- Keep docstrings up to date

Example:

```python
def analyze_sales_trends(self, store_id: int, date_range: tuple) -> dict:
    """Analyzes sales trends for a given store and date range.

    Args:
        store_id (int): The store ID to analyze
        date_range (tuple): Start and end dates (start_date, end_date)

    Returns:
        dict: Sales trend analysis results
    """
```

### 2. API Documentation

- Keep api.md updated
- Document all endpoints
- Include request/response examples

### 3. User Documentation

- Update user_guide.md
- Include screenshots
- Provide examples

## Seasonal Analytics Development

### Overview

The seasonal analytics engine provides tools for analyzing sales patterns and trends across different time periods. It supports:

- Weekly, monthly, and quarterly analysis
- Special period analysis (e.g., Black Friday, Christmas)
- Growth pattern detection
- Year-over-year comparisons

### Key Components

#### Peak Detection

The peak detection algorithm uses two criteria:

1. Local Significance: A period is a local peak if it's 10% higher than both its previous and next periods
2. Global Significance: A period is globally significant if it's 10% higher than the yearly average

A period is considered a seasonal peak if it meets either criterion.

#### Special Period Analysis

Special periods (like Black Friday and Christmas) are analyzed by:

1. Comparing with the same period in previous years
2. Calculating growth rates and significance
3. Identifying consistent patterns across years

#### Test Data Generation

When writing tests, use the `sample_data` fixture which provides:

- 2 years of daily data
- Seasonal variations (summer increase, holiday spikes)
- Weekend variations
- Realistic growth patterns

### Development Guidelines

#### Adding New Analytics

1. Define the analysis method in `AnalyticsEngine`
2. Add appropriate test cases in `test_seasonal_analytics.py`
3. Update the sample data fixture if needed
4. Document the new functionality

#### Modifying Existing Analytics

1. Ensure backwards compatibility
2. Update test cases to cover new scenarios
3. Verify all existing tests pass
4. Update documentation

#### Testing

Run the test suite with:

```bash
pytest -v tests/test_seasonal_analytics.py
```

Key test files:

- `test_seasonal_analytics.py`: Main test suite
- `conftest.py`: Test fixtures and utilities

## Deployment

### 1. Development

```bash
flask run --debug
```

### 2. Production

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app()"
```

### 3. Environment Variables

Required environment variables:

```
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=postgresql://user:pass@localhost/dbname
SECRET_KEY=your-secret-key
```

## Performance Considerations

### 1. Database

- Use appropriate indexes
- Optimize queries
- Use batch processing for large datasets

### 2. Caching

- Implement Redis caching
- Cache expensive calculations
- Cache API responses

### 3. CSV Processing

- Process large files in chunks
- Use background tasks
- Implement progress tracking
