#!/usr/bin/env python3
"""
Generate system architecture diagram using Graphviz.

This script creates a visual representation of the Financial Decision Engine
architecture showing the relationships between components.
"""

import os
from pathlib import Path
import graphviz


def create_architecture_diagram():
    """Create the main system architecture diagram"""
    
    # Create a directed graph
    dot = graphviz.Digraph(
        'financial_decision_engine_architecture',
        comment='Financial Decision Engine Architecture',
        format='png'
    )
    
    # Set graph attributes
    dot.attr(rankdir='TB', size='12,10', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial')
    dot.attr('edge', fontname='Arial', fontsize='10')
    
    # Define color scheme
    colors = {
        'api': '#E3F2FD',           # Light blue
        'data': '#F3E5F5',          # Light purple  
        'ml': '#E8F5E8',            # Light green
        'storage': '#FFF3E0',       # Light orange
        'frontend': '#FCE4EC',      # Light pink
        'external': '#F5F5F5'       # Light gray
    }
    
    # Frontend Layer
    with dot.subgraph(name='cluster_frontend') as frontend:
        frontend.attr(label='Frontend Layer', style='filled', color='lightgray')
        frontend.node('streamlit', 'Streamlit Demo\nApp', fillcolor=colors['frontend'])
        frontend.node('jupyter', 'Jupyter\nNotebooks', fillcolor=colors['frontend'])
        frontend.node('reports', 'Generated\nReports', fillcolor=colors['frontend'])
    
    # API Layer
    with dot.subgraph(name='cluster_api') as api:
        api.attr(label='API Layer', style='filled', color='lightgray')
        api.node('fastapi', 'FastAPI\nService', fillcolor=colors['api'])
        api.node('endpoints', 'REST Endpoints:\n/optimize\n/repair-concentration\n/risk-metrics', 
                fillcolor=colors['api'])
    
    # Core Engine
    with dot.subgraph(name='cluster_engine') as engine:
        engine.attr(label='Portfolio Optimization Engine', style='filled', color='lightgray')
        engine.node('optimizer', 'Mean-Variance\nOptimizer', fillcolor=colors['ml'])
        engine.node('risk_mgmt', 'Risk Management\n& HHI Repair', fillcolor=colors['ml'])
        engine.node('factor_model', 'Factor Models\n& Tilts', fillcolor=colors['ml'])
    
    # Data Processing
    with dot.subgraph(name='cluster_data') as data:
        data.attr(label='Data Processing Layer', style='filled', color='lightgray')
        data.node('dbt', 'dbt Models\n(Feature Engineering)', fillcolor=colors['data'])
        data.node('feast', 'Feast\nFeature Store', fillcolor=colors['data'])
        data.node('rag', 'RAG System\n(Document Retrieval)', fillcolor=colors['data'])
    
    # Storage Layer
    with dot.subgraph(name='cluster_storage') as storage:
        storage.attr(label='Storage Layer', style='filled', color='lightgray')
        storage.node('postgres', 'PostgreSQL\n+ pgvector', fillcolor=colors['storage'])
        storage.node('mlflow_store', 'MLflow\nExperiment Store', fillcolor=colors['storage'])
        storage.node('redis', 'Redis\nCache', fillcolor=colors['storage'])
    
    # External Data Sources
    with dot.subgraph(name='cluster_external') as external:
        external.attr(label='External Data Sources', style='filled', color='lightgray')
        external.node('bigquery', 'BigQuery\n(Market Data)', fillcolor=colors['external'])
        external.node('market_data', 'Market Data\nProviders', fillcolor=colors['external'])
        external.node('fundamental', 'Fundamental\nData', fillcolor=colors['external'])
    
    # MLOps & Monitoring
    with dot.subgraph(name='cluster_mlops') as mlops:
        mlops.attr(label='MLOps & Monitoring', style='filled', color='lightgray')
        mlops.node('mlflow', 'MLflow\nTracking', fillcolor=colors['ml'])
        mlops.node('monitoring', 'Performance\nMonitoring', fillcolor=colors['ml'])
        mlops.node('ci_cd', 'CI/CD Pipeline\n(GitHub Actions)', fillcolor=colors['ml'])
    
    # Define connections
    connections = [
        # Frontend to API
        ('streamlit', 'fastapi'),
        ('jupyter', 'fastapi'),
        ('reports', 'fastapi'),
        
        # API to Engine
        ('fastapi', 'endpoints'),
        ('endpoints', 'optimizer'),
        ('endpoints', 'risk_mgmt'),
        ('endpoints', 'factor_model'),
        
        # Engine to Data
        ('optimizer', 'feast'),
        ('risk_mgmt', 'feast'),
        ('factor_model', 'feast'),
        ('rag', 'fastapi'),
        
        # Data Processing
        ('dbt', 'feast'),
        ('bigquery', 'dbt'),
        ('market_data', 'dbt'),
        ('fundamental', 'dbt'),
        
        # Storage connections
        ('feast', 'postgres'),
        ('rag', 'postgres'),
        ('dbt', 'postgres'),
        ('fastapi', 'redis'),
        
        # MLOps connections
        ('optimizer', 'mlflow'),
        ('risk_mgmt', 'mlflow'),
        ('mlflow', 'mlflow_store'),
        ('ci_cd', 'fastapi'),
        ('monitoring', 'fastapi'),
    ]
    
    # Add edges
    for src, dst in connections:
        dot.edge(src, dst)
    
    return dot


def create_data_flow_diagram():
    """Create a data flow diagram"""
    
    dot = graphviz.Digraph(
        'data_flow',
        comment='Data Flow Diagram',
        format='png'
    )
    
    dot.attr(rankdir='LR', size='14,8', dpi='300')
    dot.attr('node', shape='ellipse', style='filled', fontname='Arial')
    dot.attr('edge', fontname='Arial', fontsize='10')
    
    # Data flow stages
    stages = [
        ('raw_data', 'Raw Market\nData', '#FFCDD2'),
        ('feature_eng', 'Feature\nEngineering', '#F8BBD9'),
        ('feature_store', 'Feature\nStore', '#E1BEE7'),
        ('optimization', 'Portfolio\nOptimization', '#C5CAE9'),
        ('risk_mgmt', 'Risk\nManagement', '#BBDEFB'),
        ('output', 'Portfolio\nWeights', '#B2DFDB'),
    ]
    
    for node_id, label, color in stages:
        dot.node(node_id, label, fillcolor=color)
    
    # Add connections with labels
    flow_connections = [
        ('raw_data', 'feature_eng', 'dbt transforms'),
        ('feature_eng', 'feature_store', 'Feast storage'),
        ('feature_store', 'optimization', 'retrieve features'),
        ('optimization', 'risk_mgmt', 'initial weights'),
        ('risk_mgmt', 'output', 'final weights'),
    ]
    
    for src, dst, label in flow_connections:
        dot.edge(src, dst, label=label)
    
    return dot


def main():
    """Generate and save architecture diagrams"""
    
    # Create output directory
    output_dir = Path('docs/images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Financial Decision Engine architecture diagrams...")
    
    try:
        # Generate main architecture diagram
        arch_diagram = create_architecture_diagram()
        arch_diagram.render(
            str(output_dir / 'architecture'),
            cleanup=True
        )
        print(f"✅ Architecture diagram saved to {output_dir / 'architecture.png'}")
        
        # Generate data flow diagram
        flow_diagram = create_data_flow_diagram()
        flow_diagram.render(
            str(output_dir / 'data_flow'),
            cleanup=True
        )
        print(f"✅ Data flow diagram saved to {output_dir / 'data_flow.png'}")
        
        print("\n📊 Architecture diagrams generated successfully!")
        print("These diagrams show:")
        print("1. System architecture with all components and their relationships")
        print("2. Data flow from raw inputs to final portfolio outputs")
        
    except Exception as e:
        print(f"❌ Error generating diagrams: {e}")
        print("Make sure Graphviz is installed: pip install graphviz")
        print("And system Graphviz: apt-get install graphviz (Ubuntu) or brew install graphviz (Mac)")


if __name__ == "__main__":
    main()