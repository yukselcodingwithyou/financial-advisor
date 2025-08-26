-- Volatility Feature Calculation
-- This model calculates volatility indicators for financial instruments
-- Volatility measures the degree of variation in trading prices over time

{{ config(materialized='table') }}

WITH price_data AS (
    -- Base price data with daily returns
    SELECT 
        date,
        symbol,
        close_price,
        high_price,
        low_price,
        open_price,
        LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) AS prev_close,
        -- Calculate daily return
        CASE 
            WHEN LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) IS NOT NULL 
            THEN (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)
            ELSE NULL 
        END AS daily_return,
        -- True Range calculation for ATR
        GREATEST(
            high_price - low_price,
            ABS(high_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)),
            ABS(low_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date))
        ) AS true_range
    FROM {{ ref('raw_price_data') }}  -- Reference to source price data table
),

volatility_calculations AS (
    SELECT 
        date,
        symbol,
        close_price,
        high_price,
        low_price,
        open_price,
        daily_return,
        true_range,
        
        -- Rolling standard deviation of returns (volatility measures)
        STDDEV(daily_return) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS volatility_5d,
        
        STDDEV(daily_return) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
        ) AS volatility_10d,
        
        STDDEV(daily_return) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
        ) AS volatility_20d,
        
        STDDEV(daily_return) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS volatility_30d,
        
        -- Average True Range (ATR) - another volatility measure
        AVG(true_range) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 13 PRECEDING AND CURRENT ROW
        ) AS atr_14d,
        
        -- Intraday price range
        (high_price - low_price) / close_price AS daily_range_percent,
        
        -- Historical volatility (annualized)
        STDDEV(daily_return) OVER (
            PARTITION BY symbol 
            ORDER BY date 
            ROWS BETWEEN 251 PRECEDING AND CURRENT ROW
        ) * SQRT(252) AS historical_volatility_annual
        
    FROM price_data
    WHERE daily_return IS NOT NULL
)

SELECT 
    date,
    symbol,
    close_price,
    daily_return,
    true_range,
    
    -- Volatility measures
    volatility_5d,
    volatility_10d,
    volatility_20d,
    volatility_30d,
    
    -- Annualized volatility (multiply by sqrt of trading days)
    volatility_5d * SQRT(252) AS volatility_5d_annualized,
    volatility_10d * SQRT(252) AS volatility_10d_annualized,
    volatility_20d * SQRT(252) AS volatility_20d_annualized,
    volatility_30d * SQRT(252) AS volatility_30d_annualized,
    
    -- Average True Range
    atr_14d,
    atr_14d / close_price AS atr_percent,
    
    -- Daily measures
    daily_range_percent,
    historical_volatility_annual,
    
    -- Volatility classification based on 20-day volatility
    CASE 
        WHEN volatility_20d * SQRT(252) > 0.4 THEN 'Very High'
        WHEN volatility_20d * SQRT(252) > 0.3 THEN 'High'
        WHEN volatility_20d * SQRT(252) > 0.2 THEN 'Moderate'
        WHEN volatility_20d * SQRT(252) > 0.1 THEN 'Low'
        ELSE 'Very Low'
    END AS volatility_classification,
    
    -- Relative volatility (compared to 30-day average)
    CASE 
        WHEN volatility_5d > volatility_30d * 1.5 THEN 'Elevated'
        WHEN volatility_5d < volatility_30d * 0.5 THEN 'Suppressed'
        ELSE 'Normal'
    END AS volatility_regime

FROM volatility_calculations
WHERE date IS NOT NULL
ORDER BY symbol, date