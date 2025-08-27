#!/usr/bin/env python3
"""
Generate scenario analysis for portfolio stress testing.

This script creates various market scenarios and evaluates portfolio
performance under different stress conditions.
"""

import numpy as np
import pandas as pd
import json
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import datetime, timedelta


def generate_market_scenarios() -> Dict[str, Dict[str, float]]:
    """Generate predefined market stress scenarios"""
    
    scenarios = {
        "base_case": {
            "name": "Base Case",
            "description": "Normal market conditions",
            "equity_shock": 0.0,
            "bond_shock": 0.0,
            "credit_spread_shock": 0.0,
            "vix_shock": 0.0,
            "currency_shock": 0.0,
            "commodity_shock": 0.0,
            "probability": 0.60
        },
        "mild_recession": {
            "name": "Mild Recession",
            "description": "Economic slowdown with moderate market decline",
            "equity_shock": -0.15,
            "bond_shock": 0.05,
            "credit_spread_shock": 0.02,
            "vix_shock": 0.40,
            "currency_shock": -0.05,
            "commodity_shock": -0.10,
            "probability": 0.20
        },
        "severe_recession": {
            "name": "Severe Recession",
            "description": "Major economic downturn similar to 2008",
            "equity_shock": -0.40,
            "bond_shock": 0.15,
            "credit_spread_shock": 0.05,
            "vix_shock": 1.00,
            "currency_shock": -0.10,
            "commodity_shock": -0.25,
            "probability": 0.05
        },
        "covid_style_shock": {
            "name": "Pandemic-Style Shock",
            "description": "Sudden market disruption like COVID-19",
            "equity_shock": -0.35,
            "bond_shock": -0.05,
            "credit_spread_shock": 0.04,
            "vix_shock": 1.50,
            "currency_shock": 0.05,
            "commodity_shock": -0.30,
            "probability": 0.03
        },
        "inflation_shock": {
            "name": "Inflation Shock",
            "description": "Persistent high inflation scenario",
            "equity_shock": -0.10,
            "bond_shock": -0.20,
            "credit_spread_shock": 0.01,
            "vix_shock": 0.30,
            "currency_shock": -0.08,
            "commodity_shock": 0.30,
            "probability": 0.07
        },
        "geopolitical_crisis": {
            "name": "Geopolitical Crisis",
            "description": "Major geopolitical tensions affecting markets",
            "equity_shock": -0.20,
            "bond_shock": 0.10,
            "credit_spread_shock": 0.03,
            "vix_shock": 0.80,
            "currency_shock": 0.15,
            "commodity_shock": 0.25,
            "probability": 0.05
        }
    }
    
    return scenarios


def apply_scenario_to_portfolio(portfolio_weights: Dict[str, float],
                               asset_characteristics: Dict[str, Dict[str, float]],
                               scenario: Dict[str, float]) -> Dict[str, float]:
    """
    Apply scenario shocks to portfolio based on asset characteristics
    
    Args:
        portfolio_weights: Current portfolio allocation
        asset_characteristics: Asset-specific risk characteristics
        scenario: Scenario shock parameters
        
    Returns:
        Portfolio returns under the scenario
    """
    scenario_returns = {}
    
    for asset, weight in portfolio_weights.items():
        if asset in asset_characteristics:
            char = asset_characteristics[asset]
            
            # Calculate scenario return based on asset characteristics
            scenario_return = (
                char.get('equity_beta', 0.0) * scenario['equity_shock'] +
                char.get('duration', 0.0) * scenario['bond_shock'] +
                char.get('credit_beta', 0.0) * scenario['credit_spread_shock'] +
                char.get('volatility_beta', 0.0) * scenario['vix_shock'] +
                char.get('currency_exposure', 0.0) * scenario['currency_shock'] +
                char.get('commodity_beta', 0.0) * scenario['commodity_shock']
            )
            
            scenario_returns[asset] = scenario_return
        else:
            # Default to equity-like behavior
            scenario_returns[asset] = scenario['equity_shock']
    
    return scenario_returns


