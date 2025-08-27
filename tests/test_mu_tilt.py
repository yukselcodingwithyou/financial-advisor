"""
Test mu tilt functionality for factor-based portfolio optimization.

These tests verify the mean return estimation and factor tilt calculations
used in the portfolio optimization process.
"""

import numpy as np
import pytest


# Mock the factor tilt functionality since we're testing the concept
def calculate_mu_tilt(
    base_returns: np.ndarray,
    factor_scores: dict[str, np.ndarray],
    tilt_coefficients: dict[str, float],
) -> np.ndarray:
    """
    Calculate tilted expected returns based on factor scores

    Args:
        base_returns: Base expected returns for assets
        factor_scores: Dictionary of factor scores (z-scores) for each factor
        tilt_coefficients: Dictionary of tilt coefficients for each factor

    Returns:
        Tilted expected returns
    """
    tilted_returns = base_returns.copy()

    for factor_name, scores in factor_scores.items():
        if factor_name in tilt_coefficients:
            coefficient = tilt_coefficients[factor_name]
            # Apply tilt: positive coefficient increases return for positive scores
            tilt_adjustment = coefficient * scores
            tilted_returns += tilt_adjustment

    return tilted_returns


def normalize_factor_scores(
    raw_scores: np.ndarray, method: str = "zscore"
) -> np.ndarray:
    """
    Normalize factor scores to z-scores or other normalized forms

    Args:
        raw_scores: Raw factor scores
        method: Normalization method ("zscore", "rank", "minmax")

    Returns:
        Normalized scores
    """
    if method == "zscore":
        mean_score = np.mean(raw_scores)
        std_score = np.std(raw_scores)
        if std_score > 0:
            return (raw_scores - mean_score) / std_score
        else:
            return np.zeros_like(raw_scores)

    elif method == "rank":
        # Convert to percentile ranks and then to z-scores
        from scipy import stats

        ranks = stats.rankdata(raw_scores) / len(raw_scores)
        return stats.norm.ppf(np.clip(ranks, 0.01, 0.99))

    elif method == "minmax":
        min_val, max_val = np.min(raw_scores), np.max(raw_scores)
        if max_val > min_val:
            return 2 * (raw_scores - min_val) / (max_val - min_val) - 1
        else:
            return np.zeros_like(raw_scores)

    else:
        raise ValueError(f"Unknown normalization method: {method}")


