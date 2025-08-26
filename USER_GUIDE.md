# Financial Advisor - User Guide

This comprehensive guide will help you set up, configure, and use the Financial Advisor framework.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Components Overview](#components-overview)
5. [Development Workflow](#development-workflow)
6. [API Usage](#api-usage)
7. [Data Pipeline](#data-pipeline)
8. [Feature Store](#feature-store)
9. [Troubleshooting](#troubleshooting)

## Prerequisites

Before getting started, ensure you have the following installed:

- Python 3.8 or higher
- Git
- Docker (optional, for containerized deployment)
- PostgreSQL or another supported database

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yukselcodingwithyou/financial-advisor.git
cd financial-advisor
```

### 2. Set Up Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt  # Will be created as development progresses
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/financial_advisor
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### Database Setup

1. Create a PostgreSQL database named `financial_advisor`
2. Run migrations (will be implemented in future updates)
3. Load initial data (if available)

## Components Overview

### 1. FastAPI Application (`advanced/api_fastapi/`)

The main web API that provides endpoints for:
- User authentication and management
- Financial data retrieval
- Recommendation services
- Portfolio analysis

**Key Files:**
- `main.py`: Application entry point
- Future: `routers/`, `models/`, `services/`

### 2. Data Transformation Pipeline (`advanced/dbt_project/`)

Uses dbt to transform raw financial data into analytical features:
- Clean and standardize market data
- Calculate financial indicators
- Create feature sets for machine learning

**Key Files:**
- `models/features/`: Feature engineering models
- Future: `models/staging/`, `models/marts/`

### 3. Feature Store (`advanced/feast_repo/`)

Manages feature serving for machine learning models:
- Store computed features
- Serve features for real-time predictions
- Maintain feature lineage and versioning

**Key Files:**
- `feature_views.py`: Feature view definitions
- Future: `entities.py`, `data_sources.py`

### 4. RAG System (`src/rag/`)

Retrieval-Augmented Generation for intelligent advice:
- Knowledge base management
- Context-aware recommendations
- Natural language processing

## Development Workflow

### 1. Setting Up for Development

```bash
# Install development dependencies
pip install -r requirements-dev.txt  # Will be created

# Set up pre-commit hooks
pre-commit install

# Run tests
pytest
```

### 2. Working with Components

#### API Development
```bash
cd advanced/api_fastapi/
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### Data Pipeline Development
```bash
cd advanced/dbt_project/
dbt run  # Execute transformations
dbt test  # Run data quality tests
```

#### Feature Store Development
```bash
cd advanced/feast_repo/
feast apply  # Deploy feature definitions
feast materialize-incremental $(date -d "1 day ago" -u +%Y-%m-%dT%H:%M:%S)
```

## API Usage

### Authentication

```bash
# Register a new user
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "secure_password"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "secure_password"}'
```

### Getting Recommendations

```bash
# Get portfolio recommendations
curl -X GET "http://localhost:8000/recommendations/portfolio" \
     -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Data Pipeline

### Running Transformations

```bash
# Run all models
dbt run

# Run specific model
dbt run --select features.financial_indicators

# Test data quality
dbt test
```

### Adding New Features

1. Create SQL model in `models/features/`
2. Add tests in `tests/`
3. Update documentation
4. Run and validate

## Feature Store

### Managing Features

```bash
# Apply feature definitions
feast apply

# Get feature values
feast get-online-features \
    --feature-view user_financial_profile \
    --entity user_id=123
```

### Adding New Features

1. Define in `feature_views.py`
2. Apply changes with `feast apply`
3. Materialize historical data
4. Test feature serving

## Troubleshooting

### Common Issues

#### API Won't Start
- Check if port 8000 is available
- Verify database connection
- Check environment variables

#### dbt Errors
- Validate SQL syntax
- Check database permissions
- Verify model dependencies

#### Feature Store Issues
- Ensure Feast server is running
- Check data source connections
- Validate feature definitions

### Getting Help

- Check component-specific documentation
- Review error logs
- Consult the troubleshooting section
- Open an issue on GitHub

## Best Practices

### Code Quality
- Follow PEP 8 style guidelines
- Write comprehensive tests
- Use type hints
- Document complex logic

### Security
- Never commit secrets to version control
- Use environment variables for configuration
- Implement proper authentication
- Validate all inputs

### Performance
- Monitor API response times
- Optimize database queries
- Cache frequently accessed data
- Use async/await for I/O operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

## Support

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review existing discussions

---

**Note**: This framework is under active development. Some features mentioned in this guide will be implemented in future updates. Check the project roadmap for current status and upcoming features.