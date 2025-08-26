# Financial Advisor User Guide

This guide provides detailed instructions on using the Financial Advisor policy-based investment system.

## Table of Contents

1. [Overview](#overview)
2. [Installation and Setup](#installation-and-setup)
3. [Policy Configuration](#policy-configuration)
4. [Using the Policy Engine](#using-the-policy-engine)
5. [Investment Data Structure](#investment-data-structure)
6. [Policy Violation Types](#policy-violation-types)
7. [Examples](#examples)
8. [Best Practices](#best-practices)

## Overview

The Financial Advisor system enforces investment policies to ensure portfolios comply with:

- **Country allocation limits** and geographic diversification requirements
- **Theme-based investment constraints** for sector and strategy alignment
- **Blacklist/whitelist mechanisms** for security screening
- **ESG (Environmental, Social, Governance) criteria** for sustainable investing
- **Risk management constraints** for portfolio risk control

## Installation and Setup

### Prerequisites

- Python 3.7 or higher
- PyYAML library

### Installation

1. Clone or download the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Basic Setup

```python
from financial_advisor.policy_engine import PolicyEngine

# Use default policy file (docs/policies.yaml)
policy_engine = PolicyEngine()

# Or specify a custom policy file
policy_engine = PolicyEngine('/path/to/custom/policies.yaml')
```

## Policy Configuration

Policies are defined in YAML format. The main policy file is `docs/policies.yaml`.

### Policy Structure

```yaml
version: "1.0"
country_limits: { ... }
theme_limits: { ... }
security_lists: { ... }
esg_constraints: { ... }
risk_management: { ... }
compliance: { ... }
```

### Country Limits

Configure geographic investment constraints:

```yaml
country_limits:
  max_allocation_per_country: 25.0    # Maximum % allocation per country
  preferred_countries:                # Countries with higher allocation allowed
    - "US"
    - "UK"
  restricted_countries:               # Countries to avoid or limit
    - "RU"
    - "IR"
  min_countries: 3                    # Minimum number of countries for diversification
```

### Theme Limits

Define investment theme constraints:

```yaml
theme_limits:
  max_allocation_per_theme: 30.0      # Maximum % allocation per theme
  preferred_themes:                   # Encouraged investment themes
    - "technology"
    - "healthcare"
  restricted_themes:                  # Themes to avoid
    - "fossil_fuels"
    - "tobacco"
  required_themes:                    # Mandatory minimum exposures
    renewable_energy:
      min_allocation: 5.0
    technology:
      min_allocation: 10.0
```

### Security Lists (Blacklist/Whitelist)

Configure security screening:

```yaml
security_lists:
  blacklist:
    companies:                        # Specific companies to avoid
      - "COMPANY_A"
    sectors:                          # Sectors to avoid
      - "tobacco_manufacturing"
    esg_blacklist:                    # ESG-based exclusions
      min_esg_score: 3.0
  
  whitelist:
    companies:                        # Preferred companies
      - "AAPL"
      - "MSFT"
    sectors:                          # Preferred sectors
      - "renewable_energy"
    esg_whitelist:                    # High ESG securities
      min_esg_score: 8.0
```

### ESG Constraints

Define sustainability requirements:

```yaml
esg_constraints:
  portfolio_requirements:
    min_avg_esg_score: 6.0           # Minimum portfolio ESG score
    max_carbon_intensity: 150.0      # Maximum carbon intensity
    min_board_diversity: 30.0        # Minimum % women on boards
  
  environmental:
    carbon_limits:
      max_scope1_emissions: 1000000
      max_scope2_emissions: 500000
    renewable_energy_min: 50.0
  
  social:
    labor_standards:
      no_child_labor: true
      fair_wages: true
    community_investment_min: 1.0
  
  governance:
    board_independence_min: 50.0
    ceo_pay_ratio_max: 300
    anti_corruption_policy: true
```

## Using the Policy Engine

### Creating Investment Objects

```python
from financial_advisor.policy_engine import Investment

investment = Investment(
    symbol='AAPL',                    # Stock symbol
    name='Apple Inc.',                # Company name
    country='US',                     # Country of incorporation
    sector='technology',              # Business sector
    theme='technology',               # Investment theme
    allocation=15.0,                  # Portfolio allocation %
    esg_score=8.5,                    # ESG score (0-10)
    carbon_intensity=50.0,            # tCO2e/$M revenue
    board_diversity=40.0              # % women on board
)
```

### Portfolio Validation

```python
# Create a list of investments
portfolio = [
    Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 15.0, 8.5, 50.0, 40.0),
    Investment('MSFT', 'Microsoft Corp.', 'US', 'technology', 'technology', 10.0, 8.0, 45.0, 35.0),
    Investment('TSLA', 'Tesla Inc.', 'US', 'automotive', 'renewable_energy', 8.0, 7.5, 200.0, 25.0),
]

# Validate against all policies
violations = policy_engine.validate_portfolio(portfolio)

# Process violations
for violation in violations:
    print(f"{violation.severity.upper()}: {violation.description}")
    if violation.current_value and violation.limit_value:
        print(f"  Current: {violation.current_value}, Limit: {violation.limit_value}")
```

### Individual Security Screening

```python
# Check if a security is allowed
is_allowed, reason = policy_engine.is_security_allowed(
    symbol='AAPL',
    sector='technology',
    esg_score=8.5
)

if is_allowed:
    print("Security is allowed for investment")
else:
    print(f"Security rejected: {reason}")
```

### Policy Summary

```python
# Get an overview of loaded policies
summary = policy_engine.get_policy_summary()
print(f"Policy version: {summary['version']}")
print(f"Max country allocation: {summary['country_limits']['max_allocation_per_country']}%")
print(f"Min ESG score: {summary['esg_constraints']['min_avg_esg_score']}")
```

## Investment Data Structure

The `Investment` class represents a security with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | str | Security identifier (e.g., "AAPL") |
| `name` | str | Full company name |
| `country` | str | Country of incorporation |
| `sector` | str | Business sector classification |
| `theme` | str | Investment theme category |
| `allocation` | float | Portfolio allocation percentage |
| `esg_score` | float | ESG score (0-10 scale) |
| `carbon_intensity` | float | Carbon intensity (tCO2e/$M revenue) |
| `board_diversity` | float | Percentage of women on board |

## Policy Violation Types

The system identifies the following violation types:

### Country-Related Violations

- `country_limit`: Country allocation exceeds maximum limit
- `restricted_country`: Investment in a restricted country
- `country_diversification`: Insufficient geographic diversification

### Theme-Related Violations

- `theme_limit`: Theme allocation exceeds maximum limit
- `restricted_theme`: Investment in a restricted theme
- `required_theme`: Missing required theme allocation

### Security List Violations

- `blacklisted_security`: Investment in blacklisted company
- `blacklisted_sector`: Investment in blacklisted sector
- `esg_blacklist`: Security below minimum ESG threshold

### ESG Violations

- `portfolio_esg_score`: Portfolio ESG score below minimum
- `carbon_intensity`: Portfolio carbon intensity too high
- `board_diversity`: Portfolio board diversity below minimum

### Risk Management Violations

- `single_security_limit`: Individual security allocation too high
- `sector_concentration`: Sector concentration exceeds limit

### Violation Severity Levels

- **Critical**: Immediate action required (e.g., blacklisted securities)
- **Major**: Significant policy breach requiring attention
- **Minor**: Minor deviations that should be monitored

## Examples

### Example 1: Basic Portfolio Validation

```python
from financial_advisor.policy_engine import PolicyEngine, Investment

# Initialize policy engine
policy_engine = PolicyEngine()

# Create a diversified portfolio
portfolio = [
    Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 20.0, 8.5, 50.0, 40.0),
    Investment('SAP', 'SAP SE', 'DE', 'technology', 'technology', 15.0, 7.0, 60.0, 30.0),
    Investment('NESN', 'Nestle SA', 'CH', 'consumer_goods', 'consumer_goods', 25.0, 6.5, 80.0, 20.0),
    Investment('NEE', 'NextEra Energy', 'US', 'utilities', 'renewable_energy', 10.0, 9.0, 30.0, 45.0),
]

# Validate portfolio
violations = policy_engine.validate_portfolio(portfolio)

if not violations:
    print("Portfolio passes all policy checks!")
else:
    print(f"Found {len(violations)} policy violations:")
    for violation in violations:
        print(f"  - {violation.type}: {violation.description}")
```

### Example 2: ESG-Focused Portfolio

```python
# Create an ESG-focused portfolio
esg_portfolio = [
    Investment('NEE', 'NextEra Energy', 'US', 'utilities', 'renewable_energy', 15.0, 9.2, 25.0, 50.0),
    Investment('JNJ', 'Johnson & Johnson', 'US', 'healthcare', 'healthcare', 20.0, 8.8, 40.0, 45.0),
    Investment('MSFT', 'Microsoft Corp.', 'US', 'technology', 'technology', 25.0, 8.5, 35.0, 40.0),
    Investment('UNH', 'UnitedHealth Group', 'US', 'healthcare', 'healthcare', 15.0, 7.8, 45.0, 38.0),
]

violations = policy_engine.validate_portfolio(esg_portfolio)

# Check portfolio ESG metrics
total_allocation = sum(inv.allocation for inv in esg_portfolio)
avg_esg_score = sum(inv.esg_score * inv.allocation for inv in esg_portfolio) / total_allocation
avg_carbon_intensity = sum(inv.carbon_intensity * inv.allocation for inv in esg_portfolio) / total_allocation

print(f"Portfolio average ESG score: {avg_esg_score:.2f}")
print(f"Portfolio carbon intensity: {avg_carbon_intensity:.2f}")
```

### Example 3: Security Screening

```python
# Screen potential investments
candidates = [
    ('AAPL', 'technology', 8.5),
    ('EVIL_CORP', 'tobacco_manufacturing', 2.0),
    ('CLEAN_ENERGY', 'renewable_energy', 9.0),
]

for symbol, sector, esg_score in candidates:
    is_allowed, reason = policy_engine.is_security_allowed(symbol, sector, esg_score)
    status = "✓ ALLOWED" if is_allowed else "✗ REJECTED"
    print(f"{symbol}: {status} - {reason}")
```

## Best Practices

### 1. Portfolio Construction

- Start with policy-compliant building blocks
- Regularly validate portfolios during construction
- Use the security screening function before adding new positions
- Monitor violation severity levels and prioritize critical issues

### 2. Policy Management

- Review and update policies quarterly
- Test policy changes with historical portfolios
- Document policy rationales for compliance purposes
- Version control policy files for audit trails

### 3. ESG Integration

- Set realistic ESG targets based on investment universe
- Balance ESG requirements with return objectives
- Monitor ESG trends and adjust thresholds accordingly
- Consider ESG data quality and coverage limitations

### 4. Risk Management

- Implement pre-trade compliance checks
- Set up automated monitoring for policy violations
- Establish clear escalation procedures for violations
- Regular stress testing of policy constraints

### 5. Performance Monitoring

- Track policy violation trends over time
- Measure impact of policy constraints on returns
- Benchmark against policy-unconstrained portfolios
- Report compliance metrics to stakeholders

## Troubleshooting

### Common Issues

1. **Policy file not found**: Ensure the policy file path is correct
2. **YAML parsing errors**: Validate YAML syntax
3. **Missing ESG data**: Handle missing data appropriately in investment objects
4. **Performance impact**: Optimize for large portfolios by caching policy checks

### Error Handling

The system provides clear error messages for:
- Invalid policy file formats
- Missing required policy parameters
- Invalid investment data
- Policy configuration conflicts

For additional support or customization requirements, refer to the source code documentation in the `financial_advisor/policy_engine.py` module.