def create_sample_portfolio_and_characteristics():
    """Create sample portfolio and asset characteristics for testing"""
    
    # Sample portfolio
    portfolio = {
        'US_EQUITIES': 0.40,
        'INTL_EQUITIES': 0.20,
        'US_BONDS': 0.25,
        'CREDIT': 0.10,
        'COMMODITIES': 0.05
    }
    
    # Asset characteristics for scenario analysis
    characteristics = {
        'US_EQUITIES': {
            'equity_beta': 1.0,
            'duration': 0.0,
            'credit_beta': 0.0,
            'volatility_beta': 0.8,
            'currency_exposure': 0.0,
            'commodity_beta': 0.1
        },
        'INTL_EQUITIES': {
            'equity_beta': 0.9,
            'duration': 0.0,
            'credit_beta': 0.0,
            'volatility_beta': 0.9,
            'currency_exposure': 0.6,
            'commodity_beta': 0.2
        },
        'US_BONDS': {
            'equity_beta': -0.2,
            'duration': 6.0,
            'credit_beta': 0.0,
            'volatility_beta': -0.3,
            'currency_exposure': 0.0,
            'commodity_beta': -0.1
        },
        'CREDIT': {
            'equity_beta': 0.3,
            'duration': 4.0,
            'credit_beta': 1.0,
            'volatility_beta': 0.4,
            'currency_exposure': 0.1,
            'commodity_beta': 0.0
        },
        'COMMODITIES': {
            'equity_beta': 0.2,
            'duration': 0.0,
            'credit_beta': 0.0,
            'volatility_beta': 0.5,
            'currency_exposure': 0.3,
            'commodity_beta': 1.0
        }
    }
    
    return portfolio, characteristics


def run_scenario_analysis(portfolio_weights: Dict[str, float],
                         asset_characteristics: Dict[str, Dict[str, float]]) -> pd.DataFrame:
    """Run comprehensive scenario analysis"""
    
    scenarios = generate_market_scenarios()
    results = []
    
    for scenario_id, scenario in scenarios.items():
        # Apply scenario to portfolio
        asset_returns = apply_scenario_to_portfolio(
            portfolio_weights, asset_characteristics, scenario
        )
        
        # Calculate portfolio return
        portfolio_return = sum(
            portfolio_weights[asset] * asset_returns[asset]
            for asset in portfolio_weights.keys()
            if asset in asset_returns
        )
        
        # Calculate contribution by asset
        contributions = {
            asset: portfolio_weights[asset] * asset_returns.get(asset, 0)
            for asset in portfolio_weights.keys()
        }
        
        result = {
            'scenario_id': scenario_id,
            'scenario_name': scenario['name'],
            'description': scenario['description'],
            'probability': scenario['probability'],
            'portfolio_return': portfolio_return,
            'portfolio_return_pct': portfolio_return * 100,
            **{f'contrib_{asset}': contrib for asset, contrib in contributions.items()},
            **{f'return_{asset}': asset_returns.get(asset, 0) for asset in portfolio_weights.keys()}
        }
        
        results.append(result)
    
    return pd.DataFrame(results)


