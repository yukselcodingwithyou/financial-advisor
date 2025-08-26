"""Unit tests for the Policy Engine."""

import unittest
import os
import tempfile
import yaml
from financial_advisor.policy_engine import PolicyEngine, Investment, PolicyViolation


class TestPolicyEngine(unittest.TestCase):
    """Test cases for PolicyEngine class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample policy configuration for testing
        self.test_policies = {
            'version': '1.0',
            'country_limits': {
                'max_allocation_per_country': 25.0,
                'restricted_countries': ['RU', 'IR'],
                'min_countries': 3
            },
            'theme_limits': {
                'max_allocation_per_theme': 30.0,
                'restricted_themes': ['tobacco', 'weapons'],
                'required_themes': {
                    'renewable_energy': {'min_allocation': 5.0},
                    'technology': {'min_allocation': 10.0}
                }
            },
            'security_lists': {
                'blacklist': {
                    'companies': ['EVIL_CORP'],
                    'sectors': ['tobacco_manufacturing'],
                    'esg_blacklist': {'min_esg_score': 3.0}
                },
                'whitelist': {
                    'companies': ['AAPL', 'MSFT'],
                    'sectors': ['renewable_energy'],
                    'esg_whitelist': {'min_esg_score': 8.0}
                }
            },
            'esg_constraints': {
                'portfolio_requirements': {
                    'min_avg_esg_score': 6.0,
                    'max_carbon_intensity': 150.0,
                    'min_board_diversity': 30.0
                }
            },
            'risk_management': {
                'max_single_security': 5.0,
                'max_sector_concentration': 35.0
            }
        }
        
        # Create temporary policy file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml.dump(self.test_policies, self.temp_file)
        self.temp_file.close()
        
        # Initialize policy engine with test configuration
        self.policy_engine = PolicyEngine(self.temp_file.name)
        
        # Create sample investments for testing
        self.sample_investments = [
            Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 15.0, 8.5, 50.0, 40.0),
            Investment('MSFT', 'Microsoft Corp.', 'US', 'technology', 'technology', 10.0, 8.0, 45.0, 35.0),
            Investment('TSLA', 'Tesla Inc.', 'US', 'automotive', 'renewable_energy', 8.0, 7.5, 200.0, 25.0),
            Investment('SAP', 'SAP SE', 'DE', 'technology', 'technology', 12.0, 7.0, 60.0, 30.0),
            Investment('NESN', 'Nestle SA', 'CH', 'consumer_goods', 'consumer_goods', 20.0, 6.5, 80.0, 20.0),
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_file.name)
    
    def test_policy_loading(self):
        """Test that policies are loaded correctly."""
        self.assertEqual(self.policy_engine.policies['version'], '1.0')
        self.assertEqual(self.policy_engine.policies['country_limits']['max_allocation_per_country'], 25.0)
        self.assertIn('RU', self.policy_engine.policies['country_limits']['restricted_countries'])
    
    def test_policy_summary(self):
        """Test policy summary generation."""
        summary = self.policy_engine.get_policy_summary()
        self.assertEqual(summary['version'], '1.0')
        self.assertEqual(summary['country_limits']['max_allocation_per_country'], 25.0)
        self.assertEqual(summary['theme_limits']['max_allocation_per_theme'], 30.0)
    
    def test_country_limits_validation(self):
        """Test country limits validation."""
        # Create investments that violate country limits
        violations_investments = [
            Investment('US1', 'US Company 1', 'US', 'tech', 'technology', 30.0, 8.0, 50.0, 40.0),  # Exceeds 25% limit
            Investment('RU1', 'Russian Company', 'RU', 'energy', 'energy', 5.0, 6.0, 300.0, 10.0),  # Restricted country
        ]
        
        violations = self.policy_engine._check_country_limits(violations_investments)
        
        # Should have violations for country limit, restricted country, and diversification (only 2 countries, needs 3)
        self.assertEqual(len(violations), 3)
        violation_types = [v.type for v in violations]
        self.assertIn('country_limit', violation_types)
        self.assertIn('restricted_country', violation_types)
        self.assertIn('country_diversification', violation_types)
    
    def test_theme_limits_validation(self):
        """Test theme limits validation."""
        # Create investments that violate theme limits
        violations_investments = [
            Investment('TOB1', 'Tobacco Company', 'US', 'tobacco', 'tobacco', 10.0, 2.0, 100.0, 15.0),  # Restricted theme
            Investment('TECH1', 'Tech Company', 'US', 'technology', 'technology', 35.0, 8.0, 50.0, 40.0),  # Exceeds 30% limit
        ]
        
        violations = self.policy_engine._check_theme_limits(violations_investments)
        
        # Should have violations for restricted theme, theme limit, and missing required renewable_energy theme
        self.assertEqual(len(violations), 3)
        violation_types = [v.type for v in violations]
        self.assertIn('restricted_theme', violation_types)
        self.assertIn('theme_limit', violation_types)
        self.assertIn('required_theme', violation_types)
    
    def test_required_themes_validation(self):
        """Test required themes validation."""
        # Create investments without required themes
        insufficient_investments = [
            Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 15.0, 8.0, 50.0, 40.0),
            # Missing renewable_energy (requires 5%) and insufficient technology (requires 10%, only has 15% but need more)
        ]
        
        violations = self.policy_engine._check_theme_limits(insufficient_investments)
        
        # Should have violation for missing renewable energy theme
        required_theme_violations = [v for v in violations if v.type == 'required_theme']
        self.assertTrue(len(required_theme_violations) > 0)
    
    def test_security_blacklist_validation(self):
        """Test security blacklist validation."""
        # Create investments with blacklisted securities
        blacklist_investments = [
            Investment('EVIL_CORP', 'Evil Corporation', 'US', 'tobacco_manufacturing', 'tobacco', 10.0, 2.0, 500.0, 5.0),
        ]
        
        violations = self.policy_engine._check_security_lists(blacklist_investments)
        
        # Should have violations for blacklisted company and sector
        self.assertTrue(len(violations) >= 2)
        violation_types = [v.type for v in violations]
        self.assertIn('blacklisted_security', violation_types)
        self.assertIn('blacklisted_sector', violation_types)
    
    def test_esg_constraints_validation(self):
        """Test ESG constraints validation."""
        # Create investments with poor ESG scores
        poor_esg_investments = [
            Investment('POOR1', 'Poor ESG Company 1', 'US', 'energy', 'fossil_fuels', 30.0, 2.0, 400.0, 10.0),
            Investment('POOR2', 'Poor ESG Company 2', 'US', 'energy', 'fossil_fuels', 40.0, 3.0, 350.0, 15.0),
        ]
        
        violations = self.policy_engine._check_esg_constraints(poor_esg_investments)
        
        # Should have violations for low portfolio ESG score and high carbon intensity
        self.assertTrue(len(violations) >= 1)
        violation_types = [v.type for v in violations]
        self.assertIn('portfolio_esg_score', violation_types)
    
    def test_risk_management_validation(self):
        """Test risk management constraints validation."""
        # Create investments that violate risk limits
        risky_investments = [
            Investment('BIG1', 'Big Position', 'US', 'technology', 'technology', 10.0, 8.0, 50.0, 40.0),  # Exceeds 5% single security limit
            Investment('TECH1', 'Tech Company 1', 'US', 'technology', 'technology', 20.0, 8.0, 50.0, 40.0),
            Investment('TECH2', 'Tech Company 2', 'US', 'technology', 'technology', 20.0, 8.0, 50.0, 40.0),  # Combined tech exceeds 35% sector limit
        ]
        
        violations = self.policy_engine._check_risk_management(risky_investments)
        
        # Should have violations for single security and sector concentration
        self.assertTrue(len(violations) >= 2)
        violation_types = [v.type for v in violations]
        self.assertIn('single_security_limit', violation_types)
        self.assertIn('sector_concentration', violation_types)
    
    def test_portfolio_validation_comprehensive(self):
        """Test comprehensive portfolio validation."""
        # Use sample investments that should pass most checks
        violations = self.policy_engine.validate_portfolio(self.sample_investments)
        
        # Sample portfolio should have minimal violations (maybe missing some required themes)
        self.assertIsInstance(violations, list)
        
        # All violations should be PolicyViolation objects
        for violation in violations:
            self.assertIsInstance(violation, PolicyViolation)
            self.assertIn(violation.type, [
                'country_limit', 'restricted_country', 'country_diversification',
                'theme_limit', 'restricted_theme', 'required_theme',
                'blacklisted_security', 'blacklisted_sector', 'esg_blacklist',
                'portfolio_esg_score', 'carbon_intensity', 'board_diversity',
                'single_security_limit', 'sector_concentration'
            ])
            self.assertIn(violation.severity, ['minor', 'major', 'critical'])
    
    def test_security_allowed_check(self):
        """Test individual security allowance checking."""
        # Test allowed security
        is_allowed, reason = self.policy_engine.is_security_allowed('AAPL', 'technology', 8.0)
        self.assertTrue(is_allowed)
        
        # Test blacklisted security
        is_allowed, reason = self.policy_engine.is_security_allowed('EVIL_CORP', 'technology', 8.0)
        self.assertFalse(is_allowed)
        self.assertIn('blacklisted', reason)
        
        # Test blacklisted sector
        is_allowed, reason = self.policy_engine.is_security_allowed('SOME_COMPANY', 'tobacco_manufacturing', 8.0)
        self.assertFalse(is_allowed)
        self.assertIn('blacklisted', reason)
        
        # Test low ESG score
        is_allowed, reason = self.policy_engine.is_security_allowed('LOW_ESG', 'technology', 2.0)
        self.assertFalse(is_allowed)
        self.assertIn('ESG score', reason)
    
    def test_empty_portfolio(self):
        """Test validation of empty portfolio."""
        violations = self.policy_engine.validate_portfolio([])
        
        # Empty portfolio should have violations for minimum country diversification and required themes
        self.assertTrue(len(violations) > 0)
        violation_types = [v.type for v in violations]
        self.assertIn('country_diversification', violation_types)
    
    def test_policy_file_not_found(self):
        """Test handling of missing policy file."""
        with self.assertRaises(FileNotFoundError):
            PolicyEngine('/nonexistent/path/policies.yaml')
    
    def test_invalid_yaml_file(self):
        """Test handling of invalid YAML file."""
        # Create invalid YAML file
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        invalid_file.write('invalid: yaml: content: [unclosed')
        invalid_file.close()
        
        try:
            with self.assertRaises(ValueError):
                PolicyEngine(invalid_file.name)
        finally:
            os.unlink(invalid_file.name)


class TestInvestmentClass(unittest.TestCase):
    """Test cases for Investment dataclass."""
    
    def test_investment_creation(self):
        """Test Investment object creation."""
        investment = Investment(
            symbol='AAPL',
            name='Apple Inc.',
            country='US',
            sector='technology',
            theme='technology',
            allocation=15.0,
            esg_score=8.5,
            carbon_intensity=50.0,
            board_diversity=40.0
        )
        
        self.assertEqual(investment.symbol, 'AAPL')
        self.assertEqual(investment.allocation, 15.0)
        self.assertEqual(investment.esg_score, 8.5)


class TestPolicyViolationClass(unittest.TestCase):
    """Test cases for PolicyViolation dataclass."""
    
    def test_policy_violation_creation(self):
        """Test PolicyViolation object creation."""
        violation = PolicyViolation(
            type='country_limit',
            description='Country allocation exceeds limit',
            severity='major',
            current_value=30.0,
            limit_value=25.0
        )
        
        self.assertEqual(violation.type, 'country_limit')
        self.assertEqual(violation.severity, 'major')
        self.assertEqual(violation.current_value, 30.0)
        self.assertEqual(violation.limit_value, 25.0)


if __name__ == '__main__':
    unittest.main()