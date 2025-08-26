# Financial Advisor

A data-driven financial decision-making framework using dbt to calculate momentum and volatility features for investment analysis.

## Overview

This project provides SQL-based models to calculate key financial indicators:
- **Momentum**: 12-month price change analysis to identify trending stocks
- **Volatility**: Risk assessment using standard deviation of daily returns

## Project Structure

```
├── README_FOR_BEGINNERS.md           # Beginner-friendly guide
├── USER_GUIDE.md                     # Detailed technical documentation  
├── INVESTMENT_EXAMPLES.md            # Practical usage examples
└── advanced/dbt_project/             # dbt models and configuration
    ├── models/features/
    │   ├── momentum.sql              # Momentum calculation model
    │   ├── volatility.sql            # Volatility calculation model
    │   └── schema.yml                # Model documentation and tests
    └── dbt_project.yml               # dbt configuration
```

## Quick Start

1. **For Beginners**: Start with [README_FOR_BEGINNERS.md](README_FOR_BEGINNERS.md)
2. **For Technical Users**: See [USER_GUIDE.md](USER_GUIDE.md)  
3. **For Implementation**: Check [INVESTMENT_EXAMPLES.md](INVESTMENT_EXAMPLES.md)
4. **For Development**: Navigate to [advanced/dbt_project/](advanced/dbt_project/)

## Features

- **Momentum Analysis**: Calculate 12-month price momentum with categorical strength levels
- **Volatility Assessment**: Measure price stability using rolling standard deviation
- **Risk-Return Framework**: Combine momentum and volatility for investment decisions
- **dbt Integration**: Production-ready SQL models with documentation and tests

## Use Cases

- Portfolio construction and optimization
- Risk assessment and management  
- Investment screening and selection
- Quantitative trading strategies
- Financial research and analysis

## Getting Started

Ensure you have:
- A database with stock price data (`symbol`, `date`, `close_price`)
- dbt installed with appropriate database adapter
- Database connection configured in dbt profiles

Then run:
```bash
cd advanced/dbt_project/
dbt run
```

## Documentation

- **Beginners**: [README_FOR_BEGINNERS.md](README_FOR_BEGINNERS.md) - Concepts and examples
- **Technical**: [USER_GUIDE.md](USER_GUIDE.md) - Implementation details
- **Practical**: [INVESTMENT_EXAMPLES.md](INVESTMENT_EXAMPLES.md) - Real-world usage
- **dbt Project**: [advanced/dbt_project/README.md](advanced/dbt_project/README.md) - Setup guide