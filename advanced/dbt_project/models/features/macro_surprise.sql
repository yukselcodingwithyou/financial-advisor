-- Macro Surprise Features
-- Economic data surprises and their market impact

SELECT 
    date,
    -- Employment surprises
    nonfarm_payrolls_surprise,
    unemployment_rate_surprise,
    jobless_claims_surprise,
    -- Inflation surprises  
    cpi_surprise,
    core_cpi_surprise,
    pce_surprise,
    core_pce_surprise,
    -- Growth surprises
    gdp_surprise,
    industrial_production_surprise,
    retail_sales_surprise,
    housing_starts_surprise,
    -- Monetary policy surprises
    fed_funds_surprise,
    fomc_statement_surprise,
    fed_speech_surprise,
    -- International surprises
    ecb_surprise,
    boj_surprise,
    china_pmi_surprise,
    -- Composite surprise indices
    growth_surprise_index = (
        COALESCE(gdp_surprise, 0) * 0.3 +
        COALESCE(industrial_production_surprise, 0) * 0.25 +
        COALESCE(retail_sales_surprise, 0) * 0.25 +
        COALESCE(nonfarm_payrolls_surprise, 0) * 0.2
    ),
    inflation_surprise_index = (
        COALESCE(cpi_surprise, 0) * 0.4 +
        COALESCE(core_cpi_surprise, 0) * 0.4 +
        COALESCE(pce_surprise, 0) * 0.2
    ),
    monetary_surprise_index = (
        COALESCE(fed_funds_surprise, 0) * 0.5 +
        COALESCE(fomc_statement_surprise, 0) * 0.3 +
        COALESCE(fed_speech_surprise, 0) * 0.2
    ),
    -- Surprise momentum (cumulative surprises)
    growth_surprise_3m = SUM(growth_surprise_index) OVER (ORDER BY date ROWS BETWEEN 62 PRECEDING AND CURRENT ROW),
    inflation_surprise_3m = SUM(inflation_surprise_index) OVER (ORDER BY date ROWS BETWEEN 62 PRECEDING AND CURRENT ROW),
    -- Market regime based on surprises
    CASE 
        WHEN growth_surprise_3m > 2 AND inflation_surprise_3m < -1 THEN 'goldilocks'
        WHEN growth_surprise_3m > 1 AND inflation_surprise_3m > 1 THEN 'overheating'
        WHEN growth_surprise_3m < -2 AND inflation_surprise_3m < 0 THEN 'deflation_risk'
        WHEN growth_surprise_3m < -1 THEN 'growth_slowdown'
        WHEN inflation_surprise_3m > 2 THEN 'inflation_risk'
        ELSE 'stable'
    END as macro_regime,
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('economic_data', 'economic_surprises') }}
WHERE date >= CURRENT_DATE - INTERVAL '5 years'