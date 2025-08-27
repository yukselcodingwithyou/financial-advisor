"""
Feast entities definition for the Financial Decision Engine.

Entities represent the main keys that features are associated with.
"""

from feast import Entity

# Security entity - represents individual stocks/securities
security = Entity(
    name="security",
    join_keys=["symbol"],
    description="Individual security/stock identifier",
)

# Date entity - for time-based feature lookups
date_entity = Entity(
    name="date",
    join_keys=["date"],
    description="Date for time-based feature queries",
)

# Portfolio entity - for portfolio-level features
portfolio = Entity(
    name="portfolio",
    join_keys=["portfolio_id"],
    description="Portfolio identifier for portfolio-level features",
)

# Sector entity - for sector-level aggregations
sector = Entity(
    name="sector",
    join_keys=["sector_code"],
    description="Sector classification for sector-level features",
)

# Country entity - for country/region-level features
country = Entity(
    name="country",
    join_keys=["country_code"],
    description="Country/region classification",
)

# Factor entity - for factor model features
factor = Entity(
    name="factor",
    join_keys=["factor_name"],
    description="Risk factor identifier",
)

# All entities list for easy import
entities = [security, date_entity, portfolio, sector, country, factor]
