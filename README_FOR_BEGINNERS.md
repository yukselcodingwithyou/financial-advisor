# Financial Decision Engine - Comprehensive Guide

## 🎯 Overview

The Financial Decision Engine is a comprehensive portfolio optimization and risk management system built for institutional and sophisticated retail investors. It combines modern portfolio theory, advanced risk models, machine learning features, and real-time data processing to provide intelligent investment decision support.

### Key Capabilities

- **Portfolio Optimization:** Mean-variance, CVaR, and multi-objective optimization
- **Risk Management:** Concentration limits, factor exposure controls, scenario analysis
- **Feature Engineering:** 12+ factor models including momentum, value, sentiment, and macro
- **RAG System:** Document-based financial advisory with vector search
- **Real-time Serving:** Low-latency API for production trading systems
- **MLOps Integration:** Experiment tracking, model versioning, and performance monitoring

## 🏗️ System Architecture

![Architecture Diagram](docs/images/architecture.png)

The system follows a modern data architecture pattern:

### Data Layer
- **Bronze:** Raw market data from APIs and feeds
- **Silver:** Processed features via dbt transformations  
- **Gold:** Aggregated signals ready for optimization

### Processing Layer
- **dbt Models:** Feature engineering with SQL
- **Feast:** Real-time feature serving
- **PostgreSQL + pgvector:** Document storage and vector search

### Application Layer
- **FastAPI:** RESTful optimization service
- **Streamlit:** Interactive demo and analysis interface
- **MLflow:** Experiment tracking and model registry

### Infrastructure Layer
- **Docker:** Containerized deployment
- **GitHub Actions:** CI/CD pipeline
- **Redis:** Caching and session storage

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yukselcodingwithyou/financial-advisor.git
cd financial-advisor

# Start all services
make docker-up

# Access interfaces
open http://localhost:8501  # Streamlit demo
open http://localhost:8000  # FastAPI docs
open http://localhost:5000  # MLflow UI
```

### Option 2: Local Development

```bash
# Setup Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt

# Configure environment
cp .env.example .env

# Start API server
make run

# In another terminal, start Streamlit
make streamlit
```

## 📊 Core Features

### Portfolio Optimization

The engine supports multiple optimization objectives:

**Mean-Variance Optimization:**
```python
POST /optimize
{
  "assets": ["AAPL", "GOOGL", "MSFT"],
  "expected_returns": {"AAPL": 0.12, "GOOGL": 0.10, "MSFT": 0.08},
  "covariance_matrix": [[0.04, 0.01, 0.01], ...],
  "risk_aversion": 3.0
}
```

**Concentration Repair:**
```python
POST /repair-concentration
{
  "current_weights": {"AAPL": 0.50, "GOOGL": 0.50},
  "max_concentration": 0.05,
  "sector_caps": {"Technology": 0.30}
}
```

### Risk Management

- **HHI Analysis:** Herfindahl-Hirschman Index for concentration measurement
- **Factor Exposure:** Market beta, size, value, momentum, quality factors
- **Scenario Testing:** Stress testing across recession, inflation, geopolitical scenarios
- **VaR/CVaR:** Value at Risk and Conditional Value at Risk calculations

### Feature Engineering

**dbt Models Available:**
- `momentum.sql` - Price momentum across multiple horizons
- `value.sql` - Valuation metrics with sector adjustments
- `sentiment.sql` - News, analyst, and social media sentiment
- `liquidity.sql` - Trading volume and bid-ask spread analysis
- `esg.sql` - Environmental, Social, Governance scores
- `options.sql` - Implied volatility and options flow
- `macro.sql` - Interest rates, credit spreads, regime detection

### RAG Financial Assistant

Retrieval-Augmented Generation for financial advice:

```python
from src.rag.rag_minimal import SimpleRAG

rag = SimpleRAG()
rag.add_financial_documents()

