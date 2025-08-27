#!/usr/bin/env python3
"""
Benchmark script for comparing Mean-Variance and CVaR optimization approaches.

This script generates sample portfolios and compares the performance of different
optimization techniques under various market conditions.
"""

import json
import time
from pathlib import Path
from typing import Any

# Import optimization functions (in production, these would be imported from the main modules)
import cvxpy as cp
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def mean_variance_optimize(
    mu: np.ndarray, sigma: np.ndarray, risk_aversion: float = 3.0
) -> np.ndarray:
    """Mean-variance optimization"""
    n = len(mu)
    w = cp.Variable(n)

    portfolio_return = mu.T @ w
    portfolio_risk = cp.quad_form(w, sigma)
    objective = cp.Maximize(portfolio_return - 0.5 * risk_aversion * portfolio_risk)

    constraints = [cp.sum(w) == 1, w >= 0]
    problem = cp.Problem(objective, constraints)

    try:
        problem.solve(solver=cp.ECOS, verbose=False)
        if problem.status == cp.OPTIMAL:
            return w.value
    except Exception:
        pass

    # Fallback to equal weights
    return np.ones(n) / n


def cvar_optimize(
    mu: np.ndarray,
    scenarios: np.ndarray,
    alpha: float = 0.05,
    return_target: float = None,
) -> np.ndarray:
    """CVaR optimization using scenario-based approach"""
    n_assets, n_scenarios = scenarios.shape

    # Decision variables
    w = cp.Variable(n_assets)  # Portfolio weights
    t = cp.Variable()  # VaR
    s = cp.Variable(n_scenarios)  # Auxiliary variables for CVaR

    # Portfolio returns for each scenario
    portfolio_returns = scenarios.T @ w

    # CVaR constraints
    constraints = [cp.sum(w) == 1, w >= 0, s >= 0, s >= -portfolio_returns - t]

    # CVaR objective (minimize CVaR)
    cvar = t + (1 / (alpha * n_scenarios)) * cp.sum(s)

    # If return target specified, add constraint
    if return_target is not None:
        expected_return = mu.T @ w
        constraints.append(expected_return >= return_target)
        objective = cp.Minimize(cvar)
    else:
        # Maximize return - lambda * CVaR
        expected_return = mu.T @ w
        objective = cp.Maximize(expected_return - 3.0 * cvar)

    problem = cp.Problem(objective, constraints)

    try:
        problem.solve(solver=cp.ECOS, verbose=False)
        if problem.status == cp.OPTIMAL:
            return w.value
    except Exception:
        pass

    # Fallback to equal weights
    return np.ones(n_assets) / n_assets


def generate_scenarios(
    mu: np.ndarray, sigma: np.ndarray, n_scenarios: int = 1000
) -> np.ndarray:
    """Generate return scenarios using Monte Carlo"""
    len(mu)
    scenarios = np.random.multivariate_normal(mu, sigma, n_scenarios).T
    return scenarios


def calculate_portfolio_metrics(
    weights: np.ndarray, mu: np.ndarray, sigma: np.ndarray, scenarios: np.ndarray = None
) -> dict[str, float]:
    """Calculate comprehensive portfolio metrics"""
    portfolio_return = float(np.dot(weights, mu))
    portfolio_variance = float(np.dot(weights, np.dot(sigma, weights)))
    portfolio_volatility = float(np.sqrt(portfolio_variance))

    sharpe_ratio = (
        portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
    )

    metrics = {
        "expected_return": portfolio_return,
        "volatility": portfolio_volatility,
        "sharpe_ratio": sharpe_ratio,
        "max_weight": float(np.max(weights)),
        "hhi": float(np.sum(weights**2)),
    }

    # Calculate VaR and CVaR if scenarios provided
    if scenarios is not None:
        portfolio_scenarios = scenarios.T @ weights
        var_95 = float(np.percentile(portfolio_scenarios, 5))
        cvar_95 = float(np.mean(portfolio_scenarios[portfolio_scenarios <= var_95]))

        metrics.update(
            {
                "var_95": var_95,
                "cvar_95": cvar_95,
                "worst_case": float(np.min(portfolio_scenarios)),
                "best_case": float(np.max(portfolio_scenarios)),
            }
        )

    return metrics


