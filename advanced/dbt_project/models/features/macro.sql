-- Macro Economic Signals
-- Calculate macro indicators for regime detection and factor tilts

SELECT 
    date,
    -- Interest rate environment
    fed_funds_rate,
    ten_year_yield,
    yield_curve_slope = ten_year_yield - two_year_yield,
    -- Volatility regime
    vix_level,
    vix_term_structure = vix_9d - vix_level,
    -- Credit conditions
    credit_spread_ig,
    credit_spread_hy,
    credit_spread_widening = credit_spread_ig - LAG(credit_spread_ig, 21) OVER (ORDER BY date),
    -- Currency strength
    dollar_index,
    dollar_momentum = (dollar_index / LAG(dollar_index, 63) OVER (ORDER BY date) - 1),
    -- Commodity signals
    oil_price,
    gold_price,
    copper_price,
    commodity_momentum = (oil_price / LAG(oil_price, 21) OVER (ORDER BY date) - 1),
    -- Economic surprise index
    economic_surprise_index,
    -- Regime classification
    CASE 
        WHEN vix_level > 25 AND credit_spread_ig > 1.5 THEN 'crisis'
        WHEN vix_level > 20 OR credit_spread_ig > 1.2 THEN 'high_vol'
        WHEN vix_level < 12 AND credit_spread_ig < 0.8 THEN 'low_vol'
        ELSE 'normal'
    END as volatility_regime,
    CASE
        WHEN yield_curve_slope < 0 THEN 'inverted'
        WHEN yield_curve_slope < 1 THEN 'flat'
        WHEN yield_curve_slope > 2 THEN 'steep'
        ELSE 'normal'
    END as yield_curve_regime,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('macro_data', 'daily_indicators') }}
WHERE date >= CURRENT_DATE - INTERVAL '5 years'