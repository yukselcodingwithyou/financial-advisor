# Financial Advisor - User Guide

This guide provides detailed technical information about the momentum and volatility feature models in our financial decision-making framework.

## Architecture Overview

The financial advisor system uses dbt (data build tool) to transform raw stock price data into actionable investment features. The models are located in `advanced/dbt_project/models/features/`.

## Feature Models

### Momentum Model (`momentum.sql`)

**Purpose**: Calculate 12-month price momentum to identify trending stocks.

**Input Data Requirements**:
- Table: `stock_prices` (referenced as `{{ ref('stock_prices') }}`)
- Required columns:
  - `symbol`: Stock ticker symbol
  - `date`: Trading date
  - `close_price`: Stock closing price

**Calculations**:
1. **12-Month Lag**: Uses `LAG(close_price, 252)` to get price from ~12 months ago (252 trading days)
2. **Momentum Percentage**: `((current_price - price_12m_ago) / price_12m_ago) * 100`
3. **Categorization**: Assigns momentum strength categories

**Output Columns**:
- `symbol`: Stock ticker
- `date`: Trading date
- `close_price`: Current closing price
- `price_12m_ago`: Price from 12 months ago
- `momentum_12m_pct`: Percentage change over 12 months
- `momentum_category`: Categorical momentum strength
- `calculated_at`: Timestamp of calculation

**Momentum Categories**:
```sql
Strong Positive: > 20%
Moderate Positive: 5% to 20%
Neutral: -5% to 5%
Moderate Negative: -20% to -5%
Strong Negative: < -20%
```

### Volatility Model (`volatility.sql`)

**Purpose**: Calculate price volatility using standard deviation of daily returns over 12 months.

**Input Data Requirements**:
- Table: `stock_prices` (referenced as `{{ ref('stock_prices') }}`)
- Same column requirements as momentum model

**Calculations**:
1. **Daily Returns**: `((close_price - prev_close_price) / prev_close_price) * 100`
2. **Rolling Standard Deviation**: 252-day rolling window of daily returns
3. **Annualized Volatility**: `volatility_12m_stddev * SQRT(252)`
4. **Alternative Measures**: Average absolute daily return

**Output Columns**:
- `symbol`: Stock ticker
- `date`: Trading date
- `close_price`: Current closing price
- `daily_return_pct`: Daily percentage return
- `volatility_12m_stddev`: 12-month rolling standard deviation
- `annualized_volatility`: Annualized volatility percentage
- `avg_abs_return_12m`: Average absolute daily return
- `volatility_category`: Categorical volatility level
- `trading_days_count`: Number of trading days in calculation
- `calculated_at`: Timestamp of calculation

**Volatility Categories**:
```sql
Very High: > 40% annualized
High: 25% to 40% annualized
Moderate: 15% to 25% annualized
Low: 8% to 15% annualized
Very Low: < 8% annualized
```

## dbt Configuration

### Project Structure
```
advanced/dbt_project/
├── dbt_project.yml          # dbt configuration
└── models/
    └── features/
        ├── momentum.sql      # Momentum feature model
        └── volatility.sql    # Volatility feature model
```

### Model Configuration
Both models are configured with:
- **Materialization**: `table` for fast query performance
- **Enabled**: `true` for active use
- **Dependencies**: Both reference `stock_prices` source table

## Usage Examples

### Running the Models
```bash
# Navigate to dbt project directory
cd advanced/dbt_project/

# Run all models
dbt run

# Run specific model
dbt run --select momentum
dbt run --select volatility

# Test models
dbt test
```

### Querying Results

**Find High-Momentum Stocks**:
```sql
SELECT symbol, momentum_12m_pct, momentum_category
FROM momentum
WHERE momentum_category IN ('Strong Positive', 'Moderate Positive')
ORDER BY momentum_12m_pct DESC;
```

**Find Low-Volatility Stocks**:
```sql
SELECT symbol, annualized_volatility, volatility_category
FROM volatility
WHERE volatility_category IN ('Low', 'Very Low')
ORDER BY annualized_volatility ASC;
```

**Combined Analysis**:
```sql
SELECT 
    m.symbol,
    m.momentum_12m_pct,
    v.annualized_volatility,
    m.momentum_category,
    v.volatility_category
FROM momentum m
JOIN volatility v ON m.symbol = v.symbol AND m.date = v.date
WHERE m.momentum_category = 'Strong Positive'
  AND v.volatility_category IN ('Low', 'Moderate')
ORDER BY m.momentum_12m_pct DESC;
```

## Investment Decision Framework

### Risk-Return Analysis
Use momentum and volatility together to categorize investments:

| Momentum | Volatility | Investment Type | Risk Level |
|----------|------------|----------------|------------|
| Strong Positive | Low | Growth with Safety | Medium |
| Strong Positive | High | High Growth | High |
| Moderate Positive | Low | Steady Growth | Low-Medium |
| Neutral | Very Low | Defensive | Low |
| Negative | Low | Value Play | Medium |

### Portfolio Construction
1. **Core Holdings**: Low volatility, moderate positive momentum
2. **Growth Allocation**: High momentum, accept higher volatility
3. **Defensive Allocation**: Very low volatility, neutral momentum
4. **Value Opportunities**: Negative momentum, low volatility (if fundamentals support)

## Data Quality Considerations

### Minimum Data Requirements
- **Momentum**: Requires 252+ trading days of price history
- **Volatility**: Requires 200+ trading days for reliable calculation

### Data Freshness
- Models filter for recent data (last month) in final output
- `calculated_at` timestamp tracks when features were computed

### Handling Edge Cases
- Models handle missing data with NULL checks
- Division by zero protection in percentage calculations
- Sufficient data validation before calculations

## Customization Options

### Adjusting Time Windows
```sql
-- Change momentum period (currently 252 days = ~12 months)
LAG(close_price, 126) -- 6 months
LAG(close_price, 504) -- 24 months

-- Change volatility window
ROWS BETWEEN 125 PRECEDING AND CURRENT ROW -- 6 months
ROWS BETWEEN 503 PRECEDING AND CURRENT ROW -- 24 months
```

### Modifying Categories
Edit the CASE statements in both models to adjust thresholds:
```sql
-- Example: More conservative momentum categories
WHEN momentum_12m_pct > 15 THEN 'Strong Positive'  -- was 20
WHEN momentum_12m_pct > 3 THEN 'Moderate Positive' -- was 5
```

## Performance Optimization

### Indexing Recommendations
For optimal performance, ensure your `stock_prices` table has indexes on:
- `(symbol, date)` - For window functions
- `date` - For date filtering

### Materialization Strategy
- Models use `table` materialization for fast querying
- Consider `incremental` materialization for large datasets
- Use `view` materialization during development/testing

## Troubleshooting

### Common Issues
1. **No Results**: Check if `stock_prices` table exists and has data
2. **Performance Issues**: Verify indexes on `stock_prices` table
3. **Null Values**: Ensure sufficient historical data (12+ months)

### Validation Queries
```sql
-- Check data availability
SELECT COUNT(*), MIN(date), MAX(date) FROM stock_prices;

-- Verify calculation results
SELECT symbol, COUNT(*) as days, 
       MIN(momentum_12m_pct) as min_momentum,
       MAX(momentum_12m_pct) as max_momentum
FROM momentum 
GROUP BY symbol;
```

## Integration with Other Systems

The momentum and volatility features can be integrated with:
- Portfolio optimization algorithms
- Risk management systems
- Automated trading strategies
- Investment research platforms
- Financial reporting dashboards

For more information on integration patterns, consult your data engineering team or system administrator.