# AMAZON SELLER CSV ANALYZER

[![Build Status](https://github.com/yourusername/amazon-seller-support/workflows/CI/badge.svg)](https://github.com/yourusername/amazon-seller-support/actions)
[![Test Coverage](https://codecov.io/gh/yourusername/amazon-seller-support/branch/main/graph/badge.svg)](https://codecov.io/gh/yourusername/amazon-seller-support)
[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

A powerful analytics platform for Amazon sellers to process CSV reports and gain valuable insights about their business performance. This application transforms raw data into visual insights, making your Amazon store more understandable and actionable.

## Features

- **Secure Authentication:**
  - JWT token-based authentication
  - Bcrypt password hashing
  - Multi-store access control

- **CSV File Processing:**
  - Business Reports, Inventory Reports
  - Advanced validation and error handling
  - Bulk processing support

- **Analytics & Dashboards:**
  - Sales and Inventory Analytics
  - Performance Metrics & KPIs
  - Seasonal Analytics with trend detection
  - Dark/Light mode support

- **Multi-Store Support:**
  - Multiple store management
  - Store-specific analytics
  - Cross-store comparisons

## Tech Stack

- **Frontend:**
  - TailwindCSS v3.4.1
  - Chart.js v4.4.1
  - Alpine.js v3.13.3
  - Responsive Design

- **Backend:**
  - Python 3.12
  - Flask v3.0.1
  - SQLAlchemy v2.0.25
  - Pandas v2.1.4

## Installation

### Prerequisites
- Python 3.12+
- Node.js 18+
- pip
- virtualenv (recommended)

### Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/amazon_seller_support.git
cd amazon_seller_support

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Initialize database
flask db upgrade

# Run the application
flask run
```

## Development

### Testing
```bash
# Run all tests (80%+ coverage required)
pytest --cov=app tests/

# Run specific module tests
pytest tests/modules/advertisement/
```

### Code Quality
```bash
# Run pre-commit hooks
pre-commit run --all-files

# Run linters
flake8
black .
eslint .
```

## Modules

1. **Advertisement**
   - Analyze Amazon ad campaign performance.
   - Visualize ROI, CTR, CPC, and more.

2. **Business**
   - Analyze sales trends in your Amazon store.
   - Visualize revenue, orders, and conversion rates.

3. **Inventory**
   - Track stock levels and product sales frequency.
   - Manage reordering and inventory health.

4. **Return**
   - Monitor and analyze product returns.
   - Identify return reasons and optimize processes.

## Project Structure

```
amazon_seller_support.v1/
├── app/                            # Main application folder
│   ├── __init__.py                # Application initialization
│   ├── models.py                  # Shared models
│   ├── core/                      # Core utilities and database logic
│   │   ├── __init__.py
│   │   ├── database.py           # Database configuration
│   │   ├── auth.py              # Authentication logic
│   │   └── utils.py             # Utility functions
│   ├── modules/                   # Modular components
│   │   ├── advertisement/        # Advertisement module
│   │   │   ├── __init__.py
│   │   │   ├── models.py        # Advertisement-specific models
│   │   │   ├── routes.py        # Advertisement routes
│   │   │   ├── services.py      # Business logic
│   │   │   └── templates/       # Module-specific templates
│   │   ├── business/            # Business module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   ├── services.py
│   │   │   └── templates/
│   │   ├── inventory/           # Inventory module
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   ├── services.py
│   │   │   └── templates/
│   │   └── return/             # Return module
│   │       ├── __init__.py
│   │       ├── models.py
│   │       ├── routes.py
│   │       ├── services.py
│   │       └── templates/
│   ├── templates/               # Global templates
│   │   ├── base.html           # Base template
│   │   ├── base_tailwind.html  # Tailwind base template
│   │   ├── dashboard.html      # Main dashboard
│   │   ├── index.html         # Landing page
│   │   ├── analytics/         # Analytics templates
│   │   │   ├── dashboard.html
│   │   │   └── advertisement_report.html
│   │   ├── auth/             # Authentication templates
│   │   ├── components/       # Reusable components
│   │   │   ├── footer.html
│   │   │   ├── header.html
│   │   │   ├── sidebar.html
│   │   │   └── user_menu.html
│   │   ├── csv/             # CSV upload templates
│   │   ├── includes/        # Partial templates
│   │   └── settings/        # Settings templates
│   ├── static/              # Static assets
│   │   ├── css/            # Stylesheets
│   │   ├── js/             # JavaScript files
│   │   └── images/         # Image assets
│   ├── utils/              # Utility modules
│   ├── services/           # Shared services
│   ├── data/              # Static data files
│   └── uploads/           # Uploaded CSV files
├── docs/                  # Documentation
│   ├── api.md            # API documentation
│   ├── technical.md      # Technical documentation
│   └── user_guide.md     # User guide
├── tests/                # Test suite
│   ├── __init__.py
│   ├── conftest.py      # Test configuration
│   └── modules/         # Module-specific tests
│       ├── advertisement/
│       ├── business/
│       ├── inventory/
│       └── return/
├── instance/            # Instance-specific files
│   └── app.db          # SQLite database
├── migrations/         # Database migrations
├── scripts/           # Utility scripts
├── uploads/          # Temporary upload directory
├── .gitignore       # Git ignore file
├── .prettierrc.cjs  # Prettier configuration
├── analytics.py     # Analytics engine
├── CHANGELOG.md     # Change log
├── eslint.config.js # ESLint configuration
├── package.json    # Node.js dependencies
├── readme.md      # This file
├── requirements.txt # Python dependencies
├── run.py         # Application entry point
├── setup.py      # Package setup
├── tailwind.config.js # Tailwind configuration
└── update_preferences.py # User preferences updater

## Design Principles

### UI/UX Guidelines
- Minimal and functional design
- Fully responsive layout
- WCAG 2.1 accessibility standards compliant
- Dark/Light mode support with consistent color palette
- Modern typography
- Modular CSS architecture

### Database Schema
- Users: Store user information and preferences
- Stores: Amazon store details and credentials
- Products: Product catalog and metadata
- Sales: Sales history and metrics
- Inventory: Stock levels and history

### CSV File Structures
- Business Reports: Sales and revenue data
- Inventory Reports: Stock levels and history
- Order History: Detailed order information

## Project Status

### Completed Features
- Core system architecture
- Database models and migrations
- User interface improvements
- CSV processing services
- Authentication system
- Store management
- Report management (Business, Advertising, Inventory, Return)

### In Progress
- Advanced analytics features
- Frontend test coverage improvements
- Video tutorials and documentation

### Next Steps
- Machine learning predictions
- Mobile application development
- Additional marketplace support

## Security

Please see our [Security Policy](SECURITY.md) for reporting vulnerabilities.

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Documentation

- [API Documentation](docs/api.md)
- [Technical Guide](docs/technical.md)
- [User Guide](docs/user_guide.md)
- [Video Tutorials](docs/tutorials)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Flask Framework
- TailwindCSS
- Chart.js
- Alpine.js
- All our [contributors](CONTRIBUTORS.md)