def calculate_risk_metrics(scenario_results: pd.DataFrame) -> Dict[str, float]:
    """Calculate portfolio risk metrics from scenario analysis"""
    
    # Expected return (probability-weighted)
    expected_return = (scenario_results['portfolio_return'] * 
                      scenario_results['probability']).sum()
    
    # Volatility (probability-weighted)
    variance = ((scenario_results['portfolio_return'] - expected_return)**2 * 
                scenario_results['probability']).sum()
    volatility = np.sqrt(variance)
    
    # Value at Risk (95% confidence)
    sorted_returns = scenario_results['portfolio_return'].sort_values()
    cumulative_prob = scenario_results.set_index(sorted_returns.index)['probability'].cumsum()
    var_95_idx = cumulative_prob[cumulative_prob >= 0.05].index[0]
    var_95 = sorted_returns.loc[var_95_idx]
    
    # Conditional Value at Risk (Expected Shortfall)
    cvar_scenarios = scenario_results[scenario_results['portfolio_return'] <= var_95]
    if len(cvar_scenarios) > 0:
        cvar_95 = (cvar_scenarios['portfolio_return'] * 
                   cvar_scenarios['probability']).sum() / cvar_scenarios['probability'].sum()
    else:
        cvar_95 = var_95
    
    # Maximum drawdown
    max_drawdown = scenario_results['portfolio_return'].min()
    
    # Upside/Downside metrics
    upside_scenarios = scenario_results[scenario_results['portfolio_return'] > 0]
    downside_scenarios = scenario_results[scenario_results['portfolio_return'] < 0]
    
    upside_probability = upside_scenarios['probability'].sum()
    downside_probability = downside_scenarios['probability'].sum()
    
    if len(upside_scenarios) > 0:
        upside_return = (upside_scenarios['portfolio_return'] * 
                        upside_scenarios['probability']).sum() / upside_probability
    else:
        upside_return = 0
    
    if len(downside_scenarios) > 0:
        downside_return = (downside_scenarios['portfolio_return'] * 
                          downside_scenarios['probability']).sum() / downside_probability
    else:
        downside_return = 0
    
    return {
        'expected_return': expected_return,
        'volatility': volatility,
        'var_95': var_95,
        'cvar_95': cvar_95,
        'max_drawdown': max_drawdown,
        'upside_probability': upside_probability,
        'downside_probability': downside_probability,
        'upside_return': upside_return,
        'downside_return': downside_return,
        'gain_loss_ratio': abs(upside_return / downside_return) if downside_return < 0 else float('inf')
    }


def generate_monte_carlo_scenarios(n_scenarios: int = 10000, 
                                  correlation_matrix: np.ndarray = None) -> pd.DataFrame:
    """Generate Monte Carlo scenarios for stress testing"""
    
    if correlation_matrix is None:
        # Default correlation structure
        n_factors = 6  # equity, bond, credit, vix, currency, commodity
        correlation_matrix = np.eye(n_factors)
        correlation_matrix[0, 1] = -0.3  # equity-bond negative correlation
        correlation_matrix[1, 0] = -0.3
        correlation_matrix[0, 3] = -0.6  # equity-vix negative correlation
        correlation_matrix[3, 0] = -0.6
        correlation_matrix = correlation_matrix + np.random.normal(0, 0.1, (n_factors, n_factors))
        correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
        np.fill_diagonal(correlation_matrix, 1.0)
    
    # Generate correlated shocks
    shocks = np.random.multivariate_normal(
        mean=np.zeros(6),
        cov=correlation_matrix,
        size=n_scenarios
    )
    
    # Scale shocks to realistic ranges
    shock_scales = np.array([0.25, 0.15, 0.03, 0.8, 0.1, 0.2])  # equity, bond, credit, vix, currency, commodity
    scaled_shocks = shocks * shock_scales
    
    scenarios_df = pd.DataFrame(scaled_shocks, columns=[
        'equity_shock', 'bond_shock', 'credit_spread_shock', 
        'vix_shock', 'currency_shock', 'commodity_shock'
    ])
    
    scenarios_df['scenario_id'] = range(n_scenarios)
    scenarios_df['probability'] = 1.0 / n_scenarios
    
    return scenarios_df


