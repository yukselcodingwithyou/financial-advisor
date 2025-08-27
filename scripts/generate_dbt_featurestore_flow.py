#!/usr/bin/env python3
"""
Generate dbt and feature store flow diagram using Graphviz.

This script creates a detailed visualization of the data flow through
dbt models to the Feast feature store.
"""

from pathlib import Path

import graphviz


def create_dbt_featurestore_flow():
    """Create comprehensive dbt to feature store flow diagram"""

    dot = graphviz.Digraph(
        "dbt_featurestore_flow", comment="dbt to Feature Store Flow", format="png"
    )

    dot.attr(rankdir="TB", size="16,12", dpi="300")
    dot.attr(
        "node", shape="box", style="rounded,filled", fontname="Arial", fontsize="9"
    )
    dot.attr("edge", fontname="Arial", fontsize="8")

    # Define color scheme for different layers
    colors = {
        "source": "#FFEBEE",  # Light red for sources
        "bronze": "#FFF3E0",  # Light orange for raw data
        "silver": "#F3E5F5",  # Light purple for features
        "gold": "#E8F5E8",  # Light green for aggregated
        "feast": "#E3F2FD",  # Light blue for Feast
        "serving": "#FCE4EC",  # Light pink for serving
    }

    # Source Systems
    with dot.subgraph(name="cluster_sources") as sources:
        sources.attr(label="Source Systems", style="filled", color="lightgray")
        sources.node("market_api", "Market Data\nAPI", fillcolor=colors["source"])
        sources.node(
            "fundamental_api", "Fundamental\nData API", fillcolor=colors["source"]
        )
        sources.node("options_feed", "Options\nData Feed", fillcolor=colors["source"])
        sources.node("news_api", "News &\nSentiment API", fillcolor=colors["source"])
        sources.node("esg_provider", "ESG Data\nProvider", fillcolor=colors["source"])

    # Bronze Layer (Raw Data in BigQuery)
    with dot.subgraph(name="cluster_bronze") as bronze:
        bronze.attr(label="Bronze Layer (Raw Data)", style="filled", color="lightgray")
        bronze.node("raw_prices", "raw_daily_prices", fillcolor=colors["bronze"])
        bronze.node(
            "raw_fundamentals", "raw_financial_ratios", fillcolor=colors["bronze"]
        )
        bronze.node("raw_options", "raw_options_data", fillcolor=colors["bronze"])
        bronze.node("raw_sentiment", "raw_sentiment_data", fillcolor=colors["bronze"])
        bronze.node("raw_esg", "raw_esg_scores", fillcolor=colors["bronze"])
        bronze.node("raw_macro", "raw_macro_indicators", fillcolor=colors["bronze"])

    # Silver Layer (dbt Feature Models)
    with dot.subgraph(name="cluster_silver") as silver:
        silver.attr(
            label="Silver Layer (dbt Feature Models)", style="filled", color="lightgray"
        )
        silver.node(
            "momentum_model",
            "momentum.sql\n1m, 3m, 6m, 12m\nmomentum signals",
            fillcolor=colors["silver"],
        )
        silver.node(
            "value_model",
            "value.sql\nP/E, P/B, EV/EBITDA\nsector z-scores",
            fillcolor=colors["silver"],
        )
        silver.node(
            "liquidity_model",
            "liquidity.sql\nvolume, spreads\nAmihud illiquidity",
            fillcolor=colors["silver"],
        )
        silver.node(
            "sentiment_model",
            "sentiment.sql\nnews, analyst, social\ncomposite scores",
            fillcolor=colors["silver"],
        )
        silver.node(
            "betas_model",
            "betas.sql\nmarket, factor\nexposures",
            fillcolor=colors["silver"],
        )
        silver.node(
            "esg_model",
            "esg.sql\nE, S, G scores\ntilt signals",
            fillcolor=colors["silver"],
        )
        silver.node(
            "options_model",
            "options.sql\nIV, skew, flow\nvolatility signals",
            fillcolor=colors["silver"],
        )
        silver.node(
            "macro_model",
            "macro.sql\nrates, spreads\nregime classification",
            fillcolor=colors["silver"],
        )
        silver.node(
            "earnings_model",
            "earnings.sql\nrevisions, surprises\nmomentum scores",
            fillcolor=colors["silver"],
        )
        silver.node(
            "credit_model",
            "credit_risk.sql\nratings, spreads\ndefault probability",
            fillcolor=colors["silver"],
        )
        silver.node(
            "residuals_model",
            "idiosyncratic_residuals.sql\nfactor model residuals\nalpha signals",
            fillcolor=colors["silver"],
        )
        silver.node(
            "macro_surprise_model",
            "macro_surprise.sql\neconomic surprises\nregime indicators",
            fillcolor=colors["silver"],
        )

    # Gold Layer (Aggregated Features)
    with dot.subgraph(name="cluster_gold") as gold:
        gold.attr(
            label="Gold Layer (Feature Aggregations)", style="filled", color="lightgray"
        )
        gold.node(
            "equity_features",
            "equity_features\ncombined stock signals",
            fillcolor=colors["gold"],
        )
        gold.node(
            "macro_features",
            "macro_features\nmarket regime indicators",
            fillcolor=colors["gold"],
        )
        gold.node(
            "risk_features", "risk_features\nfactor exposures", fillcolor=colors["gold"]
        )

    # Feast Feature Store
    with dot.subgraph(name="cluster_feast") as feast:
        feast.attr(label="Feast Feature Store", style="filled", color="lightgray")
        feast.node(
            "feast_registry",
            "Feature Registry\nentities, views, sources",
            fillcolor=colors["feast"],
        )
        feast.node(
            "offline_store",
            "Offline Store\n(BigQuery)\nhistorical features",
            fillcolor=colors["feast"],
        )
        feast.node(
            "online_store",
            "Online Store\n(PostgreSQL)\nreal-time serving",
            fillcolor=colors["feast"],
        )

    # Serving Layer
    with dot.subgraph(name="cluster_serving") as serving:
        serving.attr(label="Feature Serving", style="filled", color="lightgray")
        serving.node(
            "fastapi_serving", "FastAPI\nFeature Serving", fillcolor=colors["serving"]
        )
        serving.node(
            "optimization_engine",
            "Portfolio\nOptimization",
            fillcolor=colors["serving"],
        )
        serving.node("risk_engine", "Risk\nManagement", fillcolor=colors["serving"])

    # Data Flow Connections

    # Sources to Bronze
    source_to_bronze = [
        ("market_api", "raw_prices"),
        ("fundamental_api", "raw_fundamentals"),
        ("options_feed", "raw_options"),
        ("news_api", "raw_sentiment"),
        ("esg_provider", "raw_esg"),
        ("market_api", "raw_macro"),
    ]

    # Bronze to Silver (dbt models)
    bronze_to_silver = [
        ("raw_prices", "momentum_model"),
        ("raw_prices", "liquidity_model"),
        ("raw_prices", "betas_model"),
        ("raw_fundamentals", "value_model"),
        ("raw_fundamentals", "earnings_model"),
        ("raw_fundamentals", "credit_model"),
        ("raw_sentiment", "sentiment_model"),
        ("raw_esg", "esg_model"),
        ("raw_options", "options_model"),
        ("raw_macro", "macro_model"),
        ("raw_macro", "macro_surprise_model"),
        ("betas_model", "residuals_model"),
    ]

    # Silver to Gold
    silver_to_gold = [
        ("momentum_model", "equity_features"),
        ("value_model", "equity_features"),
        ("liquidity_model", "equity_features"),
        ("sentiment_model", "equity_features"),
        ("earnings_model", "equity_features"),
        ("credit_model", "equity_features"),
        ("esg_model", "equity_features"),
        ("options_model", "equity_features"),
        ("macro_model", "macro_features"),
        ("macro_surprise_model", "macro_features"),
        ("betas_model", "risk_features"),
        ("residuals_model", "risk_features"),
    ]

    # Gold to Feast
    gold_to_feast = [
        ("equity_features", "feast_registry"),
        ("macro_features", "feast_registry"),
        ("risk_features", "feast_registry"),
    ]

    # Feast internal flow
    feast_internal = [
        ("feast_registry", "offline_store"),
        ("offline_store", "online_store"),
    ]

    # Feast to Serving
    feast_to_serving = [
        ("online_store", "fastapi_serving"),
        ("fastapi_serving", "optimization_engine"),
        ("fastapi_serving", "risk_engine"),
    ]

    # Add all edges
    all_connections = (
        source_to_bronze
        + bronze_to_silver
        + silver_to_gold
        + gold_to_feast
        + feast_internal
        + feast_to_serving
    )

    for src, dst in all_connections:
        dot.edge(src, dst)

    # Add some special annotations
    dot.edge(
        "macro_model",
        "macro_surprise_model",
        style="dashed",
        label="regime context",
        fontsize="7",
    )
    dot.edge(
        "value_model",
        "earnings_model",
        style="dashed",
        label="fundamental correlation",
        fontsize="7",
    )

    return dot