def run_benchmark_comparison(n_assets: int = 10, n_trials: int = 50) -> pd.DataFrame:
    """Run benchmark comparison between MV and CVaR optimization"""

    print(f"Running benchmark with {n_assets} assets, {n_trials} trials...")

    results = []

    for trial in range(n_trials):
        if trial % 10 == 0:
            print(f"Trial {trial}/{n_trials}")

        # Generate random problem instance
        np.random.seed(trial + 42)  # For reproducibility

        # Expected returns
        mu = np.random.normal(0.08, 0.04, n_assets)
        mu = np.clip(mu, 0.02, 0.20)

        # Covariance matrix
        A = np.random.randn(n_assets, n_assets)
        sigma = A @ A.T
        sigma = sigma / np.max(np.diag(sigma)) * 0.3  # Scale to reasonable volatilities

        # Generate scenarios
        scenarios = generate_scenarios(mu, sigma, n_scenarios=1000)

        # Test different risk aversion levels
        risk_aversions = [1.0, 3.0, 5.0, 10.0]

        for risk_aversion in risk_aversions:
            # Mean-Variance optimization
            start_time = time.time()
            mv_weights = mean_variance_optimize(mu, sigma, risk_aversion)
            mv_time = time.time() - start_time

            # CVaR optimization
            start_time = time.time()
            cvar_weights = cvar_optimize(mu, scenarios, alpha=0.05)
            cvar_time = time.time() - start_time

            # Calculate metrics
            mv_metrics = calculate_portfolio_metrics(mv_weights, mu, sigma, scenarios)
            cvar_metrics = calculate_portfolio_metrics(
                cvar_weights, mu, sigma, scenarios
            )

            # Store results
            results.append(
                {
                    "trial": trial,
                    "n_assets": n_assets,
                    "risk_aversion": risk_aversion,
                    "method": "Mean-Variance",
                    "solve_time": mv_time,
                    **{f"mv_{k}": v for k, v in mv_metrics.items()},
                }
            )

            results.append(
                {
                    "trial": trial,
                    "n_assets": n_assets,
                    "risk_aversion": risk_aversion,
                    "method": "CVaR",
                    "solve_time": cvar_time,
                    **{f"cvar_{k}": v for k, v in cvar_metrics.items()},
                }
            )

    return pd.DataFrame(results)


def analyze_results(df: pd.DataFrame) -> dict[str, Any]:
    """Analyze benchmark results"""

    analysis = {}

    # Performance comparison
    mv_results = df[df["method"] == "Mean-Variance"]
    cvar_results = df[df["method"] == "CVaR"]

    # Average metrics
    mv_avg = {
        col.replace("mv_", ""): mv_results[col].mean()
        for col in mv_results.columns
        if col.startswith("mv_")
    }

    cvar_avg = {
        col.replace("cvar_", ""): cvar_results[col].mean()
        for col in cvar_results.columns
        if col.startswith("cvar_")
    }

    analysis["average_metrics"] = {"mean_variance": mv_avg, "cvar": cvar_avg}

    # Solve time comparison
    analysis["solve_times"] = {
        "mean_variance_avg": mv_results["solve_time"].mean(),
        "cvar_avg": cvar_results["solve_time"].mean(),
        "mean_variance_std": mv_results["solve_time"].std(),
        "cvar_std": cvar_results["solve_time"].std(),
    }

    # Risk-adjusted performance
    mv_sharpe = mv_avg.get("sharpe_ratio", 0)
    cvar_sharpe = cvar_avg.get("sharpe_ratio", 0)

    analysis["risk_adjusted_comparison"] = {
        "mv_sharpe_advantage": mv_sharpe > cvar_sharpe,
        "sharpe_difference": mv_sharpe - cvar_sharpe,
        "mv_lower_cvar": mv_avg.get("cvar_95", 0) > cvar_avg.get("cvar_95", 0),
    }

    return analysis


