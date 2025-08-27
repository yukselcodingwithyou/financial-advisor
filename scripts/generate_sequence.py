#!/usr/bin/env python3
"""
Generate sequence diagrams for key workflows using Graphviz.

This script creates sequence diagrams showing the flow of operations
through the Financial Decision Engine system.
"""

import os
from pathlib import Path
import graphviz


def create_optimization_sequence():
    """Create sequence diagram for portfolio optimization workflow"""
    
    dot = graphviz.Digraph(
        'optimization_sequence',
        comment='Portfolio Optimization Sequence',
        format='png'
    )
    
    dot.attr(rankdir='TB', size='12,10', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define actors/components
    actors = [
        ('client', 'Client\n(Streamlit/API)', '#FFE0B2'),
        ('api', 'FastAPI\nService', '#E3F2FD'),
        ('feast', 'Feast\nFeature Store', '#F3E5F5'),
        ('optimizer', 'Portfolio\nOptimizer', '#E8F5E8'),
        ('risk_mgmt', 'Risk\nManager', '#FFEB3B'),
        ('mlflow', 'MLflow\nLogger', '#E0F2F1'),
    ]
    
    # Create nodes
    for actor_id, label, color in actors:
        dot.node(actor_id, label, fillcolor=color)
    
    # Define sequence steps
    steps = [
        ('client', 'api', '1. POST /optimize\n{assets, returns, covariance}'),
        ('api', 'feast', '2. get_features()\nretrieve factor exposures'),
        ('feast', 'api', '3. return features'),
        ('api', 'optimizer', '4. mean_variance_optimize()\nmu, sigma, constraints'),
        ('optimizer', 'optimizer', '5. solve CVXPY\noptimization problem'),
        ('optimizer', 'api', '6. return optimal weights'),
        ('api', 'risk_mgmt', '7. check_concentration()\nHHI analysis'),
        ('risk_mgmt', 'risk_mgmt', '8. repair_concentration()\nif violations found'),
        ('risk_mgmt', 'api', '9. return final weights'),
        ('api', 'mlflow', '10. log_optimization_run()\nmetrics & portfolio'),
        ('mlflow', 'api', '11. return run_id'),
        ('api', 'client', '12. return portfolio\nwith metrics'),
    ]
    
    # Create a vertical layout showing the sequence
    with dot.subgraph() as s:
        s.attr(rank='same')
        for actor_id, _, _ in actors:
            s.node(f"{actor_id}_line", '', shape='point', width='0')
    
    # Add sequence arrows
    for i, (src, dst, label) in enumerate(steps):
        dot.edge(src, dst, label=f"{label}", fontsize='8')
    
    return dot


def create_rag_sequence():
    """Create sequence diagram for RAG query workflow"""
    
    dot = graphviz.Digraph(
        'rag_sequence',
        comment='RAG Query Sequence',
        format='png'
    )
    
    dot.attr(rankdir='TB', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define actors
    actors = [
        ('user', 'User', '#FFCDD2'),
        ('streamlit', 'Streamlit\nRAG Page', '#F8BBD9'),
        ('rag_system', 'RAG\nSystem', '#E1BEE7'),
        ('postgres', 'PostgreSQL\n+ pgvector', '#C5CAE9'),
        ('embeddings', 'Embedding\nModel', '#BBDEFB'),
    ]
    
    # Create nodes
    for actor_id, label, color in actors:
        dot.node(actor_id, label, fillcolor=color)
    
    # Define sequence
    steps = [
        ('user', 'streamlit', '1. Enter financial\nquestion'),
        ('streamlit', 'rag_system', '2. query(question)'),
        ('rag_system', 'embeddings', '3. generate_embedding()\nquestion vector'),
        ('embeddings', 'rag_system', '4. return embedding'),
        ('rag_system', 'postgres', '5. similarity_search()\nvector <=> embedding'),
        ('postgres', 'rag_system', '6. return relevant\ndocuments'),
        ('rag_system', 'rag_system', '7. generate_response()\nRAG synthesis'),
        ('rag_system', 'streamlit', '8. return response\n+ source docs'),
        ('streamlit', 'user', '9. display answer\nwith sources'),
    ]
    
    # Add sequence arrows
    for src, dst, label in steps:
        dot.edge(src, dst, label=label, fontsize='8')
    
    return dot


def create_feature_pipeline_sequence():
    """Create sequence diagram for feature engineering pipeline"""
    
    dot = graphviz.Digraph(
        'feature_pipeline_sequence',
        comment='Feature Engineering Pipeline',
        format='png'
    )
    
    dot.attr(rankdir='TB', size='12,10', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define components
    actors = [
        ('scheduler', 'Scheduler\n(Airflow/Cron)', '#FFAB91'),
        ('dbt', 'dbt Core', '#FFE0B2'),
        ('bigquery', 'BigQuery\nData Warehouse', '#FFF9C4'),
        ('feature_store', 'Feast\nFeature Store', '#DCEDC8'),
        ('postgres', 'PostgreSQL\nOnline Store', '#BBDEFB'),
        ('api', 'FastAPI\nService', '#E1BEE7'),
    ]
    
    # Create nodes
    for actor_id, label, color in actors:
        dot.node(actor_id, label, fillcolor=color)
    
    # Define pipeline steps
    steps = [
        ('scheduler', 'dbt', '1. trigger daily\nfeature refresh'),
        ('dbt', 'bigquery', '2. execute SQL models\nmomentum, value, etc.'),
        ('bigquery', 'dbt', '3. return computed\nfeatures'),
        ('dbt', 'feature_store', '4. materialize features\nto Feast offline store'),
        ('feature_store', 'postgres', '5. sync to online store\nfor real-time serving'),
        ('postgres', 'feature_store', '6. confirm sync'),
        ('feature_store', 'api', '7. notify feature\navailability'),
        ('api', 'api', '8. update feature\ncache/metadata'),
    ]
    
    # Add sequence arrows
    for src, dst, label in steps:
        dot.edge(src, dst, label=label, fontsize='8')
    
    return dot


def create_risk_management_sequence():
    """Create sequence diagram for risk management workflow"""
    
    dot = graphviz.Digraph(
        'risk_management_sequence',
        comment='Risk Management Sequence',
        format='png'
    )
    
    dot.attr(rankdir='TB', size='10,8', dpi='300')
    dot.attr('node', shape='box', style='rounded,filled', fontname='Arial', fontsize='10')
    dot.attr('edge', fontname='Arial', fontsize='9')
    
    # Define components
    actors = [
        ('portfolio', 'Portfolio\nInput', '#FFCDD2'),
        ('risk_analyzer', 'Risk\nAnalyzer', '#F8BBD9'),
        ('policy_engine', 'Policy\nEngine', '#E1BEE7'),
        ('optimizer', 'Concentration\nRepair', '#C5CAE9'),
        ('validator', 'Risk\nValidator', '#BBDEFB'),
    ]
    
    # Create nodes
    for actor_id, label, color in actors:
        dot.node(actor_id, label, fillcolor=color)
    
    # Define sequence
    steps = [
        ('portfolio', 'risk_analyzer', '1. analyze(weights)\ncalculate HHI, exposures'),
        ('risk_analyzer', 'policy_engine', '2. check_policies()\nconcentration limits'),
        ('policy_engine', 'risk_analyzer', '3. return violations\nif any found'),
        ('risk_analyzer', 'optimizer', '4. repair_concentration()\nif violations exist'),
        ('optimizer', 'optimizer', '5. solve CVXPY\noptimization'),
        ('optimizer', 'risk_analyzer', '6. return repaired\nweights'),
        ('risk_analyzer', 'validator', '7. validate_final()\ncheck all constraints'),
        ('validator', 'portfolio', '8. return final\nportfolio + metrics'),
    ]
    
    # Add sequence arrows
    for src, dst, label in steps:
        dot.edge(src, dst, label=label, fontsize='8')
    
    return dot


def main():
    """Generate and save sequence diagrams"""
    
    # Create output directory
    output_dir = Path('docs/images')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating Financial Decision Engine sequence diagrams...")
    
    try:
        # Generate optimization sequence
        opt_diagram = create_optimization_sequence()
        opt_diagram.render(
            str(output_dir / 'sequence_optimization'),
            cleanup=True
        )
        print(f"✅ Optimization sequence saved to {output_dir / 'sequence_optimization.png'}")
        
        # Generate RAG sequence
        rag_diagram = create_rag_sequence()
        rag_diagram.render(
            str(output_dir / 'sequence_rag'),
            cleanup=True
        )
        print(f"✅ RAG sequence saved to {output_dir / 'sequence_rag.png'}")
        
        # Generate feature pipeline sequence
        pipeline_diagram = create_feature_pipeline_sequence()
        pipeline_diagram.render(
            str(output_dir / 'sequence_feature_pipeline'),
            cleanup=True
        )
        print(f"✅ Feature pipeline sequence saved to {output_dir / 'sequence_feature_pipeline.png'}")
        
        # Generate risk management sequence
        risk_diagram = create_risk_management_sequence()
        risk_diagram.render(
            str(output_dir / 'sequence_risk_management'),
            cleanup=True
        )
        print(f"✅ Risk management sequence saved to {output_dir / 'sequence_risk_management.png'}")
        
        print("\n📊 Sequence diagrams generated successfully!")
        print("These diagrams show the workflow for:")
        print("1. Portfolio optimization process")
        print("2. RAG query and response generation")
        print("3. Feature engineering pipeline")
        print("4. Risk management and concentration repair")
        
    except Exception as e:
        print(f"❌ Error generating sequence diagrams: {e}")
        print("Make sure Graphviz is installed: pip install graphviz")
        print("And system Graphviz: apt-get install graphviz (Ubuntu) or brew install graphviz (Mac)")


if __name__ == "__main__":
    main()