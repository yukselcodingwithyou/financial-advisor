-- Momentum Features
-- Calculate price momentum indicators for portfolio optimization

SELECT 
    symbol,
    date,
    price,
    -- 1-month momentum
    (price / LAG(price, 21) OVER (PARTITION BY symbol ORDER BY date) - 1) as momentum_1m,
    -- 3-month momentum  
    (price / LAG(price, 63) OVER (PARTITION BY symbol ORDER BY date) - 1) as momentum_3m,
    -- 6-month momentum
    (price / LAG(price, 126) OVER (PARTITION BY symbol ORDER BY date) - 1) as momentum_6m,
    -- 12-month momentum
    (price / LAG(price, 252) OVER (PARTITION BY symbol ORDER BY date) - 1) as momentum_12m,
    -- Risk-adjusted momentum (momentum / volatility)
    (price / LAG(price, 63) OVER (PARTITION BY symbol ORDER BY date) - 1) / 
    NULLIF(STDDEV(price / LAG(price, 1) OVER (PARTITION BY symbol ORDER BY date)) 
           OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 62 PRECEDING AND CURRENT ROW), 0) as risk_adj_momentum_3m,
    -- Momentum acceleration (change in momentum)
    ((price / LAG(price, 63) OVER (PARTITION BY symbol ORDER BY date) - 1) - 
     (LAG(price, 63) / LAG(price, 126) OVER (PARTITION BY symbol ORDER BY date) - 1)) as momentum_acceleration,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('market_data', 'daily_prices') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'
    AND price IS NOT NULL