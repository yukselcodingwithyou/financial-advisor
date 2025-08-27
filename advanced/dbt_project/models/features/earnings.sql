-- Earnings Features
-- Earnings revisions, surprises, and quality metrics

SELECT 
    symbol,
    date,
    -- Earnings estimates
    eps_estimate_current,
    eps_estimate_next,
    eps_estimate_fy1,
    eps_estimate_fy2,
    -- Earnings revisions
    eps_revision_1w = eps_estimate_current - LAG(eps_estimate_current, 5) OVER (PARTITION BY symbol ORDER BY date),
    eps_revision_1m = eps_estimate_current - LAG(eps_estimate_current, 21) OVER (PARTITION BY symbol ORDER BY date),
    eps_revision_3m = eps_estimate_current - LAG(eps_estimate_current, 63) OVER (PARTITION BY symbol ORDER BY date),
    -- Revision momentum
    revision_momentum = (eps_revision_1m / NULLIF(ABS(LAG(eps_estimate_current, 21) OVER (PARTITION BY symbol ORDER BY date)), 0)),
    -- Analyst count and dispersion
    analyst_count,
    eps_std_dev,
    revision_dispersion = eps_std_dev / NULLIF(ABS(eps_estimate_current), 0),
    -- Earnings growth
    eps_growth_estimate = (eps_estimate_fy1 / NULLIF(eps_estimate_current, 0) - 1),
    eps_growth_ltg,  -- Long-term growth estimate
    -- Historical earnings quality
    earnings_surprise_1q,
    earnings_surprise_4q_avg,
    earnings_beat_rate_4q,
    -- Earnings quality metrics
    accruals_ratio,
    earnings_persistence,
    earnings_predictability,
    -- Guidance metrics
    company_guidance_eps,
    guidance_vs_consensus = (company_guidance_eps - eps_estimate_current) / NULLIF(ABS(eps_estimate_current), 0),
    -- Earnings momentum score
    earnings_momentum_score = (
        COALESCE(revision_momentum * 40, 0) +  -- Revision trend
        COALESCE((earnings_surprise_4q_avg / NULLIF(ABS(eps_estimate_current), 0)) * 30, 0) +  -- Historical beats
        COALESCE(-revision_dispersion * 20, 0) +  -- Lower dispersion = higher score
        COALESCE(GREATEST(-10, LEAST(10, eps_growth_estimate * 10)), 0)  -- Growth component
    ),
    -- Earnings risk score (higher = more risk)
    earnings_risk_score = (
        COALESCE(revision_dispersion * 50, 0) +  -- High dispersion = high risk
        COALESCE((1 - earnings_predictability) * 30, 0) +  -- Low predictability = high risk
        COALESCE(ABS(accruals_ratio) * 20, 0)  -- High accruals = earnings quality risk
    ),
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('earnings_data', 'earnings_estimates') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'