def main():
    """Main scenario generation and analysis"""
    
    output_dir = Path('docs/images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🎯 Starting portfolio scenario analysis...")
    
    # Create sample portfolio
    portfolio, characteristics = create_sample_portfolio_and_characteristics()
    
    print("📊 Sample Portfolio:")
    for asset, weight in portfolio.items():
        print(f"  {asset}: {weight:.1%}")
    
    # Run predefined scenario analysis
    print("\n🌪️  Running predefined scenario analysis...")
    scenario_results = run_scenario_analysis(portfolio, characteristics)
    
    # Calculate risk metrics
    risk_metrics = calculate_risk_metrics(scenario_results)
    
    # Print results
    print("\n" + "="*60)
    print("SCENARIO ANALYSIS RESULTS")
    print("="*60)
    
    print("\nScenario Outcomes:")
    for _, row in scenario_results.iterrows():
        print(f"  {row['scenario_name']:20} {row['portfolio_return_pct']:6.2f}% "
              f"(prob: {row['probability']:.1%})")
    
    print(f"\nRisk Metrics:")
    print(f"  Expected Return:     {risk_metrics['expected_return']:.4f} ({risk_metrics['expected_return']*100:.2f}%)")
    print(f"  Volatility:          {risk_metrics['volatility']:.4f}")
    print(f"  VaR (95%):          {risk_metrics['var_95']:.4f} ({risk_metrics['var_95']*100:.2f}%)")
    print(f"  CVaR (95%):         {risk_metrics['cvar_95']:.4f} ({risk_metrics['cvar_95']*100:.2f}%)")
    print(f"  Max Drawdown:        {risk_metrics['max_drawdown']:.4f} ({risk_metrics['max_drawdown']*100:.2f}%)")
    print(f"  Downside Prob:       {risk_metrics['downside_probability']:.1%}")
    print(f"  Gain/Loss Ratio:     {risk_metrics['gain_loss_ratio']:.2f}")
    
    # Generate Monte Carlo scenarios
    print("\n🎲 Generating Monte Carlo scenarios...")
    mc_scenarios = generate_monte_carlo_scenarios(n_scenarios=5000)
    
    # Analyze Monte Carlo results
    mc_results = []
    for _, scenario in mc_scenarios.iterrows():
        asset_returns = apply_scenario_to_portfolio(portfolio, characteristics, scenario.to_dict())
        portfolio_return = sum(
            portfolio[asset] * asset_returns[asset]
            for asset in portfolio.keys()
            if asset in asset_returns
        )
        mc_results.append(portfolio_return)
    
    mc_results = np.array(mc_results)
    
    print(f"\nMonte Carlo Results (5000 scenarios):")
    print(f"  Mean Return:         {np.mean(mc_results):.4f} ({np.mean(mc_results)*100:.2f}%)")
    print(f"  Volatility:          {np.std(mc_results):.4f}")
    print(f"  VaR (95%):          {np.percentile(mc_results, 5):.4f} ({np.percentile(mc_results, 5)*100:.2f}%)")
    print(f"  CVaR (95%):         {np.mean(mc_results[mc_results <= np.percentile(mc_results, 5)]):.4f}")
    print(f"  Worst Case:          {np.min(mc_results):.4f} ({np.min(mc_results)*100:.2f}%)")
    print(f"  Best Case:           {np.max(mc_results):.4f} ({np.max(mc_results)*100:.2f}%)")
    
    # Save results
    scenario_results.to_csv(output_dir / 'scenario_analysis.csv', index=False)
    print(f"\n💾 Scenario results saved to {output_dir / 'scenario_analysis.csv'}")
    
    # Save Monte Carlo results
    mc_df = pd.DataFrame({
        'scenario_id': range(len(mc_results)),
        'portfolio_return': mc_results
    })
    mc_df.to_csv(output_dir / 'monte_carlo_scenarios.csv', index=False)
    print(f"📊 Monte Carlo results saved to {output_dir / 'monte_carlo_scenarios.csv'}")
    
    # Save risk metrics
    with open(output_dir / 'risk_metrics.json', 'w') as f:
        json.dump(risk_metrics, f, indent=2)
    print(f"📈 Risk metrics saved to {output_dir / 'risk_metrics.json'}")
    
    print("\n✅ Scenario analysis completed!")
    print("\nKey Insights:")
    print("• Portfolio shows resilience in base case scenarios")
    print("• Major downside risk in severe recession and pandemic scenarios")
    print("• Diversification provides some protection but limited in extreme events")
    print("• Consider hedging strategies for tail risk management")


if __name__ == "__main__":
    main()