-- Credit Risk Features
-- Corporate credit metrics and default probability indicators

SELECT 
    symbol,
    date,
    -- Credit ratings
    sp_rating,
    moody_rating,
    fitch_rating,
    credit_rating_numeric,  -- Converted to numeric scale
    -- Credit spreads
    cds_5y_spread,
    cds_1y_spread,
    cds_curve_slope = cds_5y_spread - cds_1y_spread,
    -- Financial health metrics
    debt_to_equity,
    interest_coverage_ratio,
    current_ratio,
    quick_ratio,
    debt_service_coverage,
    -- Cash flow metrics
    free_cash_flow_yield,
    operating_cash_flow_ratio,
    cash_conversion_cycle,
    -- Profitability and efficiency
    return_on_assets,
    return_on_equity,
    profit_margin,
    asset_turnover,
    -- Market-based credit metrics
    equity_volatility,
    market_cap,
    book_value_of_equity,
    -- Altman Z-Score for bankruptcy prediction
    altman_z_score = 
        1.2 * (working_capital / total_assets) +
        1.4 * (retained_earnings / total_assets) +
        3.3 * (ebit / total_assets) +
        0.6 * (market_cap / total_liabilities) +
        1.0 * (sales / total_assets),
    -- Credit risk score (0-100, higher = lower risk)
    credit_risk_score = LEAST(100, GREATEST(0,
        50 +  -- Base score
        COALESCE((credit_rating_numeric - 10) * 5, 0) +  -- Rating component
        COALESCE(LEAST(20, interest_coverage_ratio * 2), -20) +  -- Coverage component
        COALESCE(GREATEST(-20, (current_ratio - 1) * 10), 0) +  -- Liquidity component
        COALESCE(GREATEST(-30, altman_z_score * 5), 0)  -- Bankruptcy risk component
    )),
    -- Default probability estimate (simplified)
    default_probability_1y = GREATEST(0.0001, LEAST(0.5,
        EXP(-3 + 0.1 * COALESCE(cds_5y_spread, 5) - 0.05 * COALESCE(altman_z_score, 0))
    )),
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('credit_data', 'credit_metrics') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'