"""Policy Engine for Financial Advisor.

This module implements policy enforcement logic for investment constraints including
country limits, theme limits, blacklist/whitelist mechanisms, and ESG constraints.
"""

import yaml
import os
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Investment:
    """Represents an investment security."""
    symbol: str
    name: str
    country: str
    sector: str
    theme: str
    allocation: float  # Percentage allocation in portfolio
    esg_score: float  # ESG score (0-10)
    carbon_intensity: float  # tCO2e/$M revenue
    board_diversity: float  # Percentage women on board


@dataclass
class PolicyViolation:
    """Represents a policy violation."""
    type: str
    description: str
    severity: str  # 'minor', 'major', 'critical'
    current_value: Optional[float] = None
    limit_value: Optional[float] = None


class PolicyEngine:
    """Enforces investment policies based on configuration."""
    
    def __init__(self, policy_file_path: str = None):
        """Initialize policy engine with configuration.
        
        Args:
            policy_file_path: Path to policy YAML file. Defaults to docs/policies.yaml
        """
        if policy_file_path is None:
            # Default to docs/policies.yaml relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            policy_file_path = os.path.join(project_root, 'docs', 'policies.yaml')
        
        self.policy_file_path = policy_file_path
        self.policies = self._load_policies()
    
    def _load_policies(self) -> Dict[str, Any]:
        """Load policy configuration from YAML file."""
        try:
            with open(self.policy_file_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Policy file not found: {self.policy_file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in policy file: {e}")
    
    def validate_portfolio(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Validate a portfolio against all policies.
        
        Args:
            investments: List of Investment objects representing the portfolio
            
        Returns:
            List of PolicyViolation objects for any violations found
        """
        violations = []
        
        # Check country limits
        violations.extend(self._check_country_limits(investments))
        
        # Check theme limits
        violations.extend(self._check_theme_limits(investments))
        
        # Check blacklist/whitelist
        violations.extend(self._check_security_lists(investments))
        
        # Check ESG constraints
        violations.extend(self._check_esg_constraints(investments))
        
        # Check risk management constraints
        violations.extend(self._check_risk_management(investments))
        
        return violations
    
    def _check_country_limits(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Check country-based investment limits."""
        violations = []
        country_limits = self.policies.get('country_limits', {})
        
        # Calculate country allocations
        country_allocations = {}
        for investment in investments:
            country = investment.country
            country_allocations[country] = country_allocations.get(country, 0) + investment.allocation
        
        # Check maximum allocation per country
        max_allocation = country_limits.get('max_allocation_per_country', 100)
        for country, allocation in country_allocations.items():
            if allocation > max_allocation:
                violations.append(PolicyViolation(
                    type='country_limit',
                    description=f'Country {country} allocation ({allocation:.1f}%) exceeds maximum ({max_allocation:.1f}%)',
                    severity='major',
                    current_value=allocation,
                    limit_value=max_allocation
                ))
        
        # Check restricted countries
        restricted_countries = country_limits.get('restricted_countries', [])
        for country in restricted_countries:
            if country in country_allocations:
                violations.append(PolicyViolation(
                    type='restricted_country',
                    description=f'Investment in restricted country: {country}',
                    severity='critical'
                ))
        
        # Check minimum diversification
        min_countries = country_limits.get('min_countries', 1)
        if len(country_allocations) < min_countries:
            violations.append(PolicyViolation(
                type='country_diversification',
                description=f'Portfolio has {len(country_allocations)} countries, minimum required: {min_countries}',
                severity='major',
                current_value=len(country_allocations),
                limit_value=min_countries
            ))
        
        return violations
    
    def _check_theme_limits(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Check theme-based investment limits."""
        violations = []
        theme_limits = self.policies.get('theme_limits', {})
        
        # Calculate theme allocations
        theme_allocations = {}
        for investment in investments:
            theme = investment.theme
            theme_allocations[theme] = theme_allocations.get(theme, 0) + investment.allocation
        
        # Check maximum allocation per theme
        max_allocation = theme_limits.get('max_allocation_per_theme', 100)
        for theme, allocation in theme_allocations.items():
            if allocation > max_allocation:
                violations.append(PolicyViolation(
                    type='theme_limit',
                    description=f'Theme {theme} allocation ({allocation:.1f}%) exceeds maximum ({max_allocation:.1f}%)',
                    severity='major',
                    current_value=allocation,
                    limit_value=max_allocation
                ))
        
        # Check restricted themes
        restricted_themes = theme_limits.get('restricted_themes', [])
        for theme in restricted_themes:
            if theme in theme_allocations:
                violations.append(PolicyViolation(
                    type='restricted_theme',
                    description=f'Investment in restricted theme: {theme}',
                    severity='critical'
                ))
        
        # Check required themes
        required_themes = theme_limits.get('required_themes', {})
        for theme, requirements in required_themes.items():
            min_allocation = requirements.get('min_allocation', 0)
            current_allocation = theme_allocations.get(theme, 0)
            if current_allocation < min_allocation:
                violations.append(PolicyViolation(
                    type='required_theme',
                    description=f'Theme {theme} allocation ({current_allocation:.1f}%) below minimum ({min_allocation:.1f}%)',
                    severity='major',
                    current_value=current_allocation,
                    limit_value=min_allocation
                ))
        
        return violations
    
    def _check_security_lists(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Check blacklist and whitelist constraints."""
        violations = []
        security_lists = self.policies.get('security_lists', {})
        
        # Check blacklist
        blacklist = security_lists.get('blacklist', {})
        
        # Check blacklisted companies
        blacklisted_companies = blacklist.get('companies', [])
        for investment in investments:
            if investment.symbol in blacklisted_companies or investment.name in blacklisted_companies:
                violations.append(PolicyViolation(
                    type='blacklisted_security',
                    description=f'Investment in blacklisted company: {investment.symbol}',
                    severity='critical'
                ))
        
        # Check blacklisted sectors
        blacklisted_sectors = blacklist.get('sectors', [])
        for investment in investments:
            if investment.sector in blacklisted_sectors:
                violations.append(PolicyViolation(
                    type='blacklisted_sector',
                    description=f'Investment in blacklisted sector: {investment.sector}',
                    severity='critical'
                ))
        
        # Check ESG blacklist
        esg_blacklist = blacklist.get('esg_blacklist', {})
        min_esg_score = esg_blacklist.get('min_esg_score', 0)
        for investment in investments:
            if investment.esg_score < min_esg_score:
                violations.append(PolicyViolation(
                    type='esg_blacklist',
                    description=f'Investment {investment.symbol} ESG score ({investment.esg_score:.1f}) below minimum ({min_esg_score:.1f})',
                    severity='major',
                    current_value=investment.esg_score,
                    limit_value=min_esg_score
                ))
        
        return violations
    
    def _check_esg_constraints(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Check ESG (Environmental, Social, Governance) constraints."""
        violations = []
        esg_constraints = self.policies.get('esg_constraints', {})
        
        if not investments:
            return violations
        
        # Check portfolio-level ESG requirements
        portfolio_reqs = esg_constraints.get('portfolio_requirements', {})
        
        # Calculate weighted average ESG score
        total_allocation = sum(inv.allocation for inv in investments)
        if total_allocation > 0:
            avg_esg_score = sum(inv.esg_score * inv.allocation for inv in investments) / total_allocation
            min_esg_score = portfolio_reqs.get('min_avg_esg_score', 0)
            if avg_esg_score < min_esg_score:
                violations.append(PolicyViolation(
                    type='portfolio_esg_score',
                    description=f'Portfolio average ESG score ({avg_esg_score:.1f}) below minimum ({min_esg_score:.1f})',
                    severity='major',
                    current_value=avg_esg_score,
                    limit_value=min_esg_score
                ))
        
        # Calculate weighted average carbon intensity
        if total_allocation > 0:
            avg_carbon_intensity = sum(inv.carbon_intensity * inv.allocation for inv in investments) / total_allocation
            max_carbon_intensity = portfolio_reqs.get('max_carbon_intensity', float('inf'))
            if avg_carbon_intensity > max_carbon_intensity:
                violations.append(PolicyViolation(
                    type='carbon_intensity',
                    description=f'Portfolio carbon intensity ({avg_carbon_intensity:.1f}) exceeds maximum ({max_carbon_intensity:.1f})',
                    severity='major',
                    current_value=avg_carbon_intensity,
                    limit_value=max_carbon_intensity
                ))
        
        # Calculate weighted average board diversity
        if total_allocation > 0:
            avg_board_diversity = sum(inv.board_diversity * inv.allocation for inv in investments) / total_allocation
            min_board_diversity = portfolio_reqs.get('min_board_diversity', 0)
            if avg_board_diversity < min_board_diversity:
                violations.append(PolicyViolation(
                    type='board_diversity',
                    description=f'Portfolio board diversity ({avg_board_diversity:.1f}%) below minimum ({min_board_diversity:.1f}%)',
                    severity='minor',
                    current_value=avg_board_diversity,
                    limit_value=min_board_diversity
                ))
        
        return violations
    
    def _check_risk_management(self, investments: List[Investment]) -> List[PolicyViolation]:
        """Check risk management constraints."""
        violations = []
        risk_mgmt = self.policies.get('risk_management', {})
        
        # Check maximum single security allocation
        max_single_security = risk_mgmt.get('max_single_security', 100)
        for investment in investments:
            if investment.allocation > max_single_security:
                violations.append(PolicyViolation(
                    type='single_security_limit',
                    description=f'Security {investment.symbol} allocation ({investment.allocation:.1f}%) exceeds maximum ({max_single_security:.1f}%)',
                    severity='major',
                    current_value=investment.allocation,
                    limit_value=max_single_security
                ))
        
        # Check sector concentration
        max_sector_concentration = risk_mgmt.get('max_sector_concentration', 100)
        sector_allocations = {}
        for investment in investments:
            sector = investment.sector
            sector_allocations[sector] = sector_allocations.get(sector, 0) + investment.allocation
        
        for sector, allocation in sector_allocations.items():
            if allocation > max_sector_concentration:
                violations.append(PolicyViolation(
                    type='sector_concentration',
                    description=f'Sector {sector} allocation ({allocation:.1f}%) exceeds maximum ({max_sector_concentration:.1f}%)',
                    severity='major',
                    current_value=allocation,
                    limit_value=max_sector_concentration
                ))
        
        return violations
    
    def is_security_allowed(self, symbol: str, sector: str, esg_score: float) -> Tuple[bool, str]:
        """Check if a security is allowed based on blacklist/whitelist.
        
        Args:
            symbol: Security symbol
            sector: Security sector
            esg_score: ESG score of the security
            
        Returns:
            Tuple of (is_allowed, reason)
        """
        security_lists = self.policies.get('security_lists', {})
        
        # Check blacklist first
        blacklist = security_lists.get('blacklist', {})
        
        # Check blacklisted companies
        if symbol in blacklist.get('companies', []):
            return False, f"Security {symbol} is blacklisted"
        
        # Check blacklisted sectors
        if sector in blacklist.get('sectors', []):
            return False, f"Sector {sector} is blacklisted"
        
        # Check ESG blacklist
        esg_blacklist = blacklist.get('esg_blacklist', {})
        min_esg_score = esg_blacklist.get('min_esg_score', 0)
        if esg_score < min_esg_score:
            return False, f"ESG score {esg_score} below minimum {min_esg_score}"
        
        return True, "Security is allowed"
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """Get a summary of all loaded policies."""
        return {
            'version': self.policies.get('version', 'unknown'),
            'country_limits': {
                'max_allocation_per_country': self.policies.get('country_limits', {}).get('max_allocation_per_country'),
                'restricted_countries_count': len(self.policies.get('country_limits', {}).get('restricted_countries', [])),
                'min_countries': self.policies.get('country_limits', {}).get('min_countries')
            },
            'theme_limits': {
                'max_allocation_per_theme': self.policies.get('theme_limits', {}).get('max_allocation_per_theme'),
                'restricted_themes_count': len(self.policies.get('theme_limits', {}).get('restricted_themes', [])),
                'required_themes_count': len(self.policies.get('theme_limits', {}).get('required_themes', {}))
            },
            'esg_constraints': {
                'min_avg_esg_score': self.policies.get('esg_constraints', {}).get('portfolio_requirements', {}).get('min_avg_esg_score'),
                'max_carbon_intensity': self.policies.get('esg_constraints', {}).get('portfolio_requirements', {}).get('max_carbon_intensity')
            }
        }