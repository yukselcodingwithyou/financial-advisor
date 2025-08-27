"""
Feast feature views definition for the Financial Decision Engine.

Feature views define how features are computed and retrieved from data sources.
"""

from datetime import timedelta
from feast import FeatureView, Field
from feast.types import Float64, String, Int64

from .entities import security, date_entity, sector, country
from .data_sources import data_sources


# Momentum features
momentum_fv = FeatureView(
    name="momentum_features",
    entities=[security],
    schema=[
        Field(name="momentum_1m", dtype=Float64),
        Field(name="momentum_3m", dtype=Float64),
        Field(name="momentum_6m", dtype=Float64),
        Field(name="momentum_12m", dtype=Float64),
        Field(name="risk_adj_momentum_3m", dtype=Float64),
        Field(name="momentum_acceleration", dtype=Float64),
    ],
    source=data_sources["momentum"],
    ttl=timedelta(days=7),
    description="Price momentum indicators across different time horizons",
)

# Value features
value_fv = FeatureView(
    name="value_features", 
    entities=[security],
    schema=[
        Field(name="pe_ratio", dtype=Float64),
        Field(name="pb_ratio", dtype=Float64),
        Field(name="ev_ebitda", dtype=Float64),
        Field(name="pe_zscore_sector", dtype=Float64),
        Field(name="pb_zscore_sector", dtype=Float64),
        Field(name="composite_value_score", dtype=Float64),
    ],
    source=data_sources["value"],
    ttl=timedelta(days=30),
    description="Valuation metrics and sector-relative value scores",
)

# Liquidity features
liquidity_fv = FeatureView(
    name="liquidity_features",
    entities=[security],
    schema=[
        Field(name="volume_ratio", dtype=Float64),
        Field(name="bid_ask_spread", dtype=Float64),
        Field(name="amihud_illiquidity", dtype=Float64),
        Field(name="liquidity_score", dtype=Float64),
        Field(name="dollar_volume", dtype=Float64),
    ],
    source=data_sources["liquidity"],
    ttl=timedelta(days=1),
    description="Trading liquidity and market microstructure metrics",
)

# Sentiment features
sentiment_fv = FeatureView(
    name="sentiment_features",
    entities=[security],
    schema=[
        Field(name="news_sentiment_score", dtype=Float64),
        Field(name="analyst_rating_avg", dtype=Float64),
        Field(name="target_price_return", dtype=Float64),
        Field(name="put_call_ratio", dtype=Float64),
        Field(name="short_interest_ratio", dtype=Float64),
        Field(name="composite_sentiment_score", dtype=Float64),
    ],
    source=data_sources["sentiment"],
    ttl=timedelta(days=1),
    description="Multi-source sentiment indicators and positioning metrics",
)

# Beta/risk factor exposures
betas_fv = FeatureView(
    name="beta_features",
    entities=[security],
    schema=[
        Field(name="market_beta_60d", dtype=Float64),
        Field(name="market_beta_252d", dtype=Float64),
        Field(name="value_beta", dtype=Float64),
        Field(name="growth_beta", dtype=Float64),
        Field(name="momentum_beta", dtype=Float64),
        Field(name="quality_beta", dtype=Float64),
        Field(name="size_beta", dtype=Float64),
        Field(name="downside_beta", dtype=Float64),
        Field(name="tracking_error_252d", dtype=Float64),
        Field(name="r_squared_252d", dtype=Float64),
    ],
    source=data_sources["betas"],
    ttl=timedelta(days=7),
    description="Factor loadings and risk model exposures",
)

# Idiosyncratic residuals
residuals_fv = FeatureView(
    name="residual_features",
    entities=[security],
    schema=[
        Field(name="multifactor_residual", dtype=Float64),
        Field(name="idiosyncratic_vol_30d", dtype=Float64),
        Field(name="idiosyncratic_momentum_20d", dtype=Float64),
        Field(name="residual_zscore", dtype=Float64),
        Field(name="alpha_signal", dtype=Float64),
        Field(name="specific_risk", dtype=Float64),
    ],
    source=data_sources["residuals"],
    ttl=timedelta(days=1),
    description="Stock-specific return components and alpha signals",
)

