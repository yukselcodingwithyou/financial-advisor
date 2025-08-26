# Financial Advisor

A comprehensive financial analysis platform that leverages modern data tools to analyze ESG (Environmental, Social, Governance), credit risk, and macroeconomic indicators for informed investment decisions.

## Features

### 🌱 ESG Analysis
- Environmental impact scoring and carbon intensity analysis
- Social responsibility metrics including employee satisfaction
- Governance evaluation with board diversity and transparency measures
- Green leadership identification and sustainability categorization

### 💳 Credit Risk Assessment
- Credit rating analysis and spread monitoring
- Default probability modeling and recovery rate estimation
- Liquidity analysis and leverage categorization
- Comprehensive credit scoring system

### 📊 Macroeconomic Intelligence
- Interest rate and yield curve analysis
- Economic growth phase identification
- Employment and inflation tracking
- Market sentiment and manufacturing activity monitoring

## Architecture

This project uses a modern data stack:

- **[dbt](https://www.getdbt.com/)**: Data transformation and modeling
- **[Feast](https://feast.dev/)**: Feature store for ML and analytics
- **[DuckDB](https://duckdb.org/)**: Local analytics database

## Quick Start

```bash
# Install dependencies
pip install dbt-core dbt-duckdb feast pandas pytest

# Set up dbt models
cd advanced/dbt_project
dbt deps
dbt run --profiles-dir .
dbt test --profiles-dir .

# Set up Feast feature store
cd ../feast_repo
feast apply

# Run tests
cd ../../
pytest tests/
```

## Documentation

- **[Beginner's Guide](README_FOR_BEGINNERS.md)**: New to the project? Start here!
- **[User Guide](USER_GUIDE.md)**: Detailed usage instructions and examples
- **[API Documentation](advanced/feast_repo/feature_views.py)**: Feature definitions and schemas

## Project Structure

```
financial-advisor/
├── advanced/
│   ├── dbt_project/          # dbt data models and transformations
│   │   ├── models/features/  # ESG, credit, and macro indicator models
│   │   ├── dbt_project.yml   # dbt configuration
│   │   └── profiles.yml      # Database connection settings
│   └── feast_repo/           # Feast feature store
│       ├── feature_views.py  # Feature view definitions
│       └── feature_store.yaml # Feast configuration
├── tests/                    # Unit tests
├── README_FOR_BEGINNERS.md   # Getting started guide
└── USER_GUIDE.md            # Detailed user documentation
```

## Sample Data

The system includes sample data for:

**Companies**: Apple (AAPL), Tesla (TSLA), Microsoft (MSFT), Ford (F)
**Countries**: United States (US), European Union (EU), China (CN)

## Use Cases

- **Portfolio ESG Compliance**: Evaluate sustainability of investment portfolios
- **Credit Risk Monitoring**: Track default probabilities and credit health
- **Economic Cycle Analysis**: Time investments based on macroeconomic indicators
- **Sustainable Investing**: Identify companies with strong ESG profiles

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Run the test suite
5. Submit a pull request

## License

This project is open source and available under the MIT License.