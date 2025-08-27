-- Value Features
-- Calculate value indicators like P/E, P/B, EV/EBITDA ratios

SELECT 
    f.symbol,
    f.date,
    f.pe_ratio,
    f.pb_ratio,
    f.ev_ebitda,
    f.price_to_sales,
    f.price_to_cash_flow,
    -- Value z-scores relative to sector
    (f.pe_ratio - AVG(f.pe_ratio) OVER (PARTITION BY s.sector, f.date)) / 
    NULLIF(STDDEV(f.pe_ratio) OVER (PARTITION BY s.sector, f.date), 0) as pe_zscore_sector,
    (f.pb_ratio - AVG(f.pb_ratio) OVER (PARTITION BY s.sector, f.date)) / 
    NULLIF(STDDEV(f.pb_ratio) OVER (PARTITION BY s.sector, f.date), 0) as pb_zscore_sector,
    (f.ev_ebitda - AVG(f.ev_ebitda) OVER (PARTITION BY s.sector, f.date)) / 
    NULLIF(STDDEV(f.ev_ebitda) OVER (PARTITION BY s.sector, f.date), 0) as ev_ebitda_zscore_sector,
    -- Composite value score
    (
        COALESCE((f.pe_ratio - AVG(f.pe_ratio) OVER (PARTITION BY s.sector, f.date)) / 
                 NULLIF(STDDEV(f.pe_ratio) OVER (PARTITION BY s.sector, f.date), 0), 0) * 0.4 +
        COALESCE((f.pb_ratio - AVG(f.pb_ratio) OVER (PARTITION BY s.sector, f.date)) / 
                 NULLIF(STDDEV(f.pb_ratio) OVER (PARTITION BY s.sector, f.date), 0), 0) * 0.3 +
        COALESCE((f.ev_ebitda - AVG(f.ev_ebitda) OVER (PARTITION BY s.sector, f.date)) / 
                 NULLIF(STDDEV(f.ev_ebitda) OVER (PARTITION BY s.sector, f.date), 0), 0) * 0.3
    ) * -1 as composite_value_score,  -- Negative because lower ratios = more attractive
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('fundamental_data', 'financial_ratios') }} f
LEFT JOIN {{ source('reference_data', 'security_master') }} s ON f.symbol = s.symbol
WHERE f.date >= CURRENT_DATE - INTERVAL '2 years'
    AND f.pe_ratio > 0 
    AND f.pb_ratio > 0
    AND f.ev_ebitda > 0