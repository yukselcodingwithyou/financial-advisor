# Financial Advisor dbt Project

This dbt project contains feature models for financial analysis, specifically momentum and volatility calculations.

## Project Structure

```
advanced/dbt_project/
├── dbt_project.yml          # Project configuration
├── profiles.yml.example     # Database connection example
└── models/
    └── features/
        ├── momentum.sql      # 12-month momentum feature
        ├── volatility.sql    # 12-month volatility feature
        └── schema.yml        # Model documentation and tests
```

## Prerequisites

1. **dbt installed**: Install dbt with your database adapter
   ```bash
   pip install dbt-postgres  # or dbt-snowflake, dbt-bigquery, etc.
   ```

2. **Database connection**: Configure `~/.dbt/profiles.yml` based on `profiles.yml.example`

3. **Source data**: Ensure you have a `stock_prices` table with columns:
   - `symbol` (text): Stock ticker symbol
   - `date` (date): Trading date
   - `close_price` (numeric): Closing price

## Quick Start

1. **Navigate to project directory**:
   ```bash
   cd advanced/dbt_project/
   ```

2. **Check dbt connection**:
   ```bash
   dbt debug
   ```

3. **Run the models**:
   ```bash
   dbt run
   ```

4. **Run tests**:
   ```bash
   dbt test
   ```

5. **Generate documentation**:
   ```bash
   dbt docs generate
   dbt docs serve
   ```

## Model Descriptions

### momentum.sql
- **Purpose**: Calculate 12-month price momentum
- **Output**: Percentage change and categorical momentum strength
- **Use case**: Identify trending stocks for momentum-based strategies

### volatility.sql
- **Purpose**: Calculate 12-month price volatility
- **Output**: Standard deviation of returns and risk categories
- **Use case**: Assess investment risk and portfolio construction

## Customization

- **Time periods**: Modify LAG and window functions in SQL models
- **Categories**: Adjust CASE statement thresholds
- **Materialization**: Change from 'table' to 'view' or 'incremental' in model configs

## Support

For detailed usage instructions, see:
- [User Guide](../../USER_GUIDE.md)
- [Beginner's Guide](../../README_FOR_BEGINNERS.md)