# Financial Advisor - Beginner's Guide

Welcome to the Financial Advisor project! This guide will help you understand the momentum and volatility features that power our investment decision-making framework.

## What are Momentum and Volatility?

### Momentum 📈
Momentum measures how much a stock's price has changed over a specific period (in our case, 12 months). It helps identify trends:

- **Positive Momentum**: Stock price has increased over the last 12 months
- **Negative Momentum**: Stock price has decreased over the last 12 months

**Why is this useful?**
- Stocks with strong positive momentum often continue to perform well (trend following)
- Helps identify stocks that are gaining investor interest
- Can signal potential buying or selling opportunities

### Volatility 📊
Volatility measures how much a stock's price fluctuates day-to-day. It's calculated using the standard deviation of daily returns over 12 months.

- **High Volatility**: Stock price changes dramatically from day to day
- **Low Volatility**: Stock price changes are small and consistent

**Why is this useful?**
- Helps assess investment risk
- High volatility = higher potential returns but also higher risk
- Low volatility = more stable investment but potentially lower returns

## How Our Models Work

### Momentum Model
```sql
-- Calculates percentage change over 12 months
momentum_12m_pct = ((current_price - price_12m_ago) / price_12m_ago) * 100
```

**Categories:**
- **Strong Positive**: > 20% gain
- **Moderate Positive**: 5% to 20% gain
- **Neutral**: -5% to 5% change
- **Moderate Negative**: -20% to -5% loss
- **Strong Negative**: < -20% loss

### Volatility Model
```sql
-- Calculates standard deviation of daily returns
volatility = STDDEV(daily_returns) over 252 trading days
```

**Categories:**
- **Very High**: > 40% annualized volatility
- **High**: 25% to 40% annualized volatility
- **Moderate**: 15% to 25% annualized volatility
- **Low**: 8% to 15% annualized volatility
- **Very Low**: < 8% annualized volatility

## Investment Decision Examples

### Example 1: Growth Investment Strategy
**Scenario**: Looking for stocks with strong growth potential
**Filter**: 
- Momentum: Strong Positive (> 20%)
- Volatility: Moderate to High (willing to accept risk for growth)

### Example 2: Conservative Investment Strategy
**Scenario**: Looking for stable, low-risk investments
**Filter**:
- Momentum: Moderate Positive to Neutral
- Volatility: Low to Very Low (< 15%)

### Example 3: Value Investment Strategy
**Scenario**: Looking for undervalued stocks that might recover
**Filter**:
- Momentum: Moderate to Strong Negative (price has dropped)
- Volatility: Low to Moderate (company fundamentals still strong)

## Getting Started

1. **Understand Your Risk Tolerance**: 
   - High risk tolerance → Consider higher volatility stocks
   - Low risk tolerance → Focus on lower volatility stocks

2. **Define Your Investment Timeline**:
   - Short-term → Momentum might be more important
   - Long-term → Volatility patterns might be more relevant

3. **Combine with Other Analysis**:
   - These features work best when combined with fundamental analysis
   - Consider company financials, industry trends, and market conditions

## Next Steps

- Read the [User Guide](USER_GUIDE.md) for detailed technical information
- Explore the dbt models in `advanced/dbt_project/models/features/`
- Learn about SQL and data analysis to customize the models for your needs

Remember: **Past performance doesn't guarantee future results.** Always do thorough research before making investment decisions!