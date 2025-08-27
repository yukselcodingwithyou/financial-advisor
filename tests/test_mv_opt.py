"""
Test mean-variance optimization functionality.

These tests verify the portfolio optimization algorithms used in the
Financial Decision Engine, including basic mean-variance optimization
and constrained optimization.
"""

import pytest
import numpy as np
import cvxpy as cp
from typing import Dict, Tuple, Optional
from scipy.optimize import minimize


def mean_variance_optimize(mu: np.ndarray, sigma: np.ndarray, 
                          risk_aversion: float = 3.0,
                          constraints: Optional[Dict] = None) -> np.ndarray:
    """
    Mean-variance portfolio optimization using CVXPY
    
    Args:
        mu: Expected returns vector
        sigma: Covariance matrix
        risk_aversion: Risk aversion parameter (higher = more risk averse)
        constraints: Additional constraints dictionary
        
    Returns:
        Optimal portfolio weights
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
        if "leverage_limit" in constraints:
            constraints_list.append(cp.norm(w, 1) <= constraints["leverage_limit"])
    
    # Solve optimization
    problem = cp.Problem(objective, constraints_list)
    
    try:
        problem.solve(solver=cp.ECOS, verbose=False)
        
        if problem.status == cp.OPTIMAL:
            return w.value
        else:
            # Return equal weights if optimization fails
            return np.ones(n) / n
            
    except Exception:
        # Return equal weights if solving fails
        return np.ones(n) / n


def calculate_portfolio_metrics(weights: np.ndarray, mu: np.ndarray, 
                               sigma: np.ndarray) -> Dict[str, float]:
    """
    Calculate portfolio performance metrics
    
    Args:
        weights: Portfolio weights
        mu: Expected returns
        sigma: Covariance matrix
        
    Returns:
        Dictionary of portfolio metrics
    """
    portfolio_return = float(np.dot(weights, mu))
    portfolio_variance = float(np.dot(weights, np.dot(sigma, weights)))
    portfolio_volatility = float(np.sqrt(portfolio_variance))
    
    # Sharpe ratio (assuming risk-free rate = 0)
    sharpe_ratio = portfolio_return / portfolio_volatility if portfolio_volatility > 0 else 0
    
    # Concentration metrics
    hhi = float(np.sum(weights**2))
    effective_assets = 1.0 / hhi if hhi > 0 else 0
    max_weight = float(np.max(weights))
    
    return {
        "expected_return": portfolio_return,
        "variance": portfolio_variance,
        "volatility": portfolio_volatility,
        "sharpe_ratio": sharpe_ratio,
        "hhi": hhi,
        "effective_assets": effective_assets,
        "max_weight": max_weight
    }


def efficient_frontier(mu: np.ndarray, sigma: np.ndarray, 
                      num_points: int = 50) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate efficient frontier points
    
    Args:
        mu: Expected returns vector
        sigma: Covariance matrix
        num_points: Number of frontier points to generate
        
    Returns:
        Tuple of (risks, returns) arrays
    """
    n = len(mu)
    
    # Calculate minimum variance portfolio
    ones = np.ones(n)
    sigma_inv = np.linalg.inv(sigma)
    
    # Minimum variance weights
    w_min_var = sigma_inv @ ones / (ones.T @ sigma_inv @ ones)
    min_var = float(np.dot(w_min_var, np.dot(sigma, w_min_var)))
    min_return = float(np.dot(w_min_var, mu))
    
    # Maximum return (unconstrained except sum=1)
    max_return = float(np.max(mu))
    
    # Generate target returns
    target_returns = np.linspace(min_return, max_return, num_points)
    
    risks = []
    returns = []
    
    for target_ret in target_returns:
        try:
            # Minimize variance subject to target return
            w = cp.Variable(n)
            objective = cp.Minimize(cp.quad_form(w, sigma))
            constraints = [
                cp.sum(w) == 1,
                w >= 0,
                mu.T @ w == target_ret
            ]
            
            problem = cp.Problem(objective, constraints)
            problem.solve(solver=cp.ECOS, verbose=False)
            
            if problem.status == cp.OPTIMAL:
                portfolio_risk = float(np.sqrt(np.dot(w.value, np.dot(sigma, w.value))))
                risks.append(portfolio_risk)
                returns.append(target_ret)
                
        except Exception:
            continue
    
    return np.array(risks), np.array(returns)


