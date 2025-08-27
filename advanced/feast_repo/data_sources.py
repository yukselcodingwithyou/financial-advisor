"""
Feast data sources definition for the Financial Decision Engine.

Data sources define how Feast connects to external data systems.
"""

import os

from feast import BigQuerySource, FileSource


# BigQuery data sources (for production)
def get_bigquery_source(
    table: str, timestamp_field: str = "feature_timestamp"
) -> BigQuerySource:
    """Helper to create BigQuery sources with project configuration"""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
    dataset = os.getenv("BIGQUERY_DATASET", "financial_features")

    return BigQuerySource(
        table=f"{project_id}.{dataset}.{table}",
        timestamp_field=timestamp_field,
    )


# Market data sources
momentum_source = get_bigquery_source(
    table="momentum_features", timestamp_field="feature_timestamp"
)

value_source = get_bigquery_source(
    table="value_features", timestamp_field="feature_timestamp"
)

liquidity_source = get_bigquery_source(
    table="liquidity_features", timestamp_field="feature_timestamp"
)

sentiment_source = get_bigquery_source(
    table="sentiment_features", timestamp_field="feature_timestamp"
)

# Risk model sources
betas_source = get_bigquery_source(
    table="beta_features", timestamp_field="feature_timestamp"
)

residuals_source = get_bigquery_source(
    table="residual_features", timestamp_field="feature_timestamp"
)

# Fundamental data sources
earnings_source = get_bigquery_source(
    table="earnings_features", timestamp_field="feature_timestamp"
)

credit_risk_source = get_bigquery_source(
    table="credit_risk_features", timestamp_field="feature_timestamp"
)

esg_source = get_bigquery_source(
    table="esg_features", timestamp_field="feature_timestamp"
)

# Derivatives data sources
options_source = get_bigquery_source(
    table="options_features", timestamp_field="feature_timestamp"
)

# Macro data sources
macro_source = get_bigquery_source(
    table="macro_features", timestamp_field="feature_timestamp"
)

macro_surprise_source = get_bigquery_source(
    table="macro_surprise_features", timestamp_field="feature_timestamp"
)


# File-based sources for development/testing
def get_file_source(
    filename: str, timestamp_field: str = "feature_timestamp"
) -> FileSource:
    """Helper to create file sources for local development"""
    return FileSource(
        path=f"data/{filename}",
        timestamp_field=timestamp_field,
    )


# Development file sources (fallback when BigQuery not available)
momentum_file_source = get_file_source("momentum_features.parquet")
value_file_source = get_file_source("value_features.parquet")
liquidity_file_source = get_file_source("liquidity_features.parquet")
sentiment_file_source = get_file_source("sentiment_features.parquet")
betas_file_source = get_file_source("beta_features.parquet")
residuals_file_source = get_file_source("residual_features.parquet")
earnings_file_source = get_file_source("earnings_features.parquet")
credit_risk_file_source = get_file_source("credit_risk_features.parquet")
esg_file_source = get_file_source("esg_features.parquet")
options_file_source = get_file_source("options_features.parquet")
macro_file_source = get_file_source("macro_features.parquet")
macro_surprise_file_source = get_file_source("macro_surprise_features.parquet")

# Data source mapping for easy switching between BigQuery and file sources
USE_BIGQUERY = os.getenv("USE_BIGQUERY", "false").lower() == "true"

data_sources = {
    "momentum": momentum_source if USE_BIGQUERY else momentum_file_source,
    "value": value_source if USE_BIGQUERY else value_file_source,
    "liquidity": liquidity_source if USE_BIGQUERY else liquidity_file_source,
    "sentiment": sentiment_source if USE_BIGQUERY else sentiment_file_source,
    "betas": betas_source if USE_BIGQUERY else betas_file_source,
    "residuals": residuals_source if USE_BIGQUERY else residuals_file_source,
    "earnings": earnings_source if USE_BIGQUERY else earnings_file_source,
    "credit_risk": credit_risk_source if USE_BIGQUERY else credit_risk_file_source,
    "esg": esg_source if USE_BIGQUERY else esg_file_source,
    "options": options_source if USE_BIGQUERY else options_file_source,
    "macro": macro_source if USE_BIGQUERY else macro_file_source,
    "macro_surprise": macro_surprise_source
    if USE_BIGQUERY
    else macro_surprise_file_source,
}
