# Financial Advisor - User Guide

## Table of Contents
1. [Installation and Setup](#installation-and-setup)
2. [dbt Models](#dbt-models)
3. [Feast Feature Store](#feast-feature-store)
4. [Feature Usage Examples](#feature-usage-examples)
5. [Testing](#testing)
6. [Advanced Configuration](#advanced-configuration)

## Installation and Setup

### System Requirements
- Python 3.8 or higher
- 4GB RAM minimum
- 1GB disk space

### Installation Steps

1. **Install dependencies**:
   ```bash
   pip install dbt-core dbt-duckdb feast pandas pytest
   ```

2. **Clone and navigate to project**:
   ```bash
   git clone <repository-url>
   cd financial-advisor
   ```

3. **Set up dbt**:
   ```bash
   cd advanced/dbt_project
   dbt deps
   dbt run --profiles-dir .
   ```

4. **Set up Feast**:
   ```bash
   cd ../feast_repo
   feast apply
   ```

## dbt Models

### ESG Indicators Model (`esg_indicators.sql`)

**Purpose**: Analyzes Environmental, Social, and Governance factors for companies.

**Key Features**:
- Environmental scores and carbon intensity
- Social metrics including employee satisfaction
- Governance indicators like board diversity
- Derived categorizations and flags

**Sample Query**:
```sql
SELECT 
    symbol,
    company_name,
    overall_esg_score,
    esg_category,
    is_green_leader
FROM {{ ref('esg_indicators') }}
WHERE esg_category = 'High ESG'
```

### Credit Indicators Model (`credit_indicators.sql`)

**Purpose**: Evaluates credit risk and financial health of companies.

**Key Features**:
- Credit ratings and spreads
- Debt ratios and coverage metrics
- Default probability assessments
- Liquidity and leverage analysis

**Sample Query**:
```sql
SELECT 
    symbol,
    credit_rating,
    credit_score,
    default_risk_category,
    leverage_category
FROM {{ ref('credit_indicators') }}
WHERE credit_quality_category = 'Investment Grade High'
```

### Macro Indicators Model (`macro_indicators.sql`)

**Purpose**: Tracks macroeconomic indicators by country.

**Key Features**:
- Interest rates and yield curves
- Economic growth and employment data
- Market and commodity prices
- Economic phase classifications

**Sample Query**:
```sql
SELECT 
    country,
    economic_growth_phase,
    yield_curve_shape,
    real_interest_rate,
    consumer_sentiment
FROM {{ ref('macro_indicators') }}
WHERE country = 'US'
```

## Feast Feature Store

### Feature Views

#### ESG Features
```python
from feast import FeatureStore

fs = FeatureStore(repo_path="advanced/feast_repo")

# Get ESG features for Apple
features = fs.get_online_features(
    features=[
        "esg_indicators:environmental_score",
        "esg_indicators:social_score", 
        "esg_indicators:governance_score",
        "esg_indicators:overall_esg_score"
    ],
    entity_rows=[{"company": "AAPL"}]
).to_dict()
```

#### Credit Features
```python
# Get credit features for Tesla
credit_features = fs.get_online_features(
    features=[
        "credit_indicators:credit_rating",
        "credit_indicators:credit_score",
        "credit_indicators:probability_of_default",
        "credit_indicators:leverage_category"
    ],
    entity_rows=[{"company": "TSLA"}]
).to_dict()
```

#### Macro Features
```python
# Get macro features for US
macro_features = fs.get_online_features(
    features=[
        "macro_indicators:federal_funds_rate",
        "macro_indicators:inflation_rate_yoy",
        "macro_indicators:economic_growth_phase",
        "macro_indicators:yield_curve_shape"
    ],
    entity_rows=[{"country": "US"}]
).to_dict()
```

## Feature Usage Examples

### Investment Screening

```python
# Example: Find companies with high ESG scores and low credit risk
def screen_sustainable_investments():
    companies = ["AAPL", "TSLA", "MSFT"]
    
    for company in companies:
        esg_features = fs.get_online_features(
            features=[
                "esg_indicators:overall_esg_score",
                "esg_indicators:esg_category"
            ],
            entity_rows=[{"company": company}]
        ).to_dict()
        
        credit_features = fs.get_online_features(
            features=[
                "credit_indicators:credit_score",
                "credit_indicators:default_risk_category"
            ],
            entity_rows=[{"company": company}]
        ).to_dict()
        
        # Your analysis logic here
        print(f"{company}: ESG={esg_features['overall_esg_score'][0]}, "
              f"Credit={credit_features['credit_score'][0]}")
```

### Market Timing Analysis

```python
# Example: Assess market conditions using macro indicators
def assess_market_conditions():
    macro_data = fs.get_online_features(
        features=[
            "macro_indicators:yield_curve_shape",
            "macro_indicators:economic_growth_phase",
            "macro_indicators:consumer_sentiment"
        ],
        entity_rows=[{"country": "US"}]
    ).to_dict()
    
    yield_curve = macro_data['yield_curve_shape'][0]
    growth_phase = macro_data['economic_growth_phase'][0] 
    sentiment = macro_data['consumer_sentiment'][0]
    
    # Investment decision logic
    if yield_curve == 'Inverted' and growth_phase == 'Recession':
        return "Defensive positioning recommended"
    elif sentiment == 'Very Optimistic' and growth_phase == 'Strong Growth':
        return "Growth positioning recommended"
    else:
        return "Balanced positioning recommended"
```

## Testing

### Running dbt Tests

```bash
cd advanced/dbt_project
dbt test --profiles-dir .
```

### Running Python Tests

```bash
pytest tests/ -v
```

### Test Coverage

Our tests cover:
- **Data Quality**: Null checks, range validations
- **Feature Completeness**: All expected fields present
- **Configuration Validation**: Feast feature views properly configured
- **Entity Relationships**: Correct entity mappings

## Advanced Configuration

### Custom dbt Profiles

Edit `advanced/dbt_project/profiles.yml` to configure different databases:

```yaml
financial_advisor:
  target: prod
  outputs:
    prod:
      type: postgres
      host: your-postgres-host
      user: your-username
      password: your-password
      dbname: financial_advisor
      schema: features
      threads: 8
```

### Feast Configuration

Modify `advanced/feast_repo/feature_store.yaml` for production:

```yaml
project: financial_advisor
registry: s3://your-bucket/registry.db
provider: aws
online_store:
    type: redis
    connection_string: redis://your-redis-host:6379
offline_store:
    type: bigquery
    project_id: your-gcp-project
```

### Adding New Features

1. **Add dbt model**:
   - Create new SQL file in `models/features/`
   - Add to `schema.yml` with tests
   - Run `dbt run` and `dbt test`

2. **Add Feast feature view**:
   - Define new feature view in `feature_views.py`
   - Update entities if needed
   - Run `feast apply`

3. **Add tests**:
   - Update test files with new feature validation
   - Run `pytest tests/`

## Troubleshooting

### Common Issues

**dbt connection errors**: Check profiles.yml configuration
**Feast apply fails**: Ensure feature store directory exists
**Test failures**: Validate data ranges and null constraints

### Performance Optimization

- Use appropriate materialization strategies in dbt
- Configure Feast TTL based on data freshness requirements
- Monitor feature serving latency in production