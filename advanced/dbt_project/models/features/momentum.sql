-- Momentum Feature Calculation
-- This model calculates momentum indicators for financial instruments
-- Momentum measures the rate of change in prices over a specified time period

{{ config(materialized='table') }}

WITH price_data AS (
    -- Base price data with daily returns
    SELECT 
        date,
        symbol,
        close_price,
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) AS prev_close,
        -- Calculate daily return
        CASE 
            WHEN LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) IS NOT NULL 
            THEN (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)
            ELSE NULL 
        END AS daily_return
    FROM {{ ref('raw_price_data') }}  -- Reference to source price data table
),

momentum_calculations AS (
    SELECT 
        date,
        symbol,
        close_price,
        daily_return,
        
        -- 5-day momentum (relative price change)
        CASE 
            WHEN LAG(close_price, 5) OVER (PARTITION BY symbol ORDER BY date) IS NOT NULL
            THEN (close_price - LAG(close_price, 5) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 5) OVER (PARTITION BY symbol ORDER BY date)
            ELSE NULL
        END AS momentum_5d,
        
        -- 10-day momentum
        CASE 
            WHEN LAG(close_price, 10) OVER (PARTITION BY symbol ORDER BY date) IS NOT NULL
            THEN (close_price - LAG(close_price, 10) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 10) OVER (PARTITION BY symbol ORDER BY date)
            ELSE NULL
        END AS momentum_10d,
        
        -- 20-day momentum
        CASE 
            WHEN LAG(close_price, 20) OVER (PARTITION BY symbol ORDER BY date) IS NOT NULL
            THEN (close_price - LAG(close_price, 20) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 20) OVER (PARTITION BY symbol ORDER BY date)
            ELSE NULL
        END AS momentum_20d,
        
        -- Moving average convergence divergence (MACD) components
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS ema_12d,
        AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS ema_26d
        
    FROM price_data
)

SELECT 
    date,
    symbol,
    close_price,
    daily_return,
    momentum_5d,
    momentum_10d,
    momentum_20d,
    ema_12d,
    ema_26d,
    (ema_12d - ema_26d) AS macd_line,
    
    -- Rate of Change (ROC) indicators
    momentum_5d * 100 AS roc_5d_percent,
    momentum_10d * 100 AS roc_10d_percent,
    momentum_20d * 100 AS roc_20d_percent,
    
    -- Momentum strength classification
    CASE 
        WHEN momentum_20d > 0.1 THEN 'Strong Positive'
        WHEN momentum_20d > 0.05 THEN 'Moderate Positive'
        WHEN momentum_20d > -0.05 THEN 'Neutral'
        WHEN momentum_20d > -0.1 THEN 'Moderate Negative'
        ELSE 'Strong Negative'
    END AS momentum_classification

FROM momentum_calculations
WHERE date IS NOT NULL
ORDER BY symbol, date