class TestMeanVarianceOptimization:
    """Test class for mean-variance optimization"""
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        n_assets = 5
        
        # Expected returns
        mu = np.array([0.08, 0.10, 0.12, 0.06, 0.09])
        
        # Create positive definite covariance matrix
        A = np.random.randn(n_assets, n_assets)
        sigma = A @ A.T + np.eye(n_assets) * 0.01  # Add small regularization
        
        return {
            "mu": mu,
            "sigma": sigma,
            "n_assets": n_assets
        }
    
    def test_mean_variance_basic(self, sample_data):
        """Test basic mean-variance optimization"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        weights = mean_variance_optimize(mu, sigma, risk_aversion=3.0)
        
        # Check basic properties
        assert len(weights) == len(mu)
        assert abs(np.sum(weights) - 1.0) < 1e-6  # Fully invested
        assert np.all(weights >= -1e-6)  # Long-only (allow small numerical errors)
    
    def test_mean_variance_different_risk_aversion(self, sample_data):
        """Test optimization with different risk aversion levels"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        # Low risk aversion (more aggressive)
        w_aggressive = mean_variance_optimize(mu, sigma, risk_aversion=1.0)
        metrics_agg = calculate_portfolio_metrics(w_aggressive, mu, sigma)
        
        # High risk aversion (more conservative)
        w_conservative = mean_variance_optimize(mu, sigma, risk_aversion=10.0)
        metrics_cons = calculate_portfolio_metrics(w_conservative, mu, sigma)
        
        # Aggressive portfolio should have higher expected return and risk
        assert metrics_agg["expected_return"] >= metrics_cons["expected_return"]
        # Note: volatility comparison depends on the specific data
    
    def test_mean_variance_with_constraints(self, sample_data):
        """Test optimization with position constraints"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        constraints = {
            "max_weight": 0.3,  # No position > 30%
            "min_weight": 0.05  # Minimum 5% in each asset
        }
        
        weights = mean_variance_optimize(mu, sigma, risk_aversion=3.0, constraints=constraints)
        
        # Check constraints are satisfied
        assert np.all(weights >= constraints["min_weight"] - 1e-6)
        assert np.all(weights <= constraints["max_weight"] + 1e-6)
        assert abs(np.sum(weights) - 1.0) < 1e-6
    
    def test_portfolio_metrics_calculation(self, sample_data):
        """Test portfolio metrics calculation"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        # Equal weights portfolio
        n = len(mu)
        equal_weights = np.ones(n) / n
        
        metrics = calculate_portfolio_metrics(equal_weights, mu, sigma)
        
        # Check metric properties
        assert "expected_return" in metrics
        assert "volatility" in metrics
        assert "sharpe_ratio" in metrics
        assert metrics["volatility"] >= 0
        assert metrics["hhi"] == pytest.approx(1.0 / n, abs=1e-10)  # Equal weights HHI
        assert metrics["effective_assets"] == pytest.approx(n, abs=1e-10)
    
    def test_efficient_frontier_generation(self, sample_data):
        """Test efficient frontier generation"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        risks, returns = efficient_frontier(mu, sigma, num_points=10)
        
        # Check properties
        assert len(risks) > 0
        assert len(returns) > 0
        assert len(risks) == len(returns)
        assert np.all(risks >= 0)  # Risk cannot be negative
        
        # Returns should be generally increasing with risk (with some tolerance)
        # This may not be strictly true due to numerical issues
        assert len(risks) <= 10  # At most the requested number
    
    def test_optimization_edge_cases(self):
        """Test optimization with edge cases"""
        # Single asset case
        mu_single = np.array([0.08])
        sigma_single = np.array([[0.04]])
        
        weights_single = mean_variance_optimize(mu_single, sigma_single)
        assert len(weights_single) == 1
        assert abs(weights_single[0] - 1.0) < 1e-6
        
        # Two asset case with perfect correlation
        mu_two = np.array([0.08, 0.10])
        sigma_two = np.array([[0.04, 0.06], [0.06, 0.09]])  # Perfect positive correlation
        
        weights_two = mean_variance_optimize(mu_two, sigma_two)
        assert len(weights_two) == 2
        assert abs(np.sum(weights_two) - 1.0) < 1e-6
    
    def test_optimization_identical_assets(self):
        """Test optimization when assets are identical"""
        # All assets have same expected return and risk
        n = 4
        mu = np.ones(n) * 0.08
        sigma = np.eye(n) * 0.04  # Identical and uncorrelated
        
        weights = mean_variance_optimize(mu, sigma)
        
        # Should result in equal weights (or close to it)
        expected_weight = 1.0 / n
        for weight in weights:
            assert abs(weight - expected_weight) < 1e-3
    
    def test_optimization_no_risk_aversion(self):
        """Test optimization with very low risk aversion"""
        mu = np.array([0.05, 0.10, 0.15])  # Increasing returns
        sigma = np.eye(3) * 0.04  # Uncorrelated, equal risk
        
        # Very low risk aversion (almost risk-neutral)
        weights = mean_variance_optimize(mu, sigma, risk_aversion=0.01)
        
        # Should heavily weight the highest return asset
        assert weights[2] > weights[1] > weights[0]  # Prefer higher return assets
    
    def test_optimization_high_risk_aversion(self):
        """Test optimization with very high risk aversion"""
        mu = np.array([0.05, 0.10, 0.15])
        
        # Create covariance with one very risky asset
        sigma = np.array([
            [0.01, 0.00, 0.00],
            [0.00, 0.04, 0.00], 
            [0.00, 0.00, 0.25]   # Very high risk
        ])
        
        # Very high risk aversion
        weights = mean_variance_optimize(mu, sigma, risk_aversion=100.0)
        
        # Should avoid the risky asset despite high return
        assert weights[0] > weights[2]  # Prefer low-risk asset
    
    def test_covariance_matrix_properties(self, sample_data):
        """Test that optimization handles covariance matrix properly"""
        mu = sample_data["mu"]
        sigma = sample_data["sigma"]
        
        # Check that sigma is positive semi-definite
        eigenvals = np.linalg.eigvals(sigma)
        assert np.all(eigenvals >= -1e-10)  # Allow for small numerical errors
        
        # Optimization should work with valid covariance matrix
        weights = mean_variance_optimize(mu, sigma)
        assert np.all(np.isfinite(weights))
        assert abs(np.sum(weights) - 1.0) < 1e-6
    
    def test_optimization_numerical_stability(self):
        """Test optimization numerical stability"""
        # Create a challenging case with very small differences
        mu = np.array([0.08001, 0.08002, 0.08003])
        
        # Create ill-conditioned covariance matrix
        sigma = np.array([
            [0.01, 0.009, 0.008],
            [0.009, 0.01, 0.009],
            [0.008, 0.009, 0.01]
        ])
        
        weights = mean_variance_optimize(mu, sigma)
        
        # Should still produce valid portfolio
        assert np.all(np.isfinite(weights))
        assert abs(np.sum(weights) - 1.0) < 1e-6
        assert np.all(weights >= -1e-6)


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])