# Financial Decision Engine - User Guide

## Quick Start Guide

### Prerequisites

Before getting started with the Financial Decision Engine, ensure you have:

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL with pgvector extension (for production RAG features)
- Git for version control

### Installation

#### Option 1: Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yukselcodingwithyou/financial-advisor.git
   cd financial-advisor
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   make install-dev
   # or manually:
   pip install -r requirements.txt -r requirements-dev.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

#### Option 2: Docker Setup

1. **Clone and start services:**
   ```bash
   git clone https://github.com/yukselcodingwithyou/financial-advisor.git
   cd financial-advisor
   make docker-up
   ```

2. **Access services:**
   - FastAPI service: http://localhost:8000
   - Streamlit demo: http://localhost:8501
   - MLflow UI: http://localhost:5000
   - Jupyter notebooks: http://localhost:8888

### Basic Usage

#### 1. Portfolio Optimization

**Via Streamlit Interface:**
1. Navigate to http://localhost:8501
2. Go to "Portfolio Optimization" page
3. Configure portfolio parameters
4. Click "Optimize Portfolio"

**Via API:**
```python
import requests

# Optimize portfolio
response = requests.post("http://localhost:8000/optimize", json={
    "assets": ["AAPL", "GOOGL", "MSFT"],
    "expected_returns": {"AAPL": 0.12, "GOOGL": 0.10, "MSFT": 0.08},
    "covariance_matrix": [[0.04, 0.01, 0.01], [0.01, 0.03, 0.01], [0.01, 0.01, 0.02]],
    "risk_aversion": 3.0
})

portfolio = response.json()
print(f"Optimal weights: {portfolio['portfolio']}")
```

#### 2. Risk Analysis

**Concentration Repair:**
```python
# Repair concentration violations
response = requests.post("http://localhost:8000/repair-concentration", json={
    "current_weights": {"AAPL": 0.60, "GOOGL": 0.25, "MSFT": 0.15},
    "max_concentration": 0.10
})

repaired = response.json()
print(f"HHI improved from {repaired['metrics']['original_hhi']:.4f} to {repaired['metrics']['repaired_hhi']:.4f}")
```

#### 3. RAG Assistant

**Using the RAG system:**
```python
from src.rag.rag_minimal import SimpleRAG

# Initialize RAG
rag = SimpleRAG()
rag.add_financial_documents()

# Query
result = rag.query("How do I manage portfolio risk?")
print(result['response'])
```

### Advanced Features

#### Feature Engineering with dbt

1. **Setup dbt:**
   ```bash
   cd advanced/dbt_project
   dbt deps
   dbt run
   ```

2. **Generate features:**
   ```bash
   make dbt-run
   ```

#### MLflow Experiment Tracking

1. **Start MLflow server:**
   ```bash
   mlflow server --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlruns
   ```

2. **Track experiments:**
   ```python
   from advanced.utils.mlflow_logger import log_optimization_run
   
   log_optimization_run(
       metrics={"sharpe_ratio": 0.85, "volatility": 0.15},
       portfolio={"AAPL": 0.5, "GOOGL": 0.5},
       optimization_type="mean_variance"
   )
   ```

#### Feast Feature Store

1. **Apply feature definitions:**
   ```bash
   make feast-apply
   ```

2. **Serve features:**
   ```python
   from feast import FeatureStore
   
   store = FeatureStore(repo_path="advanced/feast_repo")
   features = store.get_online_features(
       features=["momentum_features:momentum_3m"],
       entity_rows=[{"symbol": "AAPL"}]
   )
   ```

### Configuration

#### Environment Variables

Key environment variables in `.env`:

```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/db
PGVECTOR_URL=postgresql://user:pass@localhost:5432/vector_db

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=financial_optimizer

# Feature Store
USE_FEAST=true
FEAST_REPO_PATH=./advanced/feast_repo

# API
API_HOST=0.0.0.0
API_PORT=8000
```