result = rag.query("How should I manage portfolio concentration risk?")
print(result['response'])
```

## 🔧 Technical Architecture

### Optimization Engine

**Mathematical Foundation:**
- Quadratic Programming (CVXPY) for mean-variance optimization
- Linear Programming for concentration repair
- Robust optimization for parameter uncertainty
- Multi-objective optimization for ESG integration

**Risk Models:**
- Barra-style factor models
- GARCH volatility forecasting
- Copula-based tail dependence
- Regime-switching models

### Data Pipeline

**Feature Engineering Flow:**
```
Raw Data → dbt Transformations → Feast Feature Store → API Serving
```

**Supported Data Sources:**
- Market data APIs (price, volume, corporate actions)
- Fundamental data (earnings, balance sheet, ratios)
- Alternative data (news sentiment, satellite data, web scraping)
- Macroeconomic indicators (rates, spreads, surveys)

### MLOps Integration

**Experiment Tracking:**
- Model parameters and hyperparameters
- Portfolio performance metrics
- Backtest results and attribution
- A/B testing for strategy variants

**Model Registry:**
- Versioned risk models
- Feature transformation pipelines
- Optimization configurations
- Performance benchmarks

## 📈 Financial Methodology

### Modern Portfolio Theory Extensions

**Mean-Variance Optimization:**
- Markowitz efficient frontier
- Black-Litterman expected returns
- Shrinkage covariance estimation
- Transaction cost optimization

**Risk-Based Approaches:**
- Minimum variance portfolios
- Risk parity allocation
- Maximum diversification
- Hierarchical risk parity

**Factor Investing:**
- Fama-French multi-factor models
- Factor timing strategies
- Smart beta construction
- ESG integration methods

### Risk Management Framework

**Concentration Limits:**
- Single asset position limits
- Sector and geographic caps
- Factor exposure constraints
- Liquidity requirements

**Stress Testing:**
- Historical scenario replay
- Monte Carlo simulation
- Tail risk measurement
- Regime change analysis

## 📚 Glossary

**Alpha:** Risk-adjusted excess return relative to benchmark
**Beta:** Sensitivity to market movements
**CVaR:** Conditional Value at Risk, expected loss beyond VaR threshold
**HHI:** Herfindahl-Hirschman Index, concentration measurement
**Sharpe Ratio:** Risk-adjusted return metric (excess return / volatility)
**Tracking Error:** Standard deviation of active returns vs benchmark
**VaR:** Value at Risk, maximum expected loss at confidence level

**Factor Definitions:**
- **Value:** Preference for undervalued securities (low P/E, P/B)
- **Momentum:** Tendency for trending securities to continue
- **Quality:** Focus on profitable, stable companies
- **Size:** Small-cap premium over large-cap stocks
- **Low Volatility:** Lower-risk stocks often outperform risk-adjusted

## 🔍 Use Cases

### Institutional Asset Management
- **Portfolio Construction:** Multi-asset class optimization
- **Risk Budgeting:** Factor-based risk allocation
- **Performance Attribution:** Return decomposition and analysis
- **Compliance Monitoring:** Regulatory constraint enforcement

### Wealth Management
- **Goal-Based Investing:** Liability-driven optimization
- **ESG Integration:** Sustainable investing strategies
- **Tax Optimization:** After-tax return maximization
- **Rebalancing:** Systematic portfolio maintenance

### Research and Development
- **Strategy Backtesting:** Historical performance analysis
- **Factor Research:** New signal discovery and validation
- **Model Development:** Risk model enhancement
- **Market Microstructure:** Execution cost analysis

## 📊 Sample Workflows

### Daily Portfolio Management

```bash
# 1. Update market data
make dbt-run

# 2. Generate optimization recommendations
python -c "
import requests
response = requests.post('http://localhost:8000/optimize', json=portfolio_request)
print(response.json())
"

# 3. Analyze risk metrics
python -c "
from advanced.api_fastapi.main import calculate_risk_metrics
metrics = calculate_risk_metrics(current_portfolio)
print(f'Portfolio HHI: {metrics[\"concentration_hhi\"]:.4f}')
"

# 4. Generate client report
make report
```

### Research & Backtesting

```bash
# 1. Run factor analysis
python scripts/bench_compare_mv_cvar.py

# 2. Stress test scenarios
python scripts/bench_generate_scenarios.py

# 3. Generate performance attribution
python scripts/render_report.py

# 4. Update documentation
make generate-diagrams
```

## 🛠️ Development Guide

### Adding New Features

**New Optimization Method:**
1. Add function to `advanced/api_fastapi/main.py`
2. Create unit tests in `tests/`
3. Update API documentation
4. Add to Streamlit interface

**New dbt Model:**
1. Create SQL file in `advanced/dbt_project/models/features/`
2. Add to Feast feature views
3. Update documentation
4. Test data quality

**New Risk Metric:**
1. Implement calculation function
2. Add to risk analysis endpoint
3. Include in reporting templates
4. Create visualization

### Testing Strategy

**Unit Tests:** Core optimization and risk functions
**Integration Tests:** API endpoints and data pipeline
**Performance Tests:** Optimization speed and memory usage
**Security Tests:** Input validation and access control

### Code Quality

**Linting:** Ruff for Python code formatting
**Type Checking:** MyPy for static type analysis
**Security:** Bandit for vulnerability scanning
**Dependencies:** Safety for known security issues

## 🎯 Roadmap

### Short Term (3 months)
- [ ] Real-time market data integration
- [ ] Advanced factor models (Fama-French 5-factor)
- [ ] Transaction cost optimization
- [ ] Mobile-responsive Streamlit interface

### Medium Term (6 months)
- [ ] Multi-asset class support (bonds, commodities, FX)
- [ ] Alternative risk measures (drawdown, semi-variance)
- [ ] ESG scoring and integration
- [ ] Automated rebalancing workflows

### Long Term (12 months)
- [ ] Machine learning alpha generation
- [ ] Real-time execution algorithms
- [ ] Regulatory reporting automation
- [ ] Client portal and customization

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. **Code Standards:** Follow PEP 8 and use type hints
2. **Testing:** Add tests for new functionality
3. **Documentation:** Update docs for public APIs
4. **Performance:** Profile code for optimization bottlenecks

## 📞 Support

- **Documentation:** Check USER_GUIDE.md for detailed instructions
- **API Reference:** http://localhost:8000/docs when running locally
- **Issues:** Create GitHub issues for bugs or feature requests
- **Discussions:** Use GitHub Discussions for questions

---

**Disclaimer:** This software is for educational and research purposes. Always consult qualified financial advisors for investment decisions. Past performance does not guarantee future results.