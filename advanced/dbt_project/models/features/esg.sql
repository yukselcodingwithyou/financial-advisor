-- ESG Features
-- Environmental, Social, and Governance scores and ratings

SELECT 
    symbol,
    date,
    -- Core ESG scores (0-100 scale)
    esg_score_total,
    environmental_score,
    social_score,
    governance_score,
    -- ESG percentile ranks within sector
    esg_percentile_sector,
    environmental_percentile_sector,
    social_percentile_sector,
    governance_percentile_sector,
    -- ESG momentum (improvement over time)
    esg_momentum_1y = esg_score_total - LAG(esg_score_total, 252) OVER (PARTITION BY symbol ORDER BY date),
    -- Controversy score (higher = more controversies)
    controversy_score,
    controversy_level,
    -- Carbon metrics
    carbon_intensity,
    carbon_footprint,
    carbon_reduction_target,
    -- Board diversity
    board_diversity_score,
    female_board_percentage,
    independent_board_percentage,
    -- Executive compensation alignment
    ceo_pay_ratio,
    pay_for_performance_alignment,
    -- ESG risk rating
    CASE 
        WHEN esg_score_total >= 80 THEN 'leader'
        WHEN esg_score_total >= 60 THEN 'outperformer'
        WHEN esg_score_total >= 40 THEN 'average'
        WHEN esg_score_total >= 20 THEN 'underperformer'
        ELSE 'laggard'
    END as esg_rating,
    -- ESG tilt signal
    (esg_percentile_sector - 50) / 50 as esg_tilt_signal,  -- -1 to +1 scale
    CURRENT_TIMESTAMP as feature_timestamp
FROM {{ source('esg_data', 'esg_scores') }}
WHERE date >= CURRENT_DATE - INTERVAL '2 years'