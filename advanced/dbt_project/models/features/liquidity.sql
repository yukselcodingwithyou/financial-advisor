-- Liquidity Features
-- Trading volume, bid-ask spreads, and market impact measures

SELECT 
    symbol,
    date,
    volume,
    dollar_volume = volume * close_price,
    -- Volume patterns
    volume_ma_20 = AVG(volume) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW),
    volume_ratio = volume / NULLIF(AVG(volume) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW), 0),
    -- Bid-ask spread
    bid_ask_spread = (ask_price - bid_price) / NULLIF(mid_price, 0),
    bid_ask_spread_ma = AVG((ask_price - bid_price) / NULLIF(mid_price, 0)) 
                        OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),
    -- Market impact estimate
    price_impact = ABS(close_price - open_price) / NULLIF(open_price, 0) / (volume / avg_daily_volume),
    -- Amihud illiquidity measure
    amihud_illiquidity = ABS(close_price / LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) - 1) / 
                        NULLIF(dollar_volume / 1000000, 0),  -- Price impact per million dollars
    -- Roll measure (effective spread)
    roll_measure = SQRT(GREATEST(0, 
        -1 * (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) * 
             (LAG(close_price, 1) - LAG(close_price, 2) OVER (PARTITION BY symbol ORDER BY date))
    )),
    -- Liquidity score (higher = more liquid)
    liquidity_score = 
        LEAST(10, GREATEST(0, 
            5 +  -- Base score
            LOG(NULLIF(dollar_volume / 1000000, 0)) -  -- Volume component
            bid_ask_spread * 1000 -  -- Spread penalty
            LEAST(5, amihud_illiquidity * 1000)  -- Illiquidity penalty
        )),
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('market_data', 'daily_prices_detailed') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'
    AND volume > 0
    AND bid_price > 0 
    AND ask_price > bid_price