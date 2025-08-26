# Financial Advisor User Guide

## Overview

This guide provides detailed instructions for using the Financial Decision-Making System, including the implementation and usage of momentum and volatility features.

## System Architecture

The financial advisor system consists of three main components:
- **FastAPI**: For building RESTful APIs
- **DBT**: For data transformation and feature engineering
- **Feast**: For feature storage and serving

## Features

### Momentum Features

The momentum features help identify trends and price movements in financial instruments. Our implementation includes:

#### Available Momentum Indicators:
- **5-day, 10-day, and 20-day Momentum**: Relative price changes over rolling windows
- **Rate of Change (ROC)**: Percentage-based momentum indicators
- **MACD Components**: Moving Average Convergence Divergence indicators
- **Momentum Classification**: Automated categorization (Strong Positive, Moderate Positive, Neutral, Moderate Negative, Strong Negative)

#### Implementation:
The momentum calculations are implemented in `advanced/dbt_project/models/features/momentum.sql` and include:

```sql
-- Example: 20-day momentum calculation
(current_price - price_20_days_ago) / price_20_days_ago
```

#### Usage:
Momentum features are particularly useful for:
- Identifying trending markets
- Timing entry and exit points
- Risk assessment for momentum-based strategies
- Portfolio optimization based on trend strength

### Volatility Features

The volatility features measure the degree of price variation and market risk. Our implementation includes:

#### Available Volatility Indicators:
- **Rolling Standard Deviation**: 5-day, 10-day, 20-day, and 30-day volatility measures
- **Average True Range (ATR)**: Measures market volatility accounting for gaps
- **Annualized Volatility**: Standardized volatility measures for comparison
- **Historical Volatility**: Long-term volatility patterns
- **Volatility Classification**: Automated categorization (Very High, High, Moderate, Low, Very Low)
- **Volatility Regime**: Current volatility state (Elevated, Suppressed, Normal)

#### Implementation:
The volatility calculations are implemented in `advanced/dbt_project/models/features/volatility.sql` and include:

```sql
-- Example: 20-day volatility calculation
STDDEV(daily_return) OVER (
    PARTITION BY symbol 
    ORDER BY date 
    ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
)
```

#### Usage:
Volatility features are essential for:
- Risk management and position sizing
- Options pricing and volatility trading
- Portfolio diversification strategies
- Market regime identification

## Getting Started

### Prerequisites
- Python 3.8+
- DBT Core installed
- Access to financial price data
- Database connection (PostgreSQL, BigQuery, Snowflake, etc.)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yukselcodingwithyou/financial-advisor.git
cd financial-advisor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure DBT profile:
```bash
dbt init
# Configure your database connection in profiles.yml
```

### Running the Feature Pipeline

1. **Set up your data source**: Ensure your raw price data table (`raw_price_data`) contains the following columns:
   - `date`: Trading date
   - `symbol`: Financial instrument identifier
   - `open_price`: Opening price
   - `high_price`: Highest price
   - `low_price`: Lowest price
   - `close_price`: Closing price

2. **Run DBT models**:
```bash
# Navigate to the dbt project directory
cd advanced/dbt_project

# Run all models
dbt run

# Or run specific feature models
dbt run --models momentum
dbt run --models volatility
```

3. **Test the models**:
```bash
dbt test
```

### API Integration

Once the features are calculated, they can be accessed through the FastAPI endpoints:

```python
# Example API usage
import requests

# Get momentum data
response = requests.get("/api/momentum/{symbol}")
momentum_data = response.json()

# Get volatility data
response = requests.get("/api/volatility/{symbol}")
volatility_data = response.json()
```

### Feature Storage with Feast

The calculated features can be stored and served using Feast:

1. **Define feature definitions** in your feature store
2. **Ingest features** from DBT output tables
3. **Serve features** for real-time inference

## Best Practices

### Data Quality
- Ensure data completeness before running calculations
- Handle missing values appropriately
- Validate calculation outputs regularly

### Performance Optimization
- Use appropriate materialization strategies in DBT
- Consider incremental models for large datasets
- Optimize window function performance

### Risk Management
- Always consider multiple timeframes for analysis
- Combine momentum and volatility for comprehensive risk assessment
- Regular backtesting of feature effectiveness

## Troubleshooting

### Common Issues

1. **Missing data errors**: Ensure your source data table exists and has the required columns
2. **Performance issues**: Consider using incremental models or partitioning strategies
3. **Calculation anomalies**: Check for data quality issues in your source data

### Support

For additional support or questions, please refer to the README_FOR_BEGINNERS.md file or create an issue in the repository.

## Advanced Usage

### Custom Momentum Calculations
You can extend the momentum model to include additional indicators:
- Relative Strength Index (RSI)
- Stochastic oscillators
- Custom momentum periods

### Custom Volatility Measures
Additional volatility indicators can be added:
- GARCH models
- Realized volatility
- Implied volatility (if options data available)

### Integration with Machine Learning
These features can be used as inputs for:
- Predictive models
- Anomaly detection
- Portfolio optimization algorithms