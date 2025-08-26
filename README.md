# Financial Advisor

A policy-based investment guidance system that enforces comprehensive investment constraints including country limits, theme restrictions, blacklist/whitelist mechanisms, and ESG (Environmental, Social, Governance) criteria.

## Features

- **Country-based Limits**: Control investment allocation by country with maximum limits, preferred countries, and restricted countries
- **Theme-based Constraints**: Manage investments by themes with allocation limits and required minimum exposures
- **Blacklist/Whitelist Mechanisms**: Comprehensive security filtering based on companies, sectors, and ESG scores
- **ESG Constraints**: Environmental, Social, and Governance criteria enforcement for sustainable investing
- **Risk Management**: Portfolio-level risk controls including concentration limits and diversification requirements

## Quick Start

```python
from financial_advisor.policy_engine import PolicyEngine, Investment

# Initialize policy engine
policy_engine = PolicyEngine()

# Create sample investments
investments = [
    Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 15.0, 8.5, 50.0, 40.0),
    Investment('MSFT', 'Microsoft Corp.', 'US', 'technology', 'technology', 10.0, 8.0, 45.0, 35.0),
]

# Validate portfolio against policies
violations = policy_engine.validate_portfolio(investments)

# Check if a specific security is allowed
is_allowed, reason = policy_engine.is_security_allowed('AAPL', 'technology', 8.5)
```

## Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Policy Configuration

Policies are defined in `docs/policies.yaml`. The configuration includes:

- **Country Limits**: Maximum allocation per country, restricted countries, minimum diversification
- **Theme Limits**: Maximum allocation per theme, restricted themes, required minimum themes
- **Security Lists**: Blacklisted and whitelisted companies/sectors based on various criteria
- **ESG Constraints**: Environmental, social, and governance requirements
- **Risk Management**: Portfolio-level risk controls

## Testing

Run the test suite:

```bash
python -m unittest tests.test_policy_engine -v
```

## Documentation

For detailed usage instructions, see [USER_GUIDE.md](USER_GUIDE.md).

## Project Structure

```
financial-advisor/
├── financial_advisor/          # Main package
│   ├── __init__.py
│   └── policy_engine.py       # Policy enforcement logic
├── docs/
│   └── policies.yaml          # Policy configuration
├── tests/
│   ├── __init__.py
│   └── test_policy_engine.py  # Unit tests
├── requirements.txt           # Dependencies
├── README.md                  # This file
└── USER_GUIDE.md             # Detailed user guide
```