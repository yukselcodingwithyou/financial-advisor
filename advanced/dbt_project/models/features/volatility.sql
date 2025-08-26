{{ config(materialized='table') }}

-- Volatility Feature Model
-- Calculates the standard deviation of daily returns over the last 12 months
-- This helps assess the risk level and price stability of stocks

WITH daily_returns AS (
    SELECT 
        symbol,
        date,
        close_price,
        -- Calculate daily return as percentage change from previous day
        LAG(close_price, 1) OVER (
            PARTITION BY symbol 
            ORDER BY date
        ) AS prev_close_price,
        
        CASE 
            WHEN LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) > 0
            THEN ((close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) / 
                  LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) * 100.0
            ELSE NULL 
        END AS daily_return_pct
    FROM {{ ref('stock_prices') }}
    WHERE date >= CURRENT_DATE - INTERVAL '13 months'  -- Extra month for return calculation
),

volatility_calculations AS (
    SELECT 
        symbol,
        date,
        close_price,
        daily_return_pct,
        
        -- Calculate 12-month rolling standard deviation of daily returns
        STDDEV(daily_return_pct) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW  -- 252 trading days = ~12 months
        ) AS volatility_12m_stddev,
        
        -- Calculate average absolute daily return (alternative volatility measure)
        AVG(ABS(daily_return_pct)) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS avg_abs_return_12m,
        
        -- Count of trading days in calculation window
        COUNT(daily_return_pct) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) AS trading_days_count
    FROM daily_returns
    WHERE daily_return_pct IS NOT NULL
),

volatility_final AS (
    SELECT 
        symbol,
        date,
        close_price,
        daily_return_pct,
        volatility_12m_stddev,
        avg_abs_return_12m,
        trading_days_count,
        
        -- Annualized volatility (multiply by sqrt(252) for trading days)
        volatility_12m_stddev * SQRT(252) AS annualized_volatility,
        
        -- Categorize volatility levels
        CASE 
            WHEN volatility_12m_stddev * SQRT(252) > 40 THEN 'Very High'
            WHEN volatility_12m_stddev * SQRT(252) > 25 THEN 'High'
            WHEN volatility_12m_stddev * SQRT(252) > 15 THEN 'Moderate'
            WHEN volatility_12m_stddev * SQRT(252) > 8 THEN 'Low'
            ELSE 'Very Low'
        END AS volatility_category
    FROM volatility_calculations
    WHERE trading_days_count >= 200  -- Ensure sufficient data for reliable calculation
)

SELECT 
    symbol,
    date,
    close_price,
    daily_return_pct,
    volatility_12m_stddev,
    annualized_volatility,
    avg_abs_return_12m,
    volatility_category,
    trading_days_count,
    -- Add timestamp for data freshness tracking
    CURRENT_TIMESTAMP AS calculated_at
FROM volatility_final
WHERE date >= CURRENT_DATE - INTERVAL '1 month'  -- Only recent data for current analysis
ORDER BY symbol, date DESC