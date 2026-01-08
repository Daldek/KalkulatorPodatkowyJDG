# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-01-08

### Added
- Three complementary visualization charts:
  - Grouped bar chart showing first month cost structure by category
  - Line chart for monthly net income over 60 months
  - Line chart for cumulative net income progression
- Detailed monthly breakdown tables for all three tax forms
- Four summary periods instead of two (6, 12, 30, 60 months)

### Fixed
- Health insurance calculations corrected for 2025 regulations:
  - Tax scale: 9% of income (min ~315 PLN/month)
  - Linear tax: 4.9% of income (min ~315 PLN/month)
  - Lump sum: fixed ~554 PLN/month
- Lump sum costs now properly lower gross income without affecting tax calculation

### Changed
- Improved visualization with category-grouped comparisons
- Added explanatory note about costs in lump sum taxation
- Enhanced CSS styling for monthly detail tables

## [1.0.0] - 2026-01-07

### Added

#### Backend
- Complete domain layer with tax calculation logic for 2025
  - Tax scale (12%/32% progressive tax)
  - Linear tax (19% flat tax)
  - Lump sum tax (multiple rates: 2%, 3%, 5.5%, 8.5%, 10%, 12%, 14%, 15%, 17%)
  - Automatic ZUS stage recognition (relief, preferential, full)
  - Health insurance calculations (different for each tax form)
- Services layer for 60-month scenario building
  - Time utilities for month generation and grouping
  - Tax calculator for complete simulations
- FastAPI REST API
  - POST /api/calculate - main calculation endpoint
  - GET /api/tax-rates - available lump sum rates
  - GET /health - health check
  - Complete Pydantic schemas for validation
- 69 unit tests for domain layer (100% coverage of domain logic)
  - ZUS calculations tests
  - Tax scale tests
  - Linear tax tests
  - Lump sum tests
  - Health insurance tests

#### Frontend
- Static HTML5/CSS3/Vanilla JavaScript frontend
- Responsive form for input data
- Chart.js integration for comparison visualization
- Results table with summary
- Mobile-friendly design

#### Documentation
- README.md - complete project documentation
- QUICKSTART.md - 5-minute quick start guide
- IMPLEMENTATION_SUMMARY.md - implementation summary
- ARCHITECTURE.md - architecture details
- PRD.md - product requirements
- RULES.md - immutable project rules
- IMPLEMENTATION_PROMPT.md - implementation specification
- CLAUDE.md - project memory and collaboration rules

#### Examples
- example_request.json - full API request example
- example_response_summary.json - API response example
- test_api.sh - bash script for API testing
- examples/README.md - examples documentation

#### Configuration
- requirements.txt - Python dependencies
- pyproject.toml - modern Python project configuration
- Dockerfile - backend containerization
- .gitignore - git ignore patterns
- .python-version - Python version specification (3.14)
- LICENSE - MIT license with tax disclaimer

### Technical Details

- **Python:** 3.12+
- **Framework:** FastAPI 0.115+
- **Validation:** Pydantic 2.10+
- **Testing:** pytest 8.3+
- **Frontend:** Vanilla JavaScript + Chart.js 4.4+
- **Code:** ~2000 lines (backend) + ~827 lines (tests)
- **Architecture:** Clean/Layered Architecture
- **Financial Precision:** Decimal for all calculations

### Design Principles

- Domain layer with no external dependencies
- Mathematical results over interpretation
- No AI/LLM integration (optional layer for future)
- No financial advice - informational purposes only
- Tax year: 2025 (frozen, no automatic law changes)

---

## [Unreleased]

### Planned for future versions

- Export results to PDF/Excel
- Advanced projections with revenue growth
- Additional tax forms (tax card)
- User accounts and calculation history
- API rate limiting and caching
- Optional AI interpretation layer (following R13)

---

**Note:** Version 1.0.0 represents a complete, production-ready implementation
according to IMPLEMENTATION_PROMPT.md and project rules (RULES.md).