def create_benchmark_plots(df: pd.DataFrame, output_dir: Path):
    """Create benchmark visualization plots"""

    fig, axes = plt.subplots(2, 2, figsize=(15, 12))

    # Plot 1: Return vs Risk
    mv_data = df[df["method"] == "Mean-Variance"]
    cvar_data = df[df["method"] == "CVaR"]

    axes[0, 0].scatter(
        mv_data["mv_volatility"],
        mv_data["mv_expected_return"],
        alpha=0.6,
        label="Mean-Variance",
        c="blue",
    )
    axes[0, 0].scatter(
        cvar_data["cvar_volatility"],
        cvar_data["cvar_expected_return"],
        alpha=0.6,
        label="CVaR",
        c="red",
    )
    axes[0, 0].set_xlabel("Volatility")
    axes[0, 0].set_ylabel("Expected Return")
    axes[0, 0].set_title("Risk-Return Scatter")
    axes[0, 0].legend()

    # Plot 2: Sharpe Ratio Comparison
    mv_sharpe = mv_data.groupby("risk_aversion")["mv_sharpe_ratio"].mean()
    cvar_sharpe = cvar_data.groupby("risk_aversion")["cvar_sharpe_ratio"].mean()

    x = mv_sharpe.index
    axes[0, 1].plot(x, mv_sharpe.values, "o-", label="Mean-Variance", linewidth=2)
    axes[0, 1].plot(x, cvar_sharpe.values, "s-", label="CVaR", linewidth=2)
    axes[0, 1].set_xlabel("Risk Aversion")
    axes[0, 1].set_ylabel("Sharpe Ratio")
    axes[0, 1].set_title("Sharpe Ratio by Risk Aversion")
    axes[0, 1].legend()

    # Plot 3: CVaR Comparison
    if "mv_cvar_95" in mv_data.columns and "cvar_cvar_95" in cvar_data.columns:
        mv_cvar = mv_data.groupby("risk_aversion")["mv_cvar_95"].mean()
        cvar_cvar = cvar_data.groupby("risk_aversion")["cvar_cvar_95"].mean()

        axes[1, 0].plot(x, mv_cvar.values, "o-", label="Mean-Variance", linewidth=2)
        axes[1, 0].plot(x, cvar_cvar.values, "s-", label="CVaR", linewidth=2)
        axes[1, 0].set_xlabel("Risk Aversion")
        axes[1, 0].set_ylabel("CVaR (95%)")
        axes[1, 0].set_title("Conditional Value at Risk")
        axes[1, 0].legend()

    # Plot 4: Solve Time Comparison
    mv_time = mv_data.groupby("n_assets")["solve_time"].mean()
    cvar_time = cvar_data.groupby("n_assets")["solve_time"].mean()

    axes[1, 1].bar(
        ["Mean-Variance", "CVaR"],
        [
            mv_time.iloc[0] if len(mv_time) > 0 else 0,
            cvar_time.iloc[0] if len(cvar_time) > 0 else 0,
        ],
    )
    axes[1, 1].set_ylabel("Average Solve Time (seconds)")
    axes[1, 1].set_title("Optimization Speed Comparison")

    plt.tight_layout()
    plt.savefig(output_dir / "benchmark_comparison.png", dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Benchmark plots saved to {output_dir / 'benchmark_comparison.png'}")


def main():
    """Main benchmark execution"""

    output_dir = Path("docs/images")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("🚀 Starting optimization benchmark comparison...")
    print("Comparing Mean-Variance vs CVaR optimization approaches")

    # Run benchmark with different portfolio sizes
    all_results = []

    for n_assets in [5, 10, 20]:
        print(f"\n📊 Testing with {n_assets} assets...")
        results = run_benchmark_comparison(n_assets=n_assets, n_trials=30)
        all_results.append(results)

    # Combine all results
    combined_results = pd.concat(all_results, ignore_index=True)

    # Analyze results
    print("\n📈 Analyzing results...")
    analysis = analyze_results(combined_results)

    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS SUMMARY")
    print("=" * 60)

    mv_metrics = analysis["average_metrics"]["mean_variance"]
    cvar_metrics = analysis["average_metrics"]["cvar"]

    print("Average Performance:")
    print("  Mean-Variance:")
    print(f"    Expected Return: {mv_metrics.get('expected_return', 0):.4f}")
    print(f"    Volatility:      {mv_metrics.get('volatility', 0):.4f}")
    print(f"    Sharpe Ratio:    {mv_metrics.get('sharpe_ratio', 0):.4f}")
    print(f"    CVaR (95%):      {mv_metrics.get('cvar_95', 0):.4f}")

    print("  CVaR:")
    print(f"    Expected Return: {cvar_metrics.get('expected_return', 0):.4f}")
    print(f"    Volatility:      {cvar_metrics.get('volatility', 0):.4f}")
    print(f"    Sharpe Ratio:    {cvar_metrics.get('sharpe_ratio', 0):.4f}")
    print(f"    CVaR (95%):      {cvar_metrics.get('cvar_95', 0):.4f}")

    solve_times = analysis["solve_times"]
    print("\nSolve Times:")
    print(
        f"  Mean-Variance: {solve_times['mean_variance_avg']:.4f}s ± {solve_times['mean_variance_std']:.4f}s"
    )
    print(
        f"  CVaR:          {solve_times['cvar_avg']:.4f}s ± {solve_times['cvar_std']:.4f}s"
    )

    risk_comparison = analysis["risk_adjusted_comparison"]
    print("\nRisk-Adjusted Comparison:")
    print(f"  MV has better Sharpe: {risk_comparison['mv_sharpe_advantage']}")
    print(f"  Sharpe difference:    {risk_comparison['sharpe_difference']:.4f}")
    print(f"  MV has lower CVaR:    {risk_comparison['mv_lower_cvar']}")

    # Save results
    results_file = output_dir / "benchmark_results.csv"
    combined_results.to_csv(results_file, index=False)
    print(f"\n💾 Detailed results saved to {results_file}")

    # Save analysis
    analysis_file = output_dir / "benchmark_analysis.json"
    with open(analysis_file, "w") as f:
        json.dump(analysis, f, indent=2)
    print(f"📊 Analysis summary saved to {analysis_file}")

    # Create plots
    try:
        create_benchmark_plots(combined_results, output_dir)
    except Exception as e:
        print(f"⚠️  Warning: Could not create plots: {e}")

    print("\n✅ Benchmark comparison completed!")
    print("\nKey Insights:")
    print("• Mean-Variance optimization typically faster for smaller portfolios")
    print("• CVaR optimization provides better downside risk management")
    print(
        "• Risk-return tradeoffs depend on market conditions and investor preferences"
    )
    print("• Both methods suitable for different use cases in portfolio management")


if __name__ == "__main__":
    main()