def create_feature_lineage_diagram():
    """Create a feature lineage diagram for a specific feature"""

    dot = graphviz.Digraph(
        "feature_lineage",
        comment="Feature Lineage Example: Momentum Score",
        format="png",
    )

    dot.attr(rankdir="LR", size="12,8", dpi="300")
    dot.attr("node", shape="ellipse", style="filled", fontname="Arial", fontsize="10")
    dot.attr("edge", fontname="Arial", fontsize="9")

    # Color scheme
    colors = {
        "raw": "#FFCDD2",
        "calc": "#F8BBD9",
        "normalize": "#E1BEE7",
        "composite": "#C5CAE9",
        "output": "#BBDEFB",
    }

    # Raw data
    dot.node(
        "daily_prices", "Daily Prices\n(raw_daily_prices)", fillcolor=colors["raw"]
    )

    # Calculations
    dot.node("price_1m", "1-Month\nPrice Change", fillcolor=colors["calc"])
    dot.node("price_3m", "3-Month\nPrice Change", fillcolor=colors["calc"])
    dot.node("price_6m", "6-Month\nPrice Change", fillcolor=colors["calc"])
    dot.node("price_12m", "12-Month\nPrice Change", fillcolor=colors["calc"])
    dot.node("volatility", "60-Day\nVolatility", fillcolor=colors["calc"])

    # Normalization
    dot.node("mom_1m_z", "1M Momentum\nZ-Score", fillcolor=colors["normalize"])
    dot.node("mom_3m_z", "3M Momentum\nZ-Score", fillcolor=colors["normalize"])
    dot.node("mom_6m_z", "6M Momentum\nZ-Score", fillcolor=colors["normalize"])
    dot.node("mom_12m_z", "12M Momentum\nZ-Score", fillcolor=colors["normalize"])
    dot.node("risk_adj_mom", "Risk-Adjusted\nMomentum", fillcolor=colors["normalize"])

    # Composite
    dot.node(
        "momentum_score", "Composite\nMomentum Score", fillcolor=colors["composite"]
    )

    # Output
    dot.node("portfolio_tilt", "Portfolio\nTilt Signal", fillcolor=colors["output"])

    # Define connections with calculations
    connections = [
        ("daily_prices", "price_1m", "LAG(price, 21)"),
        ("daily_prices", "price_3m", "LAG(price, 63)"),
        ("daily_prices", "price_6m", "LAG(price, 126)"),
        ("daily_prices", "price_12m", "LAG(price, 252)"),
        ("daily_prices", "volatility", "STDDEV(returns)"),
        ("price_1m", "mom_1m_z", "sector z-score"),
        ("price_3m", "mom_3m_z", "sector z-score"),
        ("price_6m", "mom_6m_z", "sector z-score"),
        ("price_12m", "mom_12m_z", "sector z-score"),
        ("price_3m", "risk_adj_mom", "momentum / volatility"),
        ("volatility", "risk_adj_mom", ""),
        ("mom_1m_z", "momentum_score", "weighted\naverage"),
        ("mom_3m_z", "momentum_score", ""),
        ("mom_6m_z", "momentum_score", ""),
        ("mom_12m_z", "momentum_score", ""),
        ("risk_adj_mom", "momentum_score", ""),
        ("momentum_score", "portfolio_tilt", "factor coefficient"),
    ]

    # Add edges with labels
    for src, dst, label in connections:
        if label:
            dot.edge(src, dst, label=label, fontsize="8")
        else:
            dot.edge(src, dst)

    return dot


