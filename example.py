#!/usr/bin/env python3
"""
Example script demonstrating the Financial Advisor policy enforcement system.

This script shows how to:
1. Load policy configuration
2. Create investment portfolios
3. Validate portfolios against policies
4. Handle policy violations
"""

from financial_advisor.policy_engine import PolicyEngine, Investment


def main():
    """Main demonstration function."""
    print("Financial Advisor Policy Engine Demo")
    print("=" * 40)
    
    # Initialize policy engine
    try:
        policy_engine = PolicyEngine()
        print("✓ Policy engine initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize policy engine: {e}")
        return
    
    # Display policy summary
    print("\nPolicy Summary:")
    summary = policy_engine.get_policy_summary()
    print(f"  Version: {summary['version']}")
    print(f"  Max country allocation: {summary['country_limits']['max_allocation_per_country']}%")
    print(f"  Max theme allocation: {summary['theme_limits']['max_allocation_per_theme']}%")
    print(f"  Min portfolio ESG score: {summary['esg_constraints']['min_avg_esg_score']}")
    
    # Example 1: Compliant Portfolio
    print("\n" + "="*50)
    print("Example 1: ESG-Compliant Diversified Portfolio")
    print("="*50)
    
    compliant_portfolio = [
        Investment('AAPL', 'Apple Inc.', 'US', 'technology', 'technology', 20.0, 8.5, 50.0, 40.0),
        Investment('SAP', 'SAP SE', 'DE', 'technology', 'technology', 15.0, 7.0, 60.0, 30.0),
        Investment('NEE', 'NextEra Energy', 'US', 'utilities', 'renewable_energy', 12.0, 9.0, 30.0, 45.0),
        Investment('JNJ', 'Johnson & Johnson', 'US', 'healthcare', 'healthcare', 18.0, 8.8, 40.0, 45.0),
        Investment('ASML', 'ASML Holding', 'NL', 'technology', 'technology', 10.0, 7.5, 55.0, 35.0),
    ]
    
    violations = policy_engine.validate_portfolio(compliant_portfolio)
    
    print(f"Portfolio summary:")
    for inv in compliant_portfolio:
        print(f"  {inv.symbol:6} | {inv.country:2} | {inv.allocation:5.1f}% | ESG: {inv.esg_score}")
    
    if not violations:
        print("\n✓ Portfolio PASSES all policy checks!")
    else:
        print(f"\n⚠ Found {len(violations)} policy violations:")
        for violation in violations:
            print(f"  {violation.severity.upper():8}: {violation.description}")
    
    # Example 2: Non-Compliant Portfolio
    print("\n" + "="*50)
    print("Example 2: Non-Compliant Portfolio with Violations")
    print("="*50)
    
    problematic_portfolio = [
        Investment('CONC1', 'Concentrated US Tech', 'US', 'technology', 'technology', 40.0, 8.0, 50.0, 40.0),  # Too concentrated
        Investment('EVIL_CORP', 'Evil Corporation', 'US', 'tobacco_manufacturing', 'tobacco', 15.0, 2.0, 500.0, 10.0),  # Blacklisted
        Investment('RU_STOCK', 'Russian Company', 'RU', 'energy', 'fossil_fuels', 20.0, 3.0, 800.0, 5.0),  # Restricted country
        Investment('POOR_ESG', 'Poor ESG Company', 'US', 'mining', 'mining', 25.0, 1.5, 1000.0, 8.0),  # Poor ESG
    ]
    
    violations = policy_engine.validate_portfolio(problematic_portfolio)
    
    print(f"Portfolio summary:")
    for inv in problematic_portfolio:
        print(f"  {inv.symbol:12} | {inv.country:2} | {inv.allocation:5.1f}% | ESG: {inv.esg_score}")
    
    print(f"\n✗ Found {len(violations)} policy violations:")
    for violation in violations:
        severity_icon = "🚨" if violation.severity == "critical" else "⚠️" if violation.severity == "major" else "ℹ️"
        print(f"  {severity_icon} {violation.severity.upper():8}: {violation.description}")
        if violation.current_value and violation.limit_value:
            print(f"     Current: {violation.current_value:.1f}, Limit: {violation.limit_value:.1f}")
    
    # Example 3: Security Screening
    print("\n" + "="*40)
    print("Example 3: Individual Security Screening")
    print("="*40)
    
    test_securities = [
        ('AAPL', 'technology', 8.5),
        ('EVIL_CORP', 'tobacco_manufacturing', 2.0),
        ('CLEAN_ENERGY', 'renewable_energy', 9.0),
        ('MID_ESG', 'consumer_goods', 5.5),
    ]
    
    for symbol, sector, esg_score in test_securities:
        is_allowed, reason = policy_engine.is_security_allowed(symbol, sector, esg_score)
        status = "✓ ALLOWED" if is_allowed else "✗ REJECTED"
        print(f"  {symbol:12} | {sector:20} | ESG: {esg_score} | {status}")
        if not is_allowed:
            print(f"    Reason: {reason}")
    
    print("\n" + "="*50)
    print("Demo completed successfully!")
    print("See USER_GUIDE.md for detailed usage instructions.")


if __name__ == "__main__":
    main()