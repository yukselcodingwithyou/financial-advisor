# Investment Decision Examples

This document provides practical examples of how to use the momentum and volatility features for investment decision-making.

## Example Queries

### 1. High-Growth Investment Strategy
Find stocks with strong positive momentum and moderate to high volatility (accepting risk for growth potential):

```sql
SELECT 
    m.symbol,
    m.close_price,
    m.momentum_12m_pct,
    v.annualized_volatility,
    m.momentum_category,
    v.volatility_category
FROM momentum m
JOIN volatility v ON m.symbol = v.symbol AND m.date = v.date
WHERE m.momentum_category IN ('Strong Positive', 'Moderate Positive')
  AND v.volatility_category IN ('Moderate', 'High')
ORDER BY m.momentum_12m_pct DESC
LIMIT 20;
```

**Expected Results**: Stocks with 5%+ price gains and 15%+ volatility for growth-focused portfolios.

### 2. Conservative Investment Strategy
Find stable stocks with low volatility and neutral to positive momentum:

```sql
SELECT 
    m.symbol,
    m.close_price,
    m.momentum_12m_pct,
    v.annualized_volatility,
    m.momentum_category,
    v.volatility_category
FROM momentum m
JOIN volatility v ON m.symbol = v.symbol AND m.date = v.date
WHERE v.volatility_category IN ('Low', 'Very Low')
  AND m.momentum_category IN ('Moderate Positive', 'Neutral')
ORDER BY v.annualized_volatility ASC
LIMIT 20;
```

**Expected Results**: Stable stocks with <15% volatility for conservative portfolios.

### 3. Value Investment Opportunities
Find potentially undervalued stocks with negative momentum but low volatility (suggesting fundamental strength):

```sql
SELECT 
    m.symbol,
    m.close_price,
    m.momentum_12m_pct,
    v.annualized_volatility,
    m.momentum_category,
    v.volatility_category
FROM momentum m
JOIN volatility v ON m.symbol = v.symbol AND m.date = v.date
WHERE m.momentum_category IN ('Moderate Negative', 'Strong Negative')
  AND v.volatility_category IN ('Low', 'Moderate')
  AND m.momentum_12m_pct > -30  -- Not too extreme losses
ORDER BY m.momentum_12m_pct ASC
LIMIT 20;
```

**Expected Results**: Stocks with recent price declines but stable volatility patterns.

### 4. Risk Assessment Dashboard
Create a comprehensive risk-return profile for portfolio analysis:

```sql
SELECT 
    m.symbol,
    m.momentum_12m_pct,
    v.annualized_volatility,
    
    -- Risk-adjusted return approximation
    CASE 
        WHEN v.annualized_volatility > 0 
        THEN m.momentum_12m_pct / v.annualized_volatility 
        ELSE NULL 
    END AS risk_adjusted_return,
    
    -- Investment recommendation
    CASE 
        WHEN m.momentum_category IN ('Strong Positive', 'Moderate Positive') 
             AND v.volatility_category IN ('Low', 'Moderate') 
        THEN 'BUY - Growth with Low Risk'
        
        WHEN m.momentum_category = 'Strong Positive' 
             AND v.volatility_category IN ('High', 'Very High') 
        THEN 'SPECULATIVE - High Risk/Reward'
        
        WHEN m.momentum_category = 'Neutral' 
             AND v.volatility_category IN ('Low', 'Very Low') 
        THEN 'HOLD - Defensive'
        
        WHEN m.momentum_category IN ('Moderate Negative', 'Strong Negative') 
             AND v.volatility_category IN ('Low', 'Moderate') 
        THEN 'VALUE - Potential Opportunity'
        
        ELSE 'AVOID - High Risk/Poor Performance'
    END AS investment_recommendation,
    
    m.momentum_category,
    v.volatility_category
FROM momentum m
JOIN volatility v ON m.symbol = v.symbol AND m.date = v.date
ORDER BY 
    CASE 
        WHEN v.annualized_volatility > 0 
        THEN m.momentum_12m_pct / v.annualized_volatility 
        ELSE -999 
    END DESC;
```

## Portfolio Construction Guidelines

### Core Portfolio Allocation (60-70%)
**Target**: Stable growth with moderate risk
- Momentum: Moderate Positive to Strong Positive
- Volatility: Low to Moderate (8-25%)
- Expected return: 5-15% annually

### Growth Allocation (15-25%)
**Target**: High growth potential with higher risk acceptance
- Momentum: Strong Positive (>20%)
- Volatility: Moderate to High (15-40%)
- Expected return: 15-30% annually (higher variance)

### Defensive Allocation (10-15%)
**Target**: Capital preservation and stability
- Momentum: Neutral to Moderate Positive
- Volatility: Very Low to Low (<15%)
- Expected return: 0-8% annually

### Opportunistic Allocation (5-10%)
**Target**: Value plays and contrarian investments
- Momentum: Negative (but not extreme)
- Volatility: Low to Moderate
- Expected return: Variable (potential for significant upside)

## Real-World Application Example

**Scenario**: Building a $100,000 portfolio for a moderate-risk investor

1. **Core Holdings ($65,000)**:
   ```sql
   -- Select top 8-10 stocks
   SELECT symbol FROM momentum_volatility_combined 
   WHERE momentum_category = 'Moderate Positive' 
     AND volatility_category IN ('Low', 'Moderate')
   ORDER BY risk_adjusted_return DESC LIMIT 10;
   ```

2. **Growth Holdings ($20,000)**:
   ```sql
   -- Select top 3-5 high-momentum stocks
   SELECT symbol FROM momentum_volatility_combined 
   WHERE momentum_category = 'Strong Positive'
   ORDER BY momentum_12m_pct DESC LIMIT 5;
   ```

3. **Defensive Holdings ($10,000)**:
   ```sql
   -- Select ultra-low volatility stocks
   SELECT symbol FROM momentum_volatility_combined 
   WHERE volatility_category = 'Very Low'
     AND momentum_category != 'Strong Negative'
   ORDER BY annualized_volatility ASC LIMIT 3;
   ```

4. **Opportunistic Holdings ($5,000)**:
   ```sql
   -- Select potential value plays
   SELECT symbol FROM momentum_volatility_combined 
   WHERE momentum_category = 'Moderate Negative'
     AND volatility_category = 'Low'
     AND momentum_12m_pct > -20
   ORDER BY momentum_12m_pct ASC LIMIT 2;
   ```

## Monitoring and Rebalancing

### Monthly Review
- Update momentum and volatility calculations
- Check for category changes in existing holdings
- Identify new opportunities in each allocation bucket

### Quarterly Rebalancing
- Sell holdings that no longer meet criteria
- Reallocate proceeds to maintain target allocations
- Add new positions based on updated analysis

### Risk Management Rules
- Maximum single position: 5% of portfolio
- Maximum sector concentration: 20% of portfolio
- Stop-loss for individual positions: -15% from purchase price
- Profit-taking for high performers: Consider selling 25-50% at +50% gains

This framework provides a systematic approach to using momentum and volatility features for practical investment decision-making.