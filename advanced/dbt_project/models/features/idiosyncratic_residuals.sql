-- Idiosyncratic Residuals Features
-- Stock-specific return components after factor model decomposition

SELECT 
    symbol,
    date,
    daily_return,
    -- Factor model residuals
    market_residual = daily_return - (market_beta * market_return),
    size_residual = daily_return - (size_beta * size_factor_return),
    value_residual = daily_return - (value_beta * value_factor_return),
    momentum_residual = daily_return - (momentum_beta * momentum_factor_return),
    -- Multi-factor model residual
    multifactor_residual = daily_return - (
        market_beta * market_return +
        size_beta * size_factor_return +
        value_beta * value_factor_return +
        momentum_beta * momentum_factor_return +
        quality_beta * quality_factor_return
    ),
    -- Idiosyncratic volatility (rolling)
    idiosyncratic_vol_30d = STDDEV(multifactor_residual) OVER (
        PARTITION BY symbol ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) * SQRT(252),
    idiosyncratic_vol_90d = STDDEV(multifactor_residual) OVER (
        PARTITION BY symbol ORDER BY date ROWS BETWEEN 89 PRECEDING AND CURRENT ROW  
    ) * SQRT(252),
    -- Idiosyncratic momentum (residual trending)
    idiosyncratic_momentum_5d = SUM(multifactor_residual) OVER (
        PARTITION BY symbol ORDER BY date ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ),
    idiosyncratic_momentum_20d = SUM(multifactor_residual) OVER (
        PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ),
    -- Residual reversal signals
    residual_reversal_5d = -1 * idiosyncratic_momentum_5d,  -- Contrarian signal
    -- Idiosyncratic risk measures
    max_daily_residual_30d = MAX(ABS(multifactor_residual)) OVER (
        PARTITION BY symbol ORDER BY date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ),
    -- Factor model R-squared
    r_squared_multifactor,
    specific_risk = SQRT(GREATEST(0, 1 - r_squared_multifactor)) * total_volatility,
    -- Residual z-scores
    residual_zscore = multifactor_residual / NULLIF(idiosyncratic_vol_30d / SQRT(252), 0),
    -- Abnormal return detection
    abnormal_return_3sigma = CASE WHEN ABS(residual_zscore) > 3 THEN 1 ELSE 0 END,
    abnormal_return_2sigma = CASE WHEN ABS(residual_zscore) > 2 THEN 1 ELSE 0 END,
    -- Stock-specific alpha signals
    alpha_signal = CASE 
        WHEN residual_zscore > 2 AND idiosyncratic_momentum_5d > 0 THEN 1  -- Strong positive
        WHEN residual_zscore > 1 AND idiosyncratic_momentum_5d > 0 THEN 0.5  -- Moderate positive
        WHEN residual_zscore < -2 AND idiosyncratic_momentum_5d < 0 THEN -1  -- Strong negative
        WHEN residual_zscore < -1 AND idiosyncratic_momentum_5d < 0 THEN -0.5  -- Moderate negative
        ELSE 0
    END,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('risk_model', 'factor_residuals') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'