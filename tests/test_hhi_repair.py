"""
Test HHI (Herfindahl-Hirschman Index) concentration repair functionality.

These tests verify the concentration measurement and repair optimization
used in portfolio risk management.
"""

import pytest
import numpy as np
import cvxpy as cp
from typing import Dict, Any, Optional


def compute_hhi(weights: Dict[str, float]) -> float:
    """
    Compute Herfindahl-Hirschman Index for portfolio concentration
    
    Args:
        weights: Dictionary of asset weights
        
    Returns:
        HHI value (higher = more concentrated)
    """
    weight_array = np.array(list(weights.values()))
    return float(np.sum(weight_array ** 2))


def effective_number_of_assets(weights: Dict[str, float]) -> float:
    """
    Calculate effective number of assets (1/HHI)
    
    Args:
        weights: Dictionary of asset weights
        
    Returns:
        Effective number of assets
    """
    hhi = compute_hhi(weights)
    return 1.0 / hhi if hhi > 0 else 0.0


def concentration_repair(weights: Dict[str, float], 
                        max_concentration: float = 0.05,
                        sector_caps: Optional[Dict[str, float]] = None,
                        sector_mapping: Optional[Dict[str, str]] = None) -> Dict[str, float]:
    """
    Repair portfolio concentration violations using quadratic optimization
    
    Args:
        weights: Current portfolio weights
        max_concentration: Maximum weight per asset
        sector_caps: Maximum weight per sector
        sector_mapping: Asset to sector mapping
        
    Returns:
        Repaired portfolio weights
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
    if sector_caps and sector_mapping:
        sectors = set(sector_mapping.values())
        for sector in sectors:
            if sector in sector_caps:
                sector_assets = [i for i, asset in enumerate(assets) 
                               if sector_mapping.get(asset) == sector]
                if sector_assets:
                    constraints.append(cp.sum(w[sector_assets]) <= sector_caps[sector])
    
    # Solve optimization
    problem = cp.Problem(objective, constraints)
    
    try:
        problem.solve(solver=cp.ECOS, verbose=False)
        
        if problem.status == cp.OPTIMAL:
            return {asset: float(w.value[i]) for i, asset in enumerate(assets)}
        else:
            # If optimization fails, return equal weights as fallback
            equal_weight = 1.0 / len(assets)
            return {asset: equal_weight for asset in assets}
            
    except Exception:
        # If solving fails, return equal weights as fallback
        equal_weight = 1.0 / len(assets)
        return {asset: equal_weight for asset in assets}


class TestHHIRepair:
    """Test class for HHI concentration repair functionality"""
    
    @pytest.fixture
    def equal_weight_portfolio(self):
        """Create an equal-weighted portfolio"""
        assets = [f"ASSET_{i:02d}" for i in range(1, 11)]  # 10 assets
        equal_weight = 1.0 / len(assets)
        return {asset: equal_weight for asset in assets}
    
    @pytest.fixture
    def concentrated_portfolio(self):
        """Create a concentrated portfolio"""
        return {
            "ASSET_01": 0.40,  # Highly concentrated
            "ASSET_02": 0.25,  # Also high
            "ASSET_03": 0.15,
            "ASSET_04": 0.10,
            "ASSET_05": 0.05,
            "ASSET_06": 0.03,
            "ASSET_07": 0.02,
        }
    
    @pytest.fixture
    def sector_mapping(self):
        """Create sector mapping for testing"""
        return {
            "ASSET_01": "Technology",
            "ASSET_02": "Technology", 
            "ASSET_03": "Healthcare",
            "ASSET_04": "Healthcare",
            "ASSET_05": "Finance",
            "ASSET_06": "Finance",
            "ASSET_07": "Energy",
        }
    
    def test_compute_hhi_equal_weights(self, equal_weight_portfolio):
        """Test HHI calculation for equal-weighted portfolio"""
        hhi = compute_hhi(equal_weight_portfolio)
        
        # For equal weights, HHI = 1/N
        n_assets = len(equal_weight_portfolio)
        expected_hhi = 1.0 / n_assets
        
        assert abs(hhi - expected_hhi) < 1e-10
    
    def test_compute_hhi_concentrated(self, concentrated_portfolio):
        """Test HHI calculation for concentrated portfolio"""
        hhi = compute_hhi(concentrated_portfolio)
        
        # Calculate expected HHI manually
        weights = list(concentrated_portfolio.values())
        expected_hhi = sum(w**2 for w in weights)
        
        assert abs(hhi - expected_hhi) < 1e-10
        
        # Should be higher than equal-weight case
        n_assets = len(concentrated_portfolio)
        equal_weight_hhi = 1.0 / n_assets
        assert hhi > equal_weight_hhi
    
    def test_effective_number_of_assets(self, equal_weight_portfolio, concentrated_portfolio):
        """Test effective number of assets calculation"""
        # Equal weight case
        equal_ena = effective_number_of_assets(equal_weight_portfolio)
        n_assets = len(equal_weight_portfolio)
        assert abs(equal_ena - n_assets) < 1e-10
        
        # Concentrated case
        conc_ena = effective_number_of_assets(concentrated_portfolio)
        n_assets_conc = len(concentrated_portfolio)
        assert conc_ena < n_assets_conc  # Should be less than actual number
    
    def test_concentration_repair_basic(self, concentrated_portfolio):
        """Test basic concentration repair"""
        max_concentration = 0.10  # 10% maximum per asset
        
        repaired = concentration_repair(concentrated_portfolio, max_concentration)
        
        # Check constraints are satisfied
        assert abs(sum(repaired.values()) - 1.0) < 1e-6  # Fully invested
        assert all(w >= 0 for w in repaired.values())  # Long-only
        assert all(w <= max_concentration + 1e-6 for w in repaired.values())  # Concentration limit
        
        # Check HHI improved
        original_hhi = compute_hhi(concentrated_portfolio)
        repaired_hhi = compute_hhi(repaired)
        assert repaired_hhi < original_hhi
    
    def test_concentration_repair_no_violation(self, equal_weight_portfolio):
        """Test concentration repair when no violation exists"""
        max_concentration = 0.50  # Very high limit
        
        repaired = concentration_repair(equal_weight_portfolio, max_concentration)
        
        # Should be very close to original (no repair needed)
        for asset in equal_weight_portfolio:
            assert abs(repaired[asset] - equal_weight_portfolio[asset]) < 1e-3
    
    def test_concentration_repair_with_sectors(self, concentrated_portfolio, sector_mapping):
        """Test concentration repair with sector constraints"""
        max_concentration = 0.08
        sector_caps = {
            "Technology": 0.30,  # Tech sector cap
            "Healthcare": 0.25,
            "Finance": 0.20,
            "Energy": 0.10
        }
        
        repaired = concentration_repair(
            concentrated_portfolio, 
            max_concentration, 
            sector_caps, 
            sector_mapping
        )
        
        # Check individual asset constraints
        assert all(w <= max_concentration + 1e-6 for w in repaired.values())
        
        # Check sector constraints
        for sector, cap in sector_caps.items():
            sector_weight = sum(
                repaired[asset] for asset in repaired
                if sector_mapping.get(asset) == sector
            )
            assert sector_weight <= cap + 1e-6
    
    def test_concentration_repair_extreme_case(self):
        """Test concentration repair with extreme concentration"""
        # Single asset owns 90%
        extreme_portfolio = {
            "DOMINANT": 0.90,
            "SMALL_1": 0.03,
            "SMALL_2": 0.03,
            "SMALL_3": 0.02,
            "SMALL_4": 0.02,
        }
        
        max_concentration = 0.20  # Force major rebalancing
        
        repaired = concentration_repair(extreme_portfolio, max_concentration)
        
        # Check constraints
        assert abs(sum(repaired.values()) - 1.0) < 1e-6
        assert all(w <= max_concentration + 1e-6 for w in repaired.values())
        
        # Check significant improvement in HHI
        original_hhi = compute_hhi(extreme_portfolio)
        repaired_hhi = compute_hhi(repaired)
        assert repaired_hhi < 0.5 * original_hhi  # At least 50% improvement
    
    def test_hhi_edge_cases(self):
        """Test HHI calculation edge cases"""
        # Single asset portfolio
        single_asset = {"ONLY_ONE": 1.0}
        assert compute_hhi(single_asset) == 1.0
        assert effective_number_of_assets(single_asset) == 1.0
        
        # Empty portfolio (should not happen in practice)
        empty_portfolio = {}
        assert compute_hhi(empty_portfolio) == 0.0
        
        # Portfolio with zero weights
        with_zeros = {"A": 0.5, "B": 0.5, "C": 0.0}
        hhi = compute_hhi(with_zeros)
        expected = 0.5**2 + 0.5**2 + 0.0**2
        assert abs(hhi - expected) < 1e-10
    
    def test_concentration_repair_preserves_ranking(self):
        """Test that concentration repair preserves relative rankings where possible"""
        portfolio = {
            "LARGE": 0.30,   # Largest position
            "MEDIUM": 0.25,  # Medium position
            "SMALL": 0.20,   # Smaller position
            "TINY_1": 0.15,
            "TINY_2": 0.10,
        }
        
        max_concentration = 0.22  # Force reduction of top positions
        
        repaired = concentration_repair(portfolio, max_concentration)
        
        # Check that LARGE is still largest (or tied for largest)
        large_weight = repaired["LARGE"]
        assert all(large_weight >= repaired[asset] - 1e-6 for asset in repaired)
        
        # Check that TINY positions didn't become dominant
        assert repaired["TINY_1"] <= max_concentration + 1e-6
        assert repaired["TINY_2"] <= max_concentration + 1e-6
    
    def test_concentration_repair_infeasible_constraints(self):
        """Test concentration repair with potentially infeasible constraints"""
        portfolio = {"A": 0.4, "B": 0.3, "C": 0.2, "D": 0.1}
        
        # Very tight constraint that might be hard to satisfy
        max_concentration = 0.15  # Forces major rebalancing
        
        repaired = concentration_repair(portfolio, max_concentration)
        
        # Should still return valid portfolio even if optimization is challenging
        assert abs(sum(repaired.values()) - 1.0) < 1e-6
        assert all(w >= 0 for w in repaired.values())
        
        # Constraints should be satisfied (or very close)
        for weight in repaired.values():
            assert weight <= max_concentration + 1e-4  # Allow small tolerance
    
    def test_hhi_mathematical_properties(self):
        """Test mathematical properties of HHI"""
        # HHI should be between 1/N and 1
        for n in [2, 5, 10, 100]:
            equal_weights = {f"asset_{i}": 1.0/n for i in range(n)}
            hhi = compute_hhi(equal_weights)
            
            assert hhi >= 1.0/n - 1e-10  # Lower bound
            assert hhi <= 1.0 + 1e-10    # Upper bound
            
            # For equal weights, HHI should equal 1/N exactly
            assert abs(hhi - 1.0/n) < 1e-10


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])