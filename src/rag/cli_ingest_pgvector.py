#!/usr/bin/env python3
"""
CLI tool for ingesting documents into the PGVector RAG system.

This script allows batch ingestion of financial documents from various sources
into the vector database for retrieval-augmented generation.
"""

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import sys

try:
    from .rag_pgvector import PGVectorRAG
except ImportError:
    # For direct execution
    sys.path.append(str(Path(__file__).parent.parent.parent))
    from src.rag.rag_pgvector import PGVectorRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_sample_documents() -> List[Dict[str, Any]]:
    """Load sample financial documents for testing"""
    return [
        {
            "content": """
            Modern Portfolio Theory (MPT) Fundamentals:
            
            MPT is a mathematical framework for constructing portfolios that maximize 
            expected return for a given level of risk. Key concepts:
            
            1. Efficient Frontier: The set of optimal portfolios offering the highest 
               expected return for each level of risk
            2. Risk-Return Tradeoff: Higher returns generally require accepting higher risk
            3. Diversification: Spreading investments across uncorrelated assets reduces risk
            4. Correlation: The degree to which asset prices move together
            5. Sharpe Ratio: Measure of risk-adjusted return (excess return / volatility)
            
            MPT assumes rational investors, normal return distributions, and known 
            correlations. While simplified, it provides a foundation for portfolio 
            construction.
            """,
            "metadata": {
                "title": "Modern Portfolio Theory Fundamentals",
                "category": "theory",
                "topic": "portfolio_optimization",
                "difficulty": "intermediate",
                "source": "education"
            }
        },
        {
            "content": """
            Risk Management in Portfolio Construction:
            
            Effective risk management is crucial for long-term investment success:
            
            1. Diversification Strategies:
               - Asset class diversification (stocks, bonds, alternatives)
               - Geographic diversification (domestic vs international)
               - Sector diversification to avoid concentration risk
               - Time diversification through systematic investing
            
            2. Risk Measurement:
               - Volatility (standard deviation of returns)
               - Value at Risk (VaR): Maximum expected loss over time horizon
               - Conditional VaR: Expected loss beyond VaR threshold
               - Maximum Drawdown: Largest peak-to-trough decline
            
            3. Risk Control Techniques:
               - Position sizing and concentration limits
               - Stop-loss orders and profit-taking rules
               - Hedging with derivatives
               - Regular portfolio rebalancing
            """,
            "metadata": {
                "title": "Portfolio Risk Management",
                "category": "risk_management",
                "topic": "risk_control",
                "difficulty": "intermediate",
                "source": "best_practices"
            }
        },
        {
            "content": """
            Factor Investing and Smart Beta Strategies:
            
            Factor investing targets specific return drivers beyond market exposure:
            
            1. Equity Risk Factors:
               - Value: Preference for undervalued stocks (low P/E, P/B ratios)
               - Momentum: Stocks with strong recent performance continue trending
               - Quality: Companies with strong fundamentals (high ROE, low debt)
               - Size: Small-cap stocks historically outperform large-cap
               - Low Volatility: Lower-risk stocks often provide better risk-adjusted returns
               - Profitability: Companies with high and stable earnings growth
            
            2. Implementation Approaches:
               - Single-factor strategies focusing on one factor
               - Multi-factor strategies combining multiple factors
               - Dynamic factor allocation based on market conditions
               - Factor timing and rotation strategies
            
            3. Considerations:
               - Factor performance varies over time
               - Crowding can reduce factor effectiveness
               - Implementation costs and turnover matter
            """,
            "metadata": {
                "title": "Factor Investing Guide",
                "category": "strategies",
                "topic": "factor_investing",
                "difficulty": "advanced",
                "source": "research"
            }
        },
        {
            "content": """
            ESG Integration in Investment Decisions:
            
            Environmental, Social, and Governance (ESG) factors increasingly impact 
            investment returns and risk:
            
            1. ESG Implementation Approaches:
               - Negative Screening: Excluding harmful industries (tobacco, weapons)
               - Positive Screening: Selecting ESG leaders within sectors
               - Best-in-Class: Choosing top ESG performers across all sectors
               - Thematic Investing: Targeting specific ESG themes (clean energy, water)
               - ESG Integration: Incorporating ESG factors into fundamental analysis
               - Impact Investing: Seeking measurable positive impact alongside returns
            
            2. ESG Data and Metrics:
               - Carbon footprint and emissions data
               - Board diversity and executive compensation
               - Labor practices and supply chain management
               - Data quality and standardization challenges
            
            3. Performance Considerations:
               - ESG factors can improve risk-adjusted returns
               - Regulatory trends favor ESG integration
               - Growing investor demand for sustainable investing
            """,
            "metadata": {
                "title": "ESG Integration Strategies",
                "category": "esg",
                "topic": "sustainable_investing",
                "difficulty": "intermediate",
                "source": "trends"
            }
        },
        {
            "content": """
            Concentration Risk and Portfolio Diversification:
            
            Concentration risk arises when portfolios are overly exposed to specific 
            investments, sectors, or risk factors:
            
            1. Types of Concentration Risk:
               - Name Concentration: Too much weight in individual securities
               - Sector Concentration: Overexposure to specific industries
               - Geographic Concentration: Excessive regional/country exposure
               - Currency Concentration: Unhedged foreign exchange risk
               - Factor Concentration: Overexposure to specific risk factors
            
            2. Measurement Tools:
               - Herfindahl-Hirschman Index (HHI): Sum of squared weights
               - Effective Number of Assets: 1/HHI
               - Concentration Ratios: Weight in top N holdings
               - Active Share: Deviation from benchmark weights
            
            3. Mitigation Strategies:
               - Position limits and concentration constraints
               - Systematic rebalancing procedures
               - Correlation-aware optimization
               - Alternative investment diversifiers
               - Dynamic hedging strategies
            """,
            "metadata": {
                "title": "Concentration Risk Management",
                "category": "risk_management", 
                "topic": "diversification",
                "difficulty": "advanced",
                "source": "technical"
            }
        }
    ]