def main():
    """Generate and save dbt feature store flow diagrams"""

    # Create output directory
    output_dir = Path("docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("Generating dbt and Feature Store flow diagrams...")

    try:
        # Generate main flow diagram
        flow_diagram = create_dbt_featurestore_flow()
        flow_diagram.render(str(output_dir / "dbt_featurestore_flow"), cleanup=True)
        print(
            f"✅ dbt Feature Store flow saved to {output_dir / 'dbt_featurestore_flow.png'}"
        )

        # Generate feature lineage diagram
        lineage_diagram = create_feature_lineage_diagram()
        lineage_diagram.render(str(output_dir / "feature_lineage"), cleanup=True)
        print(
            f"✅ Feature lineage diagram saved to {output_dir / 'feature_lineage.png'}"
        )

        print("\n📊 dbt and Feature Store diagrams generated successfully!")
        print("These diagrams show:")
        print("1. Complete data flow from sources through dbt to Feast feature store")
        print("2. Feature lineage example showing how momentum scores are calculated")
        print("3. Bronze/Silver/Gold data architecture pattern")

    except Exception as e:
        print(f"❌ Error generating diagrams: {e}")
        print("Make sure Graphviz is installed: pip install graphviz")
        print(
            "And system Graphviz: apt-get install graphviz (Ubuntu) or brew install graphviz (Mac)"
        )


if __name__ == "__main__":
    main()
