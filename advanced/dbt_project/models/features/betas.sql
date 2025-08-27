-- Beta Features
-- Market, sector, and factor betas for risk modeling

SELECT 
    symbol,
    date,
    -- Market beta (vs broad market index)
    market_beta_60d,
    market_beta_252d,
    market_beta_stability = ABS(market_beta_60d - market_beta_252d),
    -- Sector beta  
    sector_beta,
    -- Style factor betas
    value_beta,
    growth_beta,
    momentum_beta,
    quality_beta,
    size_beta,
    low_vol_beta,
    -- Currency beta (for international stocks)
    currency_beta,
    -- Commodity beta
    oil_beta,
    gold_beta,
    -- Downside beta (beta during market stress)
    downside_beta = market_beta_stress,
    beta_asymmetry = downside_beta - market_beta_252d,
    -- Beta-adjusted return
    beta_adjusted_return = daily_return - market_beta_252d * market_return,
    -- Tracking error to market
    tracking_error_252d = STDDEV(daily_return - market_beta_252d * market_return) 
                         OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) * SQRT(252),
    -- R-squared (how much variance explained by market)
    r_squared_252d,
    -- Active share equivalent for single stock
    active_component = SQRT(GREATEST(0, 1 - r_squared_252d)),
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('risk_model', 'factor_exposures') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'