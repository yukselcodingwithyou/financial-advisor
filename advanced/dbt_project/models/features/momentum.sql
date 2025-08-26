{{ config(materialized='table') }}

-- Momentum Feature Model
-- Calculates the percentage change in price over the last 12 months
-- This helps identify stocks with strong upward or downward price trends

WITH price_data AS (
    SELECT 
        symbol,
        date,
        close_price,
        -- Get price from 12 months ago (252 trading days approximately)
        LAG(close_price, 252) OVER (
            PARTITION BY symbol 
            ORDER BY date
        ) AS price_12m_ago
    FROM {{ ref('stock_prices') }}
    WHERE date >= CURRENT_DATE - INTERVAL '13 months'  -- Extra month for lag calculation
),

momentum_calculations AS (
    SELECT 
        symbol,
        date,
        close_price,
        price_12m_ago,
        -- Calculate 12-month momentum as percentage change
        CASE 
            WHEN price_12m_ago IS NOT NULL AND price_12m_ago > 0 
            THEN ((close_price - price_12m_ago) / price_12m_ago) * 100.0
            ELSE NULL 
        END AS momentum_12m_pct,
        
        -- Categorize momentum strength
        CASE 
            WHEN ((close_price - price_12m_ago) / price_12m_ago) * 100.0 > 20 THEN 'Strong Positive'
            WHEN ((close_price - price_12m_ago) / price_12m_ago) * 100.0 > 5 THEN 'Moderate Positive'
            WHEN ((close_price - price_12m_ago) / price_12m_ago) * 100.0 > -5 THEN 'Neutral'
            WHEN ((close_price - price_12m_ago) / price_12m_ago) * 100.0 > -20 THEN 'Moderate Negative'
            ELSE 'Strong Negative'
        END AS momentum_category
    FROM price_data
    WHERE price_12m_ago IS NOT NULL
)

SELECT 
    symbol,
    date,
    close_price,
    price_12m_ago,
    momentum_12m_pct,
    momentum_category,
    -- Add timestamp for data freshness tracking
    CURRENT_TIMESTAMP AS calculated_at
FROM momentum_calculations
WHERE date >= CURRENT_DATE - INTERVAL '1 month'  -- Only recent data for current analysis
ORDER BY symbol, date DESC