#### Policy Configuration

Edit `docs/policies.yaml` to customize:

- Concentration limits
- Factor tilt coefficients
- Risk constraints
- Sector caps

Example:
```yaml
risk_management:
  concentration_limits:
    max_single_asset: 0.05
    max_sector: 0.15
    
factor_tilts:
  momentum:
    coefficient: 0.10
    lookback_days: 252
```

### Common Workflows

#### 1. Daily Portfolio Rebalancing

```bash
# Update features
make dbt-run

# Run optimization
python -c "
from advanced.api_fastapi.main import mean_variance_optimize
# Add your rebalancing logic here
"

# Generate report
make report
```

#### 2. Research and Backtesting

```bash
# Start Jupyter
make docker-up
# Navigate to localhost:8888

# Run benchmarks
make benchmark

# Analyze scenarios
python scripts/bench_generate_scenarios.py
```

#### 3. Model Development

```bash
# Run tests
make test

# Generate diagrams
make generate-diagrams

# Update documentation
python scripts/render_report.py
```

### API Reference

#### Core Endpoints

- `POST /optimize` - Portfolio optimization
- `POST /repair-concentration` - Fix concentration violations
- `POST /risk-metrics` - Calculate risk metrics
- `GET /policies` - Get current policies
- `GET /health` - Health check

#### Request/Response Examples

**Portfolio Optimization:**
```json
{
  "assets": ["AAPL", "GOOGL"],
  "expected_returns": {"AAPL": 0.12, "GOOGL": 0.10},
  "covariance_matrix": [[0.04, 0.01], [0.01, 0.03]],
  "risk_aversion": 3.0
}
```

Response:
```json
{
  "portfolio": {"AAPL": 0.6, "GOOGL": 0.4},
  "metrics": {
    "expected_return": 0.112,
    "volatility": 0.145,
    "sharpe_ratio": 0.772
  }
}
```

### Troubleshooting

#### Common Issues

1. **Docker containers not starting:**
   ```bash
   # Check logs
   docker-compose logs
   
   # Restart services
   make docker-down
   make docker-up
   ```

2. **Database connection errors:**
   - Verify PostgreSQL is running
   - Check DATABASE_URL in .env
   - Ensure pgvector extension is installed

3. **Import errors:**
   ```bash
   # Reinstall dependencies
   pip install -r requirements.txt --force-reinstall
   
   # Check Python path
   export PYTHONPATH=$PWD:$PYTHONPATH
   ```

4. **Feature store issues:**
   ```bash
   # Reset Feast
   cd advanced/feast_repo
   feast teardown
   feast apply
   ```

5. **Optimization convergence:**
   - Check input data quality
   - Verify covariance matrix is positive definite
   - Adjust solver tolerances
   - Review constraint feasibility

#### Performance Optimization

1. **Slow API responses:**
   - Enable Redis caching
   - Optimize database queries
   - Use connection pooling

2. **Memory issues:**
   - Reduce portfolio size
   - Limit historical data periods
   - Use data sampling for testing

3. **Slow dbt runs:**
   - Optimize SQL queries
   - Use incremental models
   - Partition large tables

### Getting Help

- **Documentation:** Check `README_FOR_BEGINNERS.md`
- **API Docs:** http://localhost:8000/docs (when running)
- **Logs:** Check `docker-compose logs` or application logs
- **Issues:** Create GitHub issues for bugs or feature requests

### Next Steps

1. **Customize for your use case:**
   - Update asset universe
   - Modify risk constraints
   - Add custom factors

2. **Integrate data sources:**
   - Connect market data APIs
   - Setup data pipelines
   - Configure real-time feeds

3. **Deploy to production:**
   - Setup cloud infrastructure
   - Configure monitoring
   - Implement security measures

4. **Extend functionality:**
   - Add new optimization methods
   - Implement custom risk models
   - Build additional interfaces