from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource, ValueType
from feast.types import Float32, String, Bool, Int32

# Define entities
company = Entity(
    name="company",
    value_type=ValueType.STRING,
    description="Company symbol identifier"
)

country = Entity(
    name="country", 
    value_type=ValueType.STRING,
    description="Country code identifier"
)

# ESG Feature Source
esg_source = FileSource(
    path="data/esg_indicators.parquet",
    timestamp_field="date",
)

# ESG Feature View
esg_feature_view = FeatureView(
    name="esg_indicators",
    entities=[company],
    ttl=timedelta(days=1),
    schema=[
        Field(name="environmental_score", dtype=Float32),
        Field(name="social_score", dtype=Float32),
        Field(name="governance_score", dtype=Float32),
        Field(name="overall_esg_score", dtype=Float32),
        Field(name="esg_rating", dtype=String),
        Field(name="carbon_intensity", dtype=Float32),
        Field(name="renewable_energy_percentage", dtype=Float32),
        Field(name="employee_satisfaction_score", dtype=Float32),
        Field(name="board_diversity_percentage", dtype=Float32),
        Field(name="esg_category", dtype=String),
        Field(name="is_green_leader", dtype=Bool),
        Field(name="weighted_esg_score", dtype=Float32),
    ],
    source=esg_source,
    tags={"team": "risk_management", "category": "esg"},
)

# Credit Feature Source
credit_source = FileSource(
    path="data/credit_indicators.parquet",
    timestamp_field="date",
)

# Credit Feature View  
credit_feature_view = FeatureView(
    name="credit_indicators",
    entities=[company],
    ttl=timedelta(days=1),
    schema=[
        Field(name="credit_rating", dtype=String),
        Field(name="credit_spread_bps", dtype=Float32),
        Field(name="debt_to_equity_ratio", dtype=Float32),
        Field(name="interest_coverage_ratio", dtype=Float32),
        Field(name="probability_of_default", dtype=Float32),
        Field(name="recovery_rate_percentage", dtype=Float32),
        Field(name="current_ratio", dtype=Float32),
        Field(name="quick_ratio", dtype=Float32),
        Field(name="debt_to_assets_ratio", dtype=Float32),
        Field(name="credit_quality_category", dtype=String),
        Field(name="default_risk_category", dtype=String),
        Field(name="is_liquid", dtype=Bool),
        Field(name="leverage_category", dtype=String),
        Field(name="credit_score", dtype=Float32),
    ],
    source=credit_source,
    tags={"team": "credit_risk", "category": "credit"},
)

# Macro Feature Source
macro_source = FileSource(
    path="data/macro_indicators.parquet", 
    timestamp_field="date",
)

# Macro Feature View
macro_feature_view = FeatureView(
    name="macro_indicators",
    entities=[country],
    ttl=timedelta(hours=6),
    schema=[
        Field(name="federal_funds_rate", dtype=Float32),
        Field(name="inflation_rate_yoy", dtype=Float32),
        Field(name="unemployment_rate", dtype=Float32),
        Field(name="gdp_growth_rate_yoy", dtype=Float32),
        Field(name="sp500_index", dtype=Float32),
        Field(name="usd_eur_exchange_rate", dtype=Float32),
        Field(name="gold_price_usd", dtype=Float32),
        Field(name="oil_price_wti", dtype=Float32),
        Field(name="treasury_10y_yield", dtype=Float32),
        Field(name="treasury_2y_yield", dtype=Float32),
        Field(name="consumer_confidence_index", dtype=Float32),
        Field(name="purchasing_managers_index", dtype=Float32),
        Field(name="yield_curve_spread", dtype=Float32),
        Field(name="yield_curve_shape", dtype=String),
        Field(name="real_interest_rate_status", dtype=String),
        Field(name="real_interest_rate", dtype=Float32),
        Field(name="economic_growth_phase", dtype=String),
        Field(name="employment_status", dtype=String),
        Field(name="consumer_sentiment", dtype=String),
        Field(name="manufacturing_activity", dtype=String),
    ],
    source=macro_source,
    tags={"team": "macro_economics", "category": "macro"},
)