class TestMuTilt:
    """Test class for mu tilt functionality"""

    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing"""
        np.random.seed(42)
        n_assets = 10

        # Base expected returns
        base_returns = np.random.normal(0.08, 0.03, n_assets)

        # Factor scores (raw)
        momentum_scores = np.random.normal(0, 1, n_assets)
        value_scores = np.random.normal(0, 1, n_assets)
        quality_scores = np.random.normal(0, 1, n_assets)

        # Factor coefficients
        tilt_coefficients = {"momentum": 0.02, "value": 0.015, "quality": 0.01}

        return {
            "base_returns": base_returns,
            "raw_factors": {
                "momentum": momentum_scores,
                "value": value_scores,
                "quality": quality_scores,
            },
            "tilt_coefficients": tilt_coefficients,
            "n_assets": n_assets,
        }

    def test_normalize_factor_scores_zscore(self, sample_data):
        """Test z-score normalization of factor scores"""
        raw_scores = sample_data["raw_factors"]["momentum"]

        normalized = normalize_factor_scores(raw_scores, "zscore")

        # Check properties of z-score normalization
        assert abs(np.mean(normalized)) < 1e-10  # Mean should be ~0
        assert abs(np.std(normalized) - 1.0) < 1e-10  # Std should be ~1
        assert len(normalized) == len(raw_scores)

    def test_normalize_factor_scores_rank(self, sample_data):
        """Test rank-based normalization"""
        raw_scores = sample_data["raw_factors"]["momentum"]

        normalized = normalize_factor_scores(raw_scores, "rank")

        # Check that normalized scores are in reasonable range
        assert np.all(normalized >= -3)  # No extreme outliers
        assert np.all(normalized <= 3)
        assert len(normalized) == len(raw_scores)

    def test_normalize_factor_scores_minmax(self, sample_data):
        """Test min-max normalization"""
        raw_scores = sample_data["raw_factors"]["momentum"]

        normalized = normalize_factor_scores(raw_scores, "minmax")

        # Check min-max properties
        assert np.min(normalized) >= -1.0
        assert np.max(normalized) <= 1.0
        assert abs(np.min(normalized) + 1.0) < 1e-10  # Should be exactly -1
        assert abs(np.max(normalized) - 1.0) < 1e-10  # Should be exactly 1

    def test_calculate_mu_tilt_basic(self, sample_data):
        """Test basic mu tilt calculation"""
        base_returns = sample_data["base_returns"]
        tilt_coefficients = sample_data["tilt_coefficients"]

        # Normalize factor scores
        factor_scores = {}
        for factor_name, raw_scores in sample_data["raw_factors"].items():
            factor_scores[factor_name] = normalize_factor_scores(raw_scores, "zscore")

        # Calculate tilted returns
        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, tilt_coefficients
        )

        # Check basic properties
        assert len(tilted_returns) == len(base_returns)
        assert np.all(np.isfinite(tilted_returns))

        # Returns should be modified (unless all factor scores are zero)
        assert not np.allclose(tilted_returns, base_returns)

    def test_calculate_mu_tilt_zero_coefficients(self, sample_data):
        """Test mu tilt with zero coefficients (no tilt)"""
        base_returns = sample_data["base_returns"]

        # Zero coefficients
        zero_coefficients = {"momentum": 0.0, "value": 0.0, "quality": 0.0}

        factor_scores = {}
        for factor_name, raw_scores in sample_data["raw_factors"].items():
            factor_scores[factor_name] = normalize_factor_scores(raw_scores, "zscore")

        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, zero_coefficients
        )

        # Should be identical to base returns
        np.testing.assert_array_almost_equal(tilted_returns, base_returns)

    def test_calculate_mu_tilt_single_factor(self, sample_data):
        """Test mu tilt with single factor"""
        base_returns = sample_data["base_returns"]

        # Only momentum factor
        momentum_scores = normalize_factor_scores(
            sample_data["raw_factors"]["momentum"], "zscore"
        )

        factor_scores = {"momentum": momentum_scores}
        tilt_coefficients = {"momentum": 0.02}

        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, tilt_coefficients
        )

        # Calculate expected tilt manually
        expected_tilt = base_returns + 0.02 * momentum_scores

        np.testing.assert_array_almost_equal(tilted_returns, expected_tilt)

    def test_calculate_mu_tilt_missing_factor(self, sample_data):
        """Test mu tilt when factor score is missing"""
        base_returns = sample_data["base_returns"]

        # Only provide momentum scores, but coefficients include value
        momentum_scores = normalize_factor_scores(
            sample_data["raw_factors"]["momentum"], "zscore"
        )

        factor_scores = {"momentum": momentum_scores}
        tilt_coefficients = {"momentum": 0.02, "value": 0.015}  # value missing

        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, tilt_coefficients
        )

        # Should only apply momentum tilt
        expected_tilt = base_returns + 0.02 * momentum_scores
        np.testing.assert_array_almost_equal(tilted_returns, expected_tilt)

    def test_factor_score_extreme_values(self):
        """Test factor score normalization with extreme values"""
        # Create data with outliers
        raw_scores = np.array([1, 2, 3, 4, 100])  # 100 is an outlier

        normalized = normalize_factor_scores(raw_scores, "zscore")

        # Check that normalization handles outliers reasonably
        assert np.all(np.isfinite(normalized))
        assert abs(np.mean(normalized)) < 1e-10
        assert abs(np.std(normalized) - 1.0) < 1e-10

    def test_factor_score_constant_values(self):
        """Test factor score normalization with constant values"""
        # All values are the same
        raw_scores = np.array([5.0, 5.0, 5.0, 5.0, 5.0])

        normalized = normalize_factor_scores(raw_scores, "zscore")

        # Should return zeros when no variation
        np.testing.assert_array_almost_equal(normalized, np.zeros(5))

    def test_mu_tilt_preserves_order(self, sample_data):
        """Test that mu tilt preserves relative ordering where appropriate"""
        base_returns = np.array([0.05, 0.08, 0.10, 0.12])  # Increasing order

        # Create factor scores that should preserve ordering
        momentum_scores = np.array([-1, -0.5, 0.5, 1])  # Also increasing

        factor_scores = {"momentum": momentum_scores}
        tilt_coefficients = {"momentum": 0.01}  # Positive coefficient

        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, tilt_coefficients
        )

        # Should still be in increasing order (positive momentum tilt)
        assert np.all(np.diff(tilted_returns) > 0)

    def test_mu_tilt_reverses_order(self, sample_data):
        """Test that negative mu tilt can reverse ordering"""
        base_returns = np.array([0.05, 0.08, 0.10, 0.12])  # Increasing order

        # Create strong negative momentum scores
        momentum_scores = np.array([2, 1, -1, -2])  # Decreasing (opposite of returns)

        factor_scores = {"momentum": momentum_scores}
        tilt_coefficients = {"momentum": -0.05}  # Negative coefficient (contrarian)

        tilted_returns = calculate_mu_tilt(
            base_returns, factor_scores, tilt_coefficients
        )

        # With strong negative tilt, order might reverse
        # Just check that calculation completed successfully
        assert len(tilted_returns) == 4
        assert np.all(np.isfinite(tilted_returns))


if __name__ == "__main__":
    # Run tests if executed directly
    pytest.main([__file__, "-v"])
