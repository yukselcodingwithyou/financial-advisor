import pytest
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the feast_repo directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../advanced/feast_repo'))

from feature_views import esg_feature_view, credit_feature_view, macro_feature_view, company, country


class TestESGFeatureView:
    """Test suite for ESG feature view configuration"""
    
    def test_esg_feature_view_name(self):
        """Test that ESG feature view has correct name"""
        assert esg_feature_view.name == "esg_indicators"
    
    def test_esg_feature_view_entities(self):
        """Test that ESG feature view has correct entities"""
        assert len(esg_feature_view.entities) == 1
        assert esg_feature_view.entities[0] == "company"
    
    def test_esg_feature_view_schema(self):
        """Test that ESG feature view has expected fields"""
        field_names = [field.name for field in esg_feature_view.schema]
        expected_fields = [
            "environmental_score", "social_score", "governance_score",
            "overall_esg_score", "esg_rating", "carbon_intensity",
            "renewable_energy_percentage", "employee_satisfaction_score",
            "board_diversity_percentage", "esg_category", "is_green_leader",
            "weighted_esg_score"
        ]
        for field in expected_fields:
            assert field in field_names, f"Field {field} missing from ESG feature view"
    
    def test_esg_feature_view_ttl(self):
        """Test that ESG feature view has reasonable TTL"""
        assert esg_feature_view.ttl == timedelta(days=1)


class TestCreditFeatureView:
    """Test suite for Credit feature view configuration"""
    
    def test_credit_feature_view_name(self):
        """Test that Credit feature view has correct name"""
        assert credit_feature_view.name == "credit_indicators"
    
    def test_credit_feature_view_entities(self):
        """Test that Credit feature view has correct entities"""
        assert len(credit_feature_view.entities) == 1
        assert credit_feature_view.entities[0] == "company"
    
    def test_credit_feature_view_schema(self):
        """Test that Credit feature view has expected fields"""
        field_names = [field.name for field in credit_feature_view.schema]
        expected_fields = [
            "credit_rating", "credit_spread_bps", "debt_to_equity_ratio",
            "interest_coverage_ratio", "probability_of_default",
            "recovery_rate_percentage", "current_ratio", "quick_ratio",
            "debt_to_assets_ratio", "credit_quality_category",
            "default_risk_category", "is_liquid", "leverage_category",
            "credit_score"
        ]
        for field in expected_fields:
            assert field in field_names, f"Field {field} missing from Credit feature view"
    
    def test_credit_feature_view_ttl(self):
        """Test that Credit feature view has reasonable TTL"""
        assert credit_feature_view.ttl == timedelta(days=1)


class TestMacroFeatureView:
    """Test suite for Macro feature view configuration"""
    
    def test_macro_feature_view_name(self):
        """Test that Macro feature view has correct name"""
        assert macro_feature_view.name == "macro_indicators"
    
    def test_macro_feature_view_entities(self):
        """Test that Macro feature view has correct entities"""
        assert len(macro_feature_view.entities) == 1
        assert macro_feature_view.entities[0] == "country"
    
    def test_macro_feature_view_schema(self):
        """Test that Macro feature view has expected fields"""
        field_names = [field.name for field in macro_feature_view.schema]
        expected_fields = [
            "federal_funds_rate", "inflation_rate_yoy", "unemployment_rate",
            "gdp_growth_rate_yoy", "sp500_index", "usd_eur_exchange_rate",
            "gold_price_usd", "oil_price_wti", "treasury_10y_yield",
            "treasury_2y_yield", "consumer_confidence_index",
            "purchasing_managers_index", "yield_curve_spread",
            "yield_curve_shape", "real_interest_rate_status",
            "real_interest_rate", "economic_growth_phase",
            "employment_status", "consumer_sentiment", "manufacturing_activity"
        ]
        for field in expected_fields:
            assert field in field_names, f"Field {field} missing from Macro feature view"
    
    def test_macro_feature_view_ttl(self):
        """Test that Macro feature view has reasonable TTL"""
        assert macro_feature_view.ttl == timedelta(hours=6)


class TestEntities:
    """Test suite for entity definitions"""
    
    def test_company_entity(self):
        """Test company entity configuration"""
        assert company.name == "company"
        assert company.description == "Company symbol identifier"
    
    def test_country_entity(self):
        """Test country entity configuration"""
        assert country.name == "country"
        assert country.description == "Country code identifier"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])