"""
Financial Decision Engine FastAPI Service

This module provides REST endpoints for portfolio optimization, risk management,
and concentration repair using modern portfolio theory and risk constraints.
"""

import logging
from datetime import datetime
from typing import Any

import cvxpy as cp
import numpy as np
import pandas as pd
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from advanced.utils.mlflow_logger import log_optimization_run

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="Financial Decision Engine",
    description="Portfolio optimization and risk management API",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for caching
POLICIES = None
SECTOR_MAP = None
COUNTRY_MAP = None


class AssetWeights(BaseModel):
    """Asset weights for portfolio optimization"""

    weights: dict[str, float] = Field(..., description="Asset symbol to weight mapping")
    benchmark_weights: dict[str, float] | None = Field(
        None, description="Benchmark weights"
    )


class OptimizationRequest(BaseModel):
    """Portfolio optimization request"""

    assets: list[str] = Field(..., description="List of asset symbols")
    expected_returns: dict[str, float] = Field(
        ..., description="Expected returns by asset"
    )
    covariance_matrix: list[list[float]] = Field(..., description="Covariance matrix")
    risk_aversion: float = Field(default=3.0, description="Risk aversion parameter")
    constraints: dict[str, Any] | None = Field(
        None, description="Additional constraints"
    )


class ConcentrationRepairRequest(BaseModel):
    """Concentration repair request"""

    current_weights: dict[str, float] = Field(
        ..., description="Current portfolio weights"
    )
    max_concentration: float = Field(
        default=0.05, description="Maximum single asset concentration"
    )
    sector_caps: dict[str, float] | None = Field(
        None, description="Sector concentration limits"
    )
    country_caps: dict[str, float] | None = Field(
        None, description="Country concentration limits"
    )


def load_policies() -> dict[str, Any]:
    """Load policy configurations from YAML file"""
    global POLICIES, SECTOR_MAP, COUNTRY_MAP

    if POLICIES is None:
        try:
            with open("docs/policies.yaml") as f:
                POLICIES = yaml.safe_load(f)

            # Load mapping files
            SECTOR_MAP = (
                pd.read_csv("docs/sector_map.csv")
                .set_index("symbol")["sector"]
                .to_dict()
            )
            COUNTRY_MAP = (
                pd.read_csv("docs/country_map.csv")
                .set_index("symbol")["country"]
                .to_dict()
            )

            logger.info("Policies and mappings loaded successfully")
        except FileNotFoundError:
            logger.warning("Policy files not found, using defaults")
            POLICIES = {
                "concentration_limits": {"max_single_asset": 0.05, "max_sector": 0.15},
                "tilt_coefficients": {"momentum": 0.1, "value": 0.05, "quality": 0.03},
                "risk_limits": {"max_tracking_error": 0.02, "max_volatility": 0.20},
            }
            SECTOR_MAP = {}
            COUNTRY_MAP = {}

    return POLICIES


def risk_regime_adjust(volatility: float, regime: str = "normal") -> float:
    """Adjust risk parameters based on market regime"""
    regime_multipliers = {"low_vol": 0.8, "normal": 1.0, "high_vol": 1.5, "crisis": 2.0}
    return volatility * regime_multipliers.get(regime, 1.0)


def estimate_mu_sigma(returns_data: pd.DataFrame, lookback: int = 252) -> tuple:
    """Estimate expected returns and covariance matrix"""
    if len(returns_data) < lookback:
        lookback = len(returns_data)

    recent_returns = returns_data.tail(lookback)

    # Expected returns using EWMA
    alpha = 0.94  # Decay factor
    weights = np.array(
        [(1 - alpha) * alpha**i for i in range(len(recent_returns))][::-1]
    )
    weights = weights / weights.sum()

    mu = (recent_returns * weights.reshape(-1, 1)).sum(axis=0)

    # Covariance matrix using EWMA
    sigma = (
        recent_returns.ewm(alpha=1 - alpha)
        .cov()
        .iloc[-len(recent_returns.columns) :, :]
    )

    return mu.values, sigma.values


