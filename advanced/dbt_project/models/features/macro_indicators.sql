{{ config(
    materialized='table',
    description='Macroeconomic indicators affecting financial markets and investment decisions'
) }}

with macro_raw_data as (
    -- In a real implementation, this would reference actual macroeconomic data sources
    select 
        current_date as date,
        'US' as country,
        'United States' as country_name,
        'USD' as currency,
        3.25 as federal_funds_rate,
        2.8 as inflation_rate_yoy,
        3.6 as unemployment_rate,
        24.8 as gdp_growth_rate_yoy,
        4250.0 as sp500_index,
        1.052 as usd_eur_exchange_rate,
        1875.50 as gold_price_usd,
        72.45 as oil_price_wti,
        4.15 as treasury_10y_yield,
        0.85 as treasury_2y_yield,
        125.6 as consumer_confidence_index,
        118.2 as purchasing_managers_index

    union all

    select 
        current_date as date,
        'EU' as country,
        'European Union' as country_name,
        'EUR' as currency,
        4.0 as federal_funds_rate,
        5.2 as inflation_rate_yoy,
        6.1 as unemployment_rate,
        0.8 as gdp_growth_rate_yoy,
        null as sp500_index,
        0.952 as usd_eur_exchange_rate,
        1780.25 as gold_price_usd,
        68.90 as oil_price_wti,
        3.95 as treasury_10y_yield,
        3.85 as treasury_2y_yield,
        98.4 as consumer_confidence_index,
        102.8 as purchasing_managers_index

    union all

    select 
        current_date as date,
        'CN' as country,
        'China' as country_name,
        'CNY' as currency,
        3.45 as federal_funds_rate,
        0.5 as inflation_rate_yoy,
        5.2 as unemployment_rate,
        5.2 as gdp_growth_rate_yoy,
        null as sp500_index,
        null as usd_eur_exchange_rate,
        null as gold_price_usd,
        null as oil_price_wti,
        2.85 as treasury_10y_yield,
        2.75 as treasury_2y_yield,
        112.8 as consumer_confidence_index,
        95.6 as purchasing_managers_index
),

macro_features as (
    select
        date,
        country,
        country_name,
        currency,
        federal_funds_rate,
        inflation_rate_yoy,
        unemployment_rate,
        gdp_growth_rate_yoy,
        sp500_index,
        usd_eur_exchange_rate,
        gold_price_usd,
        oil_price_wti,
        treasury_10y_yield,
        treasury_2y_yield,
        consumer_confidence_index,
        purchasing_managers_index,
        -- Derived features
        treasury_10y_yield - treasury_2y_yield as yield_curve_spread,
        case 
            when treasury_10y_yield - treasury_2y_yield < 0 then 'Inverted'
            when treasury_10y_yield - treasury_2y_yield < 0.5 then 'Flat'
            when treasury_10y_yield - treasury_2y_yield < 1.5 then 'Normal'
            else 'Steep'
        end as yield_curve_shape,
        case 
            when inflation_rate_yoy > federal_funds_rate then 'Negative Real Rate'
            else 'Positive Real Rate'
        end as real_interest_rate_status,
        federal_funds_rate - inflation_rate_yoy as real_interest_rate,
        case 
            when gdp_growth_rate_yoy > 3.0 then 'Strong Growth'
            when gdp_growth_rate_yoy > 1.0 then 'Moderate Growth'
            when gdp_growth_rate_yoy > -1.0 then 'Slow Growth'
            else 'Recession'
        end as economic_growth_phase,
        case 
            when unemployment_rate < 4.0 then 'Full Employment'
            when unemployment_rate < 6.0 then 'Healthy Employment'
            when unemployment_rate < 8.0 then 'Elevated Unemployment'
            else 'High Unemployment'
        end as employment_status,
        case 
            when consumer_confidence_index > 120 then 'Very Optimistic'
            when consumer_confidence_index > 100 then 'Optimistic'
            when consumer_confidence_index > 80 then 'Neutral'
            else 'Pessimistic'
        end as consumer_sentiment,
        case 
            when purchasing_managers_index > 55 then 'Strong Expansion'
            when purchasing_managers_index > 50 then 'Expansion'
            when purchasing_managers_index > 45 then 'Contraction'
            else 'Strong Contraction'
        end as manufacturing_activity
    from macro_raw_data
)

select * from macro_features