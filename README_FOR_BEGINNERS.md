# Financial Advisor - Beginner's Guide

## Overview

Welcome to the Financial Advisor project! This is a modern data-driven financial analysis platform that helps make informed investment decisions by analyzing ESG (Environmental, Social, Governance), credit risk, and macroeconomic indicators.

## What is this project?

This financial advisor system uses cutting-edge data tools to:

- **Analyze ESG Factors**: Evaluate companies based on their environmental impact, social responsibility, and governance practices
- **Assess Credit Risk**: Monitor credit ratings, debt levels, and default probabilities
- **Track Economic Indicators**: Follow macroeconomic trends that affect investment decisions

## Architecture

Our system uses two main components:

### 1. dbt (Data Build Tool)
- **Purpose**: Transforms raw financial data into clean, analysis-ready features
- **Location**: `advanced/dbt_project/`
- **What it does**: Takes financial data and creates structured tables with calculated indicators

### 2. Feast (Feature Store)
- **Purpose**: Serves features to machine learning models and applications
- **Location**: `advanced/feast_repo/`
- **What it does**: Provides fast access to features for real-time financial analysis

## Key Features

### ESG Indicators
- Environmental scores (carbon footprint, renewable energy usage)
- Social scores (employee satisfaction, diversity metrics)
- Governance scores (board composition, transparency)
- Overall ESG ratings and categorizations

### Credit Indicators
- Credit ratings and spreads
- Debt-to-equity ratios
- Default probability assessments
- Liquidity and leverage analysis

### Macro Indicators
- Interest rates and yield curves
- Inflation and unemployment rates
- GDP growth and economic phases
- Market indices and commodity prices

## Getting Started

### Prerequisites
- Python 3.8+
- dbt-core
- feast
- duckdb (for local development)

### Quick Start

1. **Set up the environment**:
   ```bash
   pip install dbt-core dbt-duckdb feast pandas pytest
   ```

2. **Run dbt models**:
   ```bash
   cd advanced/dbt_project
   dbt deps
   dbt run
   dbt test
   ```

3. **Set up Feast**:
   ```bash
   cd advanced/feast_repo
   feast apply
   ```

4. **Run tests**:
   ```bash
   cd ../../
   pytest tests/
   ```

## Understanding the Data

### Sample Companies
- **AAPL (Apple)**: High ESG, excellent credit rating
- **TSLA (Tesla)**: Very high environmental score, moderate credit
- **MSFT (Microsoft)**: Well-balanced across all metrics

### Sample Countries
- **US**: Current economic indicators and market data
- **EU**: European economic environment
- **CN**: Chinese economic indicators

## Next Steps

1. Review the [User Guide](USER_GUIDE.md) for detailed usage instructions
2. Explore the dbt models in `advanced/dbt_project/models/features/`
3. Check out the Feast feature definitions in `advanced/feast_repo/feature_views.py`
4. Run the example queries and tests to understand the data flow

## Common Use Cases

- **Portfolio Analysis**: Assess ESG compliance of investment portfolios
- **Risk Management**: Monitor credit risk across holdings
- **Market Timing**: Use macro indicators for investment timing decisions
- **Sustainable Investing**: Focus on companies with high ESG scores

## Need Help?

- Check the detailed [User Guide](USER_GUIDE.md)
- Review the test files to understand expected behavior
- Look at the SQL models to understand data transformations