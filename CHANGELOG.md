# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Dark/Light mode toggle support
- Video tutorials in documentation
- Responsive design improvements
- Pre-commit hooks for code quality
- GitHub Actions CI/CD pipeline

### Changed
- Updated Python version to 3.12
- Upgraded dependencies:
  - TailwindCSS to v3.4.1
  - Chart.js to v4.4.1
  - Alpine.js to v3.13.3
  - Flask to v3.0.1
  - SQLAlchemy to v2.0.25
  - Pandas to v2.1.4

### Security
- Implemented JWT token-based authentication
- Added bcrypt password hashing
- Enhanced store access control

## [0.3.0] - 2025-01-23

### Added
- Seasonal Analytics Dashboard
  - Monthly/Quarterly/Weekly trend analysis
  - Peak period detection system
  - Special period analysis (Black Friday, Christmas)
- Performance metrics and KPIs
- Advanced error handling for CSV processing
- Bulk processing support
- Cross-store comparison features

### Changed
- Enhanced documentation structure
- Improved modular architecture
- Optimized database queries
- Updated project structure for better organization

### Fixed
- Dashboard loading time optimizations
- Dark mode UI inconsistencies
- CSV export timeout for large datasets

## [0.2.0] - 2025-01-09

### Added
- Return Report integration
  - CSV upload and validation
  - Return rate calculation
  - Customer feedback tracking
- Inventory Report integration
  - Stock level monitoring
  - Warehouse distribution tracking
  - Reorder point calculation
- Store detail page
  - Performance metrics dashboard
  - Inventory overview
  - Recent activity feed
- User-Store relationship
  - Store-level permissions
  - Access control implementation
  - Auto-incrementing store IDs

### Changed
- Updated CSV validation process
- Improved store management interface
- Enhanced data processing performance

### Fixed
- Store ID validation for user permissions
- CSV format compatibility issues
- Date format handling in reports

## [0.1.0] - 2025-01-08

### Added
- Initial release
- Business Report integration
- Advertising Report integration
- Basic store management
- CSV upload functionality