def ingest_documents(rag: PGVectorRAG, documents: List[Dict[str, Any]]) -> None:
    """
    Ingest a list of documents into the RAG system
    
    Args:
        rag: PGVectorRAG instance
        documents: List of document dictionaries with 'content' and 'metadata'
    """
    logger.info(f"Starting ingestion of {len(documents)} documents...")
    
    for i, doc in enumerate(documents):
        try:
            doc_id = f"sample_doc_{i:03d}"
            rag.add_document(
                content=doc["content"],
                metadata=doc["metadata"],
                doc_id=doc_id
            )
            logger.info(f"Ingested document {doc_id}: {doc['metadata'].get('title', 'Untitled')}")
            
        except Exception as e:
            logger.error(f"Failed to ingest document {i}: {e}")
    
    logger.info("Document ingestion completed!")


def ingest_from_file(rag: PGVectorRAG, file_path: Path) -> None:
    """
    Ingest documents from a JSON file
    
    Args:
        rag: PGVectorRAG instance
        file_path: Path to JSON file containing documents
    """
    try:
        with open(file_path, 'r') as f:
            documents = json.load(f)
        
        if not isinstance(documents, list):
            documents = [documents]
        
        ingest_documents(rag, documents)
        
    except Exception as e:
        logger.error(f"Failed to ingest from file {file_path}: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Ingest documents into PGVector RAG system"
    )
    
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Ingest sample financial documents"
    )
    
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON file containing documents to ingest"
    )
    
    parser.add_argument(
        "--connection-string",
        type=str,
        help="PostgreSQL connection string (uses PGVECTOR_URL env var if not provided)"
    )
    
    parser.add_argument(
        "--test-query",
        type=str,
        help="Test query to run after ingestion"
    )
    
    args = parser.parse_args()
    
    if not args.sample and not args.file:
        parser.error("Must specify either --sample or --file")
    
    try:
        # Initialize RAG system
        logger.info("Initializing PGVector RAG system...")
        rag = PGVectorRAG(connection_string=args.connection_string)
        
        # Ingest documents
        if args.sample:
            documents = load_sample_documents()
            ingest_documents(rag, documents)
        
        if args.file:
            file_path = Path(args.file)
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return
            ingest_from_file(rag, file_path)
        
        # Test query
        if args.test_query:
            logger.info(f"Testing query: {args.test_query}")
            result = rag.query(args.test_query)
            print(f"\nQuery: {result['query']}")
            print(f"Response: {result['response']}")
            print(f"Found {result['num_documents_found']} relevant documents")
        
        # Print stats
        stats = rag.get_stats()
        logger.info(f"RAG system stats: {stats}")
        
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())