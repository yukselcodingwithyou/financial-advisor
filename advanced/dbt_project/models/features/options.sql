-- Options Features
-- Options-derived signals for volatility and sentiment

SELECT 
    symbol,
    date,
    -- Implied volatility metrics
    iv_30d,
    iv_90d,
    iv_term_structure = iv_90d - iv_30d,
    iv_rank_30d,  -- Percentile rank of current IV vs historical
    iv_percentile_30d,
    -- Volatility smile/skew
    put_skew_25d,  -- 25-delta put IV - ATM IV
    call_skew_25d,  -- 25-delta call IV - ATM IV
    volatility_skew = put_skew_25d - call_skew_25d,
    -- Options flow and positioning
    put_call_ratio_volume,
    put_call_ratio_oi,  -- Open interest
    options_volume_ratio = total_options_volume / NULLIF(avg_daily_volume, 0),
    -- Gamma exposure
    dealer_gamma_exposure,
    total_gamma,
    gamma_flip_level,
    -- Options-based sentiment
    fear_greed_index,
    -- Volatility risk premium
    realized_vol_20d,
    vol_risk_premium = iv_30d - realized_vol_20d,
    -- Expected move (from straddle pricing)
    expected_move_1w,
    expected_move_1m,
    -- Max pain level
    max_pain_level,
    max_pain_distance = (close_price - max_pain_level) / NULLIF(close_price, 0),
    -- Options flow signals
    unusual_options_activity,
    smart_money_flow,
    -- Volatility regime
    CASE 
        WHEN iv_rank_30d > 80 THEN 'high_vol'
        WHEN iv_rank_30d > 50 THEN 'elevated_vol'
        WHEN iv_rank_30d < 20 THEN 'low_vol'
        ELSE 'normal_vol'
    END as volatility_regime,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('options_data', 'options_metrics') }}
WHERE date >= CURRENT_DATE - INTERVAL '1 year'