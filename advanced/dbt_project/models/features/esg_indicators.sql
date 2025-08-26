{{ config(
    materialized='table',
    description='ESG (Environmental, Social, Governance) indicators for financial assets'
) }}

with esg_raw_data as (
    -- In a real implementation, this would reference actual ESG data sources
    select 
        'AAPL' as symbol,
        'Apple Inc.' as company_name,
        current_date as date,
        8.5 as environmental_score,
        9.2 as social_score,
        8.8 as governance_score,
        8.83 as overall_esg_score,
        'A' as esg_rating,
        0.15 as carbon_intensity,
        95.2 as renewable_energy_percentage,
        89.1 as employee_satisfaction_score,
        12.5 as board_diversity_percentage

    union all

    select 
        'TSLA' as symbol,
        'Tesla Inc.' as company_name,
        current_date as date,
        9.8 as environmental_score,
        7.1 as social_score,
        6.9 as governance_score,
        7.93 as overall_esg_score,
        'B+' as esg_rating,
        0.05 as carbon_intensity,
        98.7 as renewable_energy_percentage,
        76.3 as employee_satisfaction_score,
        18.2 as board_diversity_percentage

    union all

    select 
        'MSFT' as symbol,
        'Microsoft Corporation' as company_name,
        current_date as date,
        8.9 as environmental_score,
        8.7 as social_score,
        9.1 as governance_score,
        8.90 as overall_esg_score,
        'A' as esg_rating,
        0.12 as carbon_intensity,
        87.4 as renewable_energy_percentage,
        91.6 as employee_satisfaction_score,
        22.8 as board_diversity_percentage
),

esg_features as (
    select
        symbol,
        company_name,
        date,
        environmental_score,
        social_score,
        governance_score,
        overall_esg_score,
        esg_rating,
        carbon_intensity,
        renewable_energy_percentage,
        employee_satisfaction_score,
        board_diversity_percentage,
        -- Derived features
        case 
            when overall_esg_score >= 8.5 then 'High ESG'
            when overall_esg_score >= 7.0 then 'Medium ESG'
            else 'Low ESG'
        end as esg_category,
        case 
            when environmental_score > 8.0 and carbon_intensity < 0.1 then true
            else false
        end as is_green_leader,
        (environmental_score + social_score + governance_score) / 3 as weighted_esg_score
    from esg_raw_data
)

select * from esg_features