{{ config(
    materialized='table',
    description='Credit risk indicators and credit quality metrics for financial assets'
) }}

with credit_raw_data as (
    -- In a real implementation, this would reference actual credit data sources
    select 
        'AAPL' as symbol,
        'Apple Inc.' as company_name,
        current_date as date,
        'AAA' as credit_rating,
        0.25 as credit_spread_bps,
        2.1 as debt_to_equity_ratio,
        28.5 as interest_coverage_ratio,
        0.15 as probability_of_default,
        98.2 as recovery_rate_percentage,
        15.8 as current_ratio,
        8.9 as quick_ratio,
        25.6 as debt_to_assets_ratio

    union all

    select 
        'TSLA' as symbol,
        'Tesla Inc.' as company_name,
        current_date as date,
        'BBB+' as credit_rating,
        1.85 as credit_spread_bps,
        1.8 as debt_to_equity_ratio,
        12.3 as interest_coverage_ratio,
        2.1 as probability_of_default,
        75.6 as recovery_rate_percentage,
        2.1 as current_ratio,
        1.8 as quick_ratio,
        18.9 as debt_to_assets_ratio

    union all

    select 
        'F' as symbol,
        'Ford Motor Company' as company_name,
        current_date as date,
        'BB-' as credit_rating,
        4.25 as credit_spread_bps,
        3.2 as debt_to_equity_ratio,
        5.8 as interest_coverage_ratio,
        8.5 as probability_of_default,
        45.2 as recovery_rate_percentage,
        1.2 as current_ratio,
        0.9 as quick_ratio,
        45.6 as debt_to_assets_ratio
),

credit_features as (
    select
        symbol,
        company_name,
        date,
        credit_rating,
        credit_spread_bps,
        debt_to_equity_ratio,
        interest_coverage_ratio,
        probability_of_default,
        recovery_rate_percentage,
        current_ratio,
        quick_ratio,
        debt_to_assets_ratio,
        -- Derived features
        case 
            when credit_rating in ('AAA', 'AA+', 'AA', 'AA-') then 'Investment Grade High'
            when credit_rating in ('A+', 'A', 'A-', 'BBB+', 'BBB', 'BBB-') then 'Investment Grade Low'
            when credit_rating in ('BB+', 'BB', 'BB-', 'B+', 'B', 'B-') then 'Speculative Grade'
            else 'High Risk'
        end as credit_quality_category,
        case 
            when probability_of_default < 1.0 then 'Low Risk'
            when probability_of_default < 5.0 then 'Medium Risk'
            else 'High Risk'
        end as default_risk_category,
        case 
            when current_ratio >= 2.0 and quick_ratio >= 1.0 then true
            else false
        end as is_liquid,
        case 
            when debt_to_equity_ratio < 0.5 then 'Conservative'
            when debt_to_equity_ratio < 1.5 then 'Moderate'
            else 'Aggressive'
        end as leverage_category,
        -- Credit score calculation (0-100)
        least(100, greatest(0, 
            100 - (probability_of_default * 10) - (credit_spread_bps / 10) + 
            (recovery_rate_percentage / 10) + (interest_coverage_ratio / 2)
        )) as credit_score
    from credit_raw_data
)

select * from credit_features