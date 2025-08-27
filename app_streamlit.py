"""
Streamlit Demo Application for Financial Decision Engine

This app provides a user-friendly interface for testing portfolio optimization,
risk analysis, and RAG-based financial advice.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import requests
import json
from typing import Dict, List, Any
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Financial Decision Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.25rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"  # FastAPI server URL

# Helper functions
@st.cache_data
def generate_sample_data(num_assets: int = 10) -> Dict[str, Any]:
    """Generate sample portfolio data for demonstration"""
    np.random.seed(42)  # For reproducible results
    
    assets = [f"ASSET_{i:02d}" for i in range(1, num_assets + 1)]
    
    # Generate expected returns (annualized)
    expected_returns = np.random.normal(0.08, 0.05, num_assets)
    expected_returns = np.clip(expected_returns, -0.2, 0.3)
    
    # Generate correlation matrix
    correlation_matrix = np.random.uniform(0.1, 0.7, (num_assets, num_assets))
    np.fill_diagonal(correlation_matrix, 1.0)
    
    # Make symmetric
    correlation_matrix = (correlation_matrix + correlation_matrix.T) / 2
    np.fill_diagonal(correlation_matrix, 1.0)
    
    # Generate volatilities
    volatilities = np.random.uniform(0.15, 0.35, num_assets)
    
    # Create covariance matrix
    vol_matrix = np.outer(volatilities, volatilities)
    covariance_matrix = correlation_matrix * vol_matrix
    
    return {
        "assets": assets,
        "expected_returns": {asset: float(ret) for asset, ret in zip(assets, expected_returns)},
        "covariance_matrix": covariance_matrix.tolist(),
        "volatilities": {asset: float(vol) for asset, vol in zip(assets, volatilities)},
        "correlations": correlation_matrix
    }

def call_api_endpoint(endpoint: str, method: str = "GET", data: Dict = None) -> Dict:
    """Call FastAPI endpoint with error handling"""
    try:
        url = f"{API_BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error {response.status_code}: {response.text}")
            return {"error": f"API Error {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Cannot connect to API server. Using demo mode with sample data.")
        return {"error": "Connection error"}
    except Exception as e:
        st.error(f"Error calling API: {str(e)}")
        return {"error": str(e)}

def create_portfolio_chart(weights: Dict[str, float], title: str = "Portfolio Allocation") -> go.Figure:
    """Create a pie chart for portfolio weights"""
    assets = list(weights.keys())
    values = list(weights.values())
    
    fig = go.Figure(data=[go.Pie(
        labels=assets,
        values=values,
        hole=0.3,
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig.update_layout(
        title=title,
        showlegend=True,
        height=400
    )
    
    return fig

def create_efficient_frontier_chart(returns: List[float], risks: List[float], 
                                  optimal_point: tuple = None) -> go.Figure:
    """Create efficient frontier visualization"""
    fig = go.Figure()
    
    # Efficient frontier curve
    fig.add_trace(go.Scatter(
        x=risks,
        y=returns,
        mode='lines+markers',
        name='Efficient Frontier',
        line=dict(color='blue', width=2),
        marker=dict(size=4)
    ))
    
    # Optimal portfolio point
    if optimal_point:
        fig.add_trace(go.Scatter(
            x=[optimal_point[0]],
            y=[optimal_point[1]],
            mode='markers',
            name='Optimal Portfolio',
            marker=dict(size=12, color='red', symbol='star')
        ))
    
    fig.update_layout(
        title='Efficient Frontier',
        xaxis_title='Risk (Volatility)',
        yaxis_title='Expected Return',
        height=400,
        showlegend=True
    )
    
    return fig

# Main application
def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">📊 Financial Decision Engine</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["Portfolio Optimization", "Risk Analysis", "RAG Assistant", "System Status"]
    )
    
    if page == "Portfolio Optimization":
        portfolio_optimization_page()
    elif page == "Risk Analysis":
        risk_analysis_page()
    elif page == "RAG Assistant":
        rag_assistant_page()
    elif page == "System Status":
        system_status_page()

def portfolio_optimization_page():
    """Portfolio optimization interface"""
    st.header("🎯 Portfolio Optimization")
    
    # Configuration sidebar
    st.sidebar.subheader("Optimization Settings")
    num_assets = st.sidebar.slider("Number of Assets", 5, 20, 10)
    risk_aversion = st.sidebar.slider("Risk Aversion", 0.5, 10.0, 3.0, 0.5)
    use_constraints = st.sidebar.checkbox("Use Position Constraints", True)
    
    if use_constraints:
        max_weight = st.sidebar.slider("Max Asset Weight", 0.05, 0.50, 0.10, 0.01)
        min_weight = st.sidebar.slider("Min Asset Weight", 0.0, 0.05, 0.01, 0.005)
    
    # Generate or load data
    st.subheader("📊 Portfolio Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎲 Generate Sample Data"):
            st.session_state.portfolio_data = generate_sample_data(num_assets)
    
    with col2:
        if st.button("🔄 Refresh from API"):
            # In a real implementation, this would fetch actual market data
            st.session_state.portfolio_data = generate_sample_data(num_assets)
    
    # Initialize data if not exists
    if 'portfolio_data' not in st.session_state:
        st.session_state.portfolio_data = generate_sample_data(num_assets)
    
    data = st.session_state.portfolio_data
    
    # Display current data
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Expected Returns")
        returns_df = pd.DataFrame.from_dict(data["expected_returns"], orient='index', columns=['Expected Return'])
        returns_df['Expected Return'] = returns_df['Expected Return'].apply(lambda x: f"{x:.2%}")
        st.dataframe(returns_df)
    
    with col2:
        st.subheader("Asset Volatilities")
        vol_df = pd.DataFrame.from_dict(data["volatilities"], orient='index', columns=['Volatility'])
        vol_df['Volatility'] = vol_df['Volatility'].apply(lambda x: f"{x:.2%}")
        st.dataframe(vol_df)
    
    # Optimization
    st.subheader("⚡ Run Optimization")
    
    if st.button("🚀 Optimize Portfolio"):
        with st.spinner("Optimizing portfolio..."):
            
            # Prepare optimization request
            constraints = {}
            if use_constraints:
                constraints = {
                    "max_weight": max_weight,
                    "min_weight": min_weight
                }
            
            optimization_request = {
                "assets": data["assets"],
                "expected_returns": data["expected_returns"],
                "covariance_matrix": data["covariance_matrix"],
                "risk_aversion": risk_aversion,
                "constraints": constraints
            }
            
            # Call API (with fallback to demo calculation)
            result = call_api_endpoint("/optimize", "POST", optimization_request)
            
            if "error" not in result:
                st.success("✅ Optimization completed!")
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 Optimized Portfolio")
                    portfolio_weights = result["portfolio"]
                    
                    # Create portfolio DataFrame
                    portfolio_df = pd.DataFrame.from_dict(portfolio_weights, orient='index', columns=['Weight'])
                    portfolio_df['Weight'] = portfolio_df['Weight'].apply(lambda x: f"{x:.2%}")
                    st.dataframe(portfolio_df)
                    
                    # Portfolio chart
                    fig = create_portfolio_chart(result["portfolio"], "Optimized Portfolio Allocation")
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    st.subheader("📊 Performance Metrics")
                    metrics = result["metrics"]
                    
                    st.metric("Expected Return", f"{metrics['expected_return']:.2%}")
                    st.metric("Volatility", f"{metrics['volatility']:.2%}")
                    st.metric("Sharpe Ratio", f"{metrics['sharpe_ratio']:.3f}")
                    st.metric("Concentration (HHI)", f"{metrics['concentration_hhi']:.4f}")
                
                # Store results for other pages
                st.session_state.optimization_result = result
                
            else:
                st.error("❌ Optimization failed. Please check your inputs and try again.")

def risk_analysis_page():
    """Risk analysis interface"""
    st.header("⚠️ Risk Analysis")
    
    # Check if we have optimization results
    if 'optimization_result' not in st.session_state:
        st.warning("⚠️ Please run portfolio optimization first to see risk analysis.")
        return
    
    result = st.session_state.optimization_result
    portfolio_weights = result["portfolio"]
    
    st.subheader("🎯 Current Portfolio Risk Metrics")
    
    # Calculate additional risk metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Portfolio Volatility", f"{result['metrics']['volatility']:.2%}")
    
    with col2:
        hhi = result['metrics']['concentration_hhi']
        st.metric("Concentration (HHI)", f"{hhi:.4f}")
    
    with col3:
        effective_assets = 1 / hhi if hhi > 0 else 0
        st.metric("Effective # of Assets", f"{effective_assets:.1f}")
    
    with col4:
        max_weight = max(portfolio_weights.values())
        st.metric("Max Asset Weight", f"{max_weight:.2%}")
    
    # Concentration repair demonstration
    st.subheader("🔧 Concentration Repair")
    
    col1, col2 = st.columns(2)
    
    with col1:
        max_concentration = st.slider("Max Asset Concentration", 0.01, 0.20, 0.05, 0.01)
        
        if st.button("🛠️ Repair Concentration"):
            repair_request = {
                "current_weights": portfolio_weights,
                "max_concentration": max_concentration
            }
            
            repair_result = call_api_endpoint("/repair-concentration", "POST", repair_request)
            
            if "error" not in repair_result:
                st.session_state.repair_result = repair_result
                st.success("✅ Concentration repair completed!")
    
    with col2:
        if 'repair_result' in st.session_state:
            repair_result = st.session_state.repair_result
            
            st.subheader("Repair Results")
            metrics = repair_result["metrics"]
            
            st.metric("Original HHI", f"{metrics['original_hhi']:.4f}")
            st.metric("Repaired HHI", f"{metrics['repaired_hhi']:.4f}")
            st.metric("HHI Reduction", f"{metrics['concentration_reduction']:.4f}")
    
    # Risk scenario analysis
    st.subheader("📉 Stress Testing")
    
    scenarios = {
        "Market Crash (-30%)": -0.30,
        "Moderate Decline (-15%)": -0.15,
        "Normal Volatility": 0.0,
        "Bull Market (+20%)": 0.20
    }
    
    scenario_results = []
    portfolio_return = result['metrics']['expected_return']
    portfolio_vol = result['metrics']['volatility']
    
    for scenario_name, shock in scenarios.items():
        stressed_return = portfolio_return + shock
        scenario_results.append({
            "Scenario": scenario_name,
            "Portfolio Return": f"{stressed_return:.2%}",
            "Market Shock": f"{shock:.1%}"
        })
    
    scenario_df = pd.DataFrame(scenario_results)
    st.dataframe(scenario_df)

def rag_assistant_page():
    """RAG-based financial assistant"""
    st.header("🤖 Financial Assistant (RAG)")
    
    st.markdown("""
    Ask questions about portfolio management, risk analysis, or investment strategies.
    The assistant uses retrieval-augmented generation to provide informed responses.
    """)
    
    # Sample questions
    st.subheader("💡 Sample Questions")
    sample_questions = [
        "How do I manage portfolio risk?",
        "What is mean variance optimization?",
        "How to measure portfolio concentration?",
        "What are the benefits of ESG investing?",
        "Explain factor investing strategies"
    ]
    
    selected_question = st.selectbox("Choose a sample question:", [""] + sample_questions)
    
    # Query input
    user_query = st.text_area(
        "Your question:",
        value=selected_question,
        height=100,
        help="Enter your financial question here"
    )
    
    if st.button("🔍 Get Answer") and user_query:
        with st.spinner("Searching knowledge base..."):
            
            # For demo purposes, use the minimal RAG system
            try:
                from src.rag.rag_minimal import SimpleRAG
                
                # Initialize and populate RAG system
                rag = SimpleRAG()
                rag.add_financial_documents()
                
                # Query the RAG system
                result = rag.query(user_query, top_k=3)
                
                # Display response
                st.subheader("📝 Response")
                st.write(result["response"])
                
                # Display source documents
                if result["context_documents"]:
                    st.subheader("📚 Source Documents")
                    
                    for i, doc in enumerate(result["context_documents"]):
                        with st.expander(f"Source {i+1} (Relevance: {doc['relevance_score']:.3f})"):
                            st.write(doc["content"])
                            
                            if doc["metadata"]:
                                st.json(doc["metadata"])
                
            except Exception as e:
                st.error(f"RAG system error: {str(e)}")
                
                # Fallback response
                st.info("""
                **Demo Response:**
                
                Thank you for your question about financial topics. In a production system, 
                this would be answered using our knowledge base of financial documents, 
                research papers, and best practices.
                
                For specific financial advice, please consult with a qualified financial advisor.
                """)

def system_status_page():
    """System status and health checks"""
    st.header("🔧 System Status")
    
    # API Health Check
    st.subheader("🏥 API Health")
    
    health_result = call_api_endpoint("/health")
    
    if "error" not in health_result:
        st.success("✅ API is running")
        st.json(health_result)
    else:
        st.error("❌ API is not accessible")
    
    # System Configuration
    st.subheader("⚙️ Configuration")
    
    config_info = {
        "API Base URL": API_BASE_URL,
        "Streamlit Version": st.__version__,
        "Demo Mode": "Enabled" if "error" in call_api_endpoint("/") else "Disabled"
    }
    
    for key, value in config_info.items():
        st.text(f"{key}: {value}")
    
    # Sample Data Info
    if 'portfolio_data' in st.session_state:
        st.subheader("📊 Current Sample Data")
        data = st.session_state.portfolio_data
        
        st.text(f"Number of Assets: {len(data['assets'])}")
        st.text(f"Assets: {', '.join(data['assets'])}")
    
    # Clear Cache
    st.subheader("🗑️ Cache Management")
    if st.button("Clear All Cache"):
        st.cache_data.clear()
        if 'portfolio_data' in st.session_state:
            del st.session_state.portfolio_data
        if 'optimization_result' in st.session_state:
            del st.session_state.optimization_result
        if 'repair_result' in st.session_state:
            del st.session_state.repair_result
        st.success("✅ Cache cleared!")

# Disclaimer
def show_disclaimer():
    """Show financial disclaimer"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    **⚠️ Important Disclaimer:**
    
    This application is for educational and demonstration purposes only. 
    It does not constitute financial advice. Always consult with qualified 
    financial advisors before making investment decisions.
    """)

if __name__ == "__main__":
    # Show disclaimer
    show_disclaimer()
    
    # Run main app
    main()