def compute_hhi(weights: dict[str, float]) -> float:
    """Compute Herfindahl-Hirschman Index for concentration measurement"""
    weight_array = np.array(list(weights.values()))
    return np.sum(weight_array**2)


def concentration_repair(
    weights: dict[str, float],
    max_concentration: float = 0.05,
    sector_caps: dict[str, float] | None = None,
    country_caps: dict[str, float] | None = None,
    sector_mapping: dict[str, str] | None = None,
    country_mapping: dict[str, str] | None = None,
) -> dict[str, float]:
    """
    Repair portfolio concentration violations using quadratic optimization
    """
    assets = list(weights.keys())
    w0 = np.array(list(weights.values()))
    n = len(assets)

    # Decision variables
    w = cp.Variable(n, name="weights")

    # Objective: minimize deviation from original weights
    objective = cp.Minimize(cp.sum_squares(w - w0))

    # Constraints
    constraints = [
        cp.sum(w) == 1,  # Fully invested
        w >= 0,  # Long-only
        w <= max_concentration,  # Individual asset limits
    ]

    # Sector constraints
    sector_map = sector_mapping or SECTOR_MAP
    if sector_caps and sector_map:
        for sector, cap in sector_caps.items():
            sector_assets = [
                i for i, asset in enumerate(assets) if sector_map.get(asset) == sector
            ]
            if sector_assets:
                constraints.append(cp.sum(w[sector_assets]) <= cap)

    # Country constraints
    country_map = country_mapping or COUNTRY_MAP
    if country_caps and country_map:
        for country, cap in country_caps.items():
            country_assets = [
                i for i, asset in enumerate(assets) if country_map.get(asset) == country
            ]
            if country_assets:
                constraints.append(cp.sum(w[country_assets]) <= cap)

    # Solve optimization
    problem = cp.Problem(objective, constraints)

    try:
        # Try different solvers
        solvers_to_try = [cp.CLARABEL, cp.SCS, cp.OSQP]
        for solver in solvers_to_try:
            try:
                problem.solve(solver=solver, verbose=False)
                if problem.status == cp.OPTIMAL:
                    repaired_weights = {
                        asset: float(w.value[i]) for i, asset in enumerate(assets)
                    }
                    logger.info(
                        f"Concentration repair completed. HHI: {compute_hhi(repaired_weights):.4f}"
                    )
                    return repaired_weights
            except Exception:
                continue

        logger.error("Optimization failed with all solvers")
        return weights

    except Exception as e:
        logger.error(f"Concentration repair failed: {e}")
        return weights