# Earnings features
earnings_fv = FeatureView(
    name="earnings_features",
    entities=[security],
    schema=[
        Field(name="eps_revision_1m", dtype=Float64),
        Field(name="eps_revision_3m", dtype=Float64),
        Field(name="eps_growth_estimate", dtype=Float64),
        Field(name="earnings_surprise_4q_avg", dtype=Float64),
        Field(name="earnings_momentum_score", dtype=Float64),
        Field(name="earnings_risk_score", dtype=Float64),
        Field(name="analyst_count", dtype=Int64),
    ],
    source=data_sources["earnings"],
    ttl=timedelta(days=7),
    description="Earnings estimates, revisions, and quality metrics",
)

# Credit risk features
credit_risk_fv = FeatureView(
    name="credit_risk_features",
    entities=[security],
    schema=[
        Field(name="credit_rating_numeric", dtype=Float64),
        Field(name="debt_to_equity", dtype=Float64),
        Field(name="interest_coverage_ratio", dtype=Float64),
        Field(name="altman_z_score", dtype=Float64),
        Field(name="credit_risk_score", dtype=Float64),
        Field(name="default_probability_1y", dtype=Float64),
    ],
    source=data_sources["credit_risk"],
    ttl=timedelta(days=30),
    description="Credit quality and default risk indicators",
)

# ESG features
esg_fv = FeatureView(
    name="esg_features",
    entities=[security],
    schema=[
        Field(name="esg_score_total", dtype=Float64),
        Field(name="environmental_score", dtype=Float64),
        Field(name="social_score", dtype=Float64),
        Field(name="governance_score", dtype=Float64),
        Field(name="esg_percentile_sector", dtype=Float64),
        Field(name="esg_tilt_signal", dtype=Float64),
        Field(name="controversy_score", dtype=Float64),
    ],
    source=data_sources["esg"],
    ttl=timedelta(days=30),
    description="Environmental, Social, and Governance metrics",
)

# Options features
options_fv = FeatureView(
    name="options_features",
    entities=[security],
    schema=[
        Field(name="iv_30d", dtype=Float64),
        Field(name="iv_rank_30d", dtype=Float64),
        Field(name="put_call_ratio_volume", dtype=Float64),
        Field(name="volatility_skew", dtype=Float64),
        Field(name="vol_risk_premium", dtype=Float64),
        Field(name="max_pain_distance", dtype=Float64),
    ],
    source=data_sources["options"],
    ttl=timedelta(days=1),
    description="Options-derived volatility and sentiment indicators",
)

# Macro features
macro_fv = FeatureView(
    name="macro_features",
    entities=[date_entity],
    schema=[
        Field(name="fed_funds_rate", dtype=Float64),
        Field(name="yield_curve_slope", dtype=Float64),
        Field(name="vix_level", dtype=Float64),
        Field(name="credit_spread_ig", dtype=Float64),
        Field(name="dollar_index", dtype=Float64),
        Field(name="volatility_regime", dtype=String),
        Field(name="yield_curve_regime", dtype=String),
    ],
    source=data_sources["macro"],
    ttl=timedelta(days=1),
    description="Macroeconomic indicators and regime classification",
)

# Macro surprise features
macro_surprise_fv = FeatureView(
    name="macro_surprise_features",
    entities=[date_entity],
    schema=[
        Field(name="growth_surprise_index", dtype=Float64),
        Field(name="inflation_surprise_index", dtype=Float64),
        Field(name="monetary_surprise_index", dtype=Float64),
        Field(name="growth_surprise_3m", dtype=Float64),
        Field(name="inflation_surprise_3m", dtype=Float64),
        Field(name="macro_regime", dtype=String),
    ],
    source=data_sources["macro_surprise"],
    ttl=timedelta(days=1),
    description="Economic data surprises and regime indicators",
)

# All feature views for easy import
feature_views = [
    momentum_fv,
    value_fv,
    liquidity_fv,
    sentiment_fv,
    betas_fv,
    residuals_fv,
    earnings_fv,
    credit_risk_fv,
    esg_fv,
    options_fv,
    macro_fv,
    macro_surprise_fv,
]