def mean_variance_optimize(
    mu: np.ndarray,
    sigma: np.ndarray,
    risk_aversion: float = 3.0,
    constraints: dict | None = None,
) -> np.ndarray:
    """
    Mean-variance portfolio optimization using CVXPY
    """
    n = len(mu)
    w = cp.Variable(n, name="weights")

    # Mean-variance objective
    portfolio_return = mu.T @ w
    portfolio_risk = cp.quad_form(w, sigma)
    objective = cp.Maximize(portfolio_return - 0.5 * risk_aversion * portfolio_risk)

    # Basic constraints
    constraints_list = [
        cp.sum(w) == 1,  # Fully invested
        w >= 0,  # Long-only
    ]

    # Additional constraints
    if constraints:
        if "max_weight" in constraints:
            constraints_list.append(w <= constraints["max_weight"])
        if "min_weight" in constraints:
            constraints_list.append(w >= constraints["min_weight"])
        if "sector_limits" in constraints:
            # Would need sector mapping for implementation
            pass

    # Solve optimization
    problem = cp.Problem(objective, constraints_list)

    try:
        problem.solve(solver=cp.ECOS)

        if problem.status == cp.OPTIMAL:
            return w.value
        else:
            logger.error(f"Optimization failed with status: {problem.status}")
            return np.ones(n) / n  # Equal weights fallback

    except Exception as e:
        logger.error(f"Mean-variance optimization failed: {e}")
        return np.ones(n) / n


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Financial Decision Engine API",
        "version": "1.0.0",
        "endpoints": [
            "/optimize",
            "/repair-concentration",
            "/risk-metrics",
            "/policies",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


@app.get("/policies")
async def get_policies():
    """Get current risk policies and constraints"""
    policies = load_policies()
    return policies


@app.post("/optimize")
async def optimize_portfolio(request: OptimizationRequest):
    """Optimize portfolio using mean-variance optimization"""
    try:
        # Convert inputs
        mu = np.array([request.expected_returns[asset] for asset in request.assets])
        sigma = np.array(request.covariance_matrix)

        # Validate inputs
        if len(mu) != len(request.assets):
            raise HTTPException(400, "Expected returns length mismatch")
        if sigma.shape != (len(request.assets), len(request.assets)):
            raise HTTPException(400, "Covariance matrix dimension mismatch")

        # Optimize
        optimal_weights = mean_variance_optimize(
            mu, sigma, request.risk_aversion, request.constraints
        )

        # Format response
        portfolio = {
            asset: float(weight)
            for asset, weight in zip(request.assets, optimal_weights, strict=False)
        }

        # Calculate metrics
        portfolio_return = float(np.dot(optimal_weights, mu))
        portfolio_risk = float(
            np.sqrt(np.dot(optimal_weights, np.dot(sigma, optimal_weights)))
        )
        sharpe_ratio = portfolio_return / portfolio_risk if portfolio_risk > 0 else 0

        # Log to MLflow
        metrics = {
            "portfolio_return": portfolio_return,
            "portfolio_risk": portfolio_risk,
            "sharpe_ratio": sharpe_ratio,
            "risk_aversion": request.risk_aversion,
        }
        log_optimization_run(metrics, portfolio, "mean_variance")

        return {
            "portfolio": portfolio,
            "metrics": {
                "expected_return": portfolio_return,
                "volatility": portfolio_risk,
                "sharpe_ratio": sharpe_ratio,
                "concentration_hhi": compute_hhi(portfolio),
            },
        }

    except Exception as e:
        logger.error(f"Portfolio optimization failed: {e}")
        raise HTTPException(500, f"Optimization failed: {str(e)}") from e


@app.post("/repair-concentration")
async def repair_portfolio_concentration(request: ConcentrationRepairRequest):
    """Repair portfolio concentration violations"""
    try:
        repaired_weights = concentration_repair(
            request.current_weights,
            request.max_concentration,
            request.sector_caps,
            request.country_caps,
        )

        original_hhi = compute_hhi(request.current_weights)
        repaired_hhi = compute_hhi(repaired_weights)

        return {
            "original_portfolio": request.current_weights,
            "repaired_portfolio": repaired_weights,
            "metrics": {
                "original_hhi": original_hhi,
                "repaired_hhi": repaired_hhi,
                "concentration_reduction": original_hhi - repaired_hhi,
            },
        }

    except Exception as e:
        logger.error(f"Concentration repair failed: {e}")
        raise HTTPException(500, f"Concentration repair failed: {str(e)}") from e


@app.post("/risk-metrics")
async def calculate_risk_metrics(weights: AssetWeights):
    """Calculate comprehensive risk metrics for a portfolio"""
    try:
        portfolio_weights = weights.weights

        # Basic metrics
        hhi = compute_hhi(portfolio_weights)

        # Active share (if benchmark provided)
        active_share = None
        if weights.benchmark_weights:
            active_weights = {
                asset: portfolio_weights.get(asset, 0)
                - weights.benchmark_weights.get(asset, 0)
                for asset in set(
                    list(portfolio_weights.keys())
                    + list(weights.benchmark_weights.keys())
                )
            }
            active_share = 0.5 * sum(abs(w) for w in active_weights.values())

        return {
            "concentration_hhi": hhi,
            "max_weight": max(portfolio_weights.values()),
            "num_positions": len([w for w in portfolio_weights.values() if w > 0.001]),
            "active_share": active_share,
            "effective_num_stocks": 1 / hhi if hhi > 0 else None,
        }

    except Exception as e:
        logger.error(f"Risk metrics calculation failed: {e}")
        raise HTTPException(500, f"Risk calculation failed: {str(e)}") from e


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
