"""
Minimal RAG implementation for the Financial Decision Engine.

This module provides a simple in-memory RAG system for development and testing.
For production use, consider PGVectorRAG with proper vector database.
"""

import logging
from datetime import datetime
from typing import Any

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


class SimpleRAG:
    """
    Simple in-memory RAG implementation using TF-IDF for document retrieval.

    This is a minimal implementation suitable for development and small-scale use.
    For production, use PGVectorRAG with proper vector embeddings.
    """

    def __init__(self, max_docs: int = 1000):
        """
        Initialize SimpleRAG

        Args:
            max_docs: Maximum number of documents to store
        """
        self.max_docs = max_docs
        self.documents: list[dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(
            max_features=1000, stop_words="english", ngram_range=(1, 2)
        )
        self.doc_vectors = None
        self._is_fitted = False

    def add_document(self, content: str, metadata: dict[str, Any] | None = None) -> str:
        """
        Add a document to the RAG system

        Args:
            content: Document text content
            metadata: Optional metadata dictionary

        Returns:
            Document ID
        """
        if metadata is None:
            metadata = {}

        doc_id = f"doc_{len(self.documents)}_{datetime.now().timestamp()}"

        doc = {
            "id": doc_id,
            "content": content,
            "metadata": metadata,
            "timestamp": datetime.now().isoformat(),
            "content_length": len(content),
        }

        self.documents.append(doc)

        # Limit document storage
        if len(self.documents) > self.max_docs:
            self.documents = self.documents[-self.max_docs :]

        # Re-fit vectorizer when documents change
        self._is_fitted = False

        logger.info(f"Added document {doc_id}, total documents: {len(self.documents)}")
        return doc_id

    def add_financial_documents(self) -> None:
        """Add sample financial documents for testing"""
        sample_docs = [
            {
                "content": """
                Portfolio Risk Management Best Practices:
                1. Diversification across asset classes, sectors, and geographies
                2. Regular rebalancing to maintain target allocations
                3. Stress testing against historical scenarios
                4. Monitoring concentration limits and exposure constraints
                5. Using derivatives for hedging when appropriate
                """,
                "metadata": {"type": "risk_management", "category": "best_practices"},
            },
            {
                "content": """
                Mean-Variance Optimization Theory:
                Modern Portfolio Theory suggests that investors can construct portfolios
                to maximize expected return for a given level of risk. The efficient frontier
                represents the set of optimal portfolios offering the highest expected return
                for each level of risk. Key assumptions include rational investors, normal
                return distributions, and known correlations.
                """,
                "metadata": {"type": "theory", "category": "optimization"},
            },
            {
                "content": """
                ESG Integration in Portfolio Construction:
                Environmental, Social, and Governance factors can be integrated through:
                - Exclusionary screening of controversial sectors
                - Best-in-class selection within sectors
                - Thematic investing in sustainable solutions
                - ESG tilt overlays on existing strategies
                - Impact measurement and reporting
                """,
                "metadata": {"type": "esg", "category": "integration"},
            },
            {
                "content": """
                Factor Investing Fundamentals:
                Academic research has identified several factors that explain returns:
                - Value: Cheap stocks outperform expensive ones
                - Momentum: Trending stocks continue to trend
                - Quality: Profitable, stable companies outperform
                - Size: Small-cap stocks have higher expected returns
                - Low Volatility: Lower risk stocks often outperform
                """,
                "metadata": {"type": "factors", "category": "research"},
            },
            {
                "content": """
                Concentration Risk and HHI Analysis:
                The Herfindahl-Hirschman Index (HHI) measures portfolio concentration.
                HHI = sum of squared weights. Values range from 1/N to 1.
                - HHI > 0.15: Highly concentrated
                - HHI 0.05-0.15: Moderately concentrated
                - HHI < 0.05: Well diversified
                Concentration repair uses optimization to reduce HHI while minimizing changes.
                """,
                "metadata": {"type": "risk_metrics", "category": "concentration"},
            },
        ]

        for doc in sample_docs:
            self.add_document(doc["content"], doc["metadata"])

    def _fit_vectorizer(self) -> None:
        """Fit the TF-IDF vectorizer on current documents"""
        if not self.documents:
            return

        texts = [doc["content"] for doc in self.documents]
        self.doc_vectors = self.vectorizer.fit_transform(texts)
        self._is_fitted = True
        logger.info(f"Fitted vectorizer on {len(texts)} documents")

    def retrieve(self, query: str, top_k: int = 3) -> list[dict[str, Any]]:
        """
        Retrieve most relevant documents for a query

        Args:
            query: Search query
            top_k: Number of documents to return

        Returns:
            List of documents with relevance scores
        """
        if not self.documents:
            return []

        if not self._is_fitted:
            self._fit_vectorizer()

        if self.doc_vectors is None:
            return []

        # Vectorize query
        query_vector = self.vectorizer.transform([query])

        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]

        # Get top-k most similar documents
        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.01:  # Minimum similarity threshold
                doc = self.documents[idx].copy()
                doc["relevance_score"] = float(similarities[idx])
                results.append(doc)

        return results

    def generate_response(self, query: str, context_docs: list[dict[str, Any]]) -> str:
        """
        Generate a response using retrieved context (simple template-based)

        Args:
            query: User query
            context_docs: Retrieved context documents

        Returns:
            Generated response
        """
        if not context_docs:
            return "I don't have enough information to answer that question."

        # Simple template-based response
        context = "\n\n".join([doc["content"] for doc in context_docs[:2]])

        response = f"""Based on the available information:

{context}

This information is relevant to your query: "{query}"

For more specific guidance, please consult with a financial advisor or refer to additional resources."""

        return response

    def query(self, query: str, top_k: int = 3) -> dict[str, Any]:
        """
        Complete RAG query: retrieve and generate response

        Args:
            query: User query
            top_k: Number of documents to retrieve

        Returns:
            Response with context and metadata
        """
        # Retrieve relevant documents
        context_docs = self.retrieve(query, top_k)

        # Generate response
        response = self.generate_response(query, context_docs)

        return {
            "query": query,
            "response": response,
            "context_documents": context_docs,
            "num_documents_found": len(context_docs),
            "timestamp": datetime.now().isoformat(),
        }

    def get_stats(self) -> dict[str, Any]:
        """Get RAG system statistics"""
        return {
            "num_documents": len(self.documents),
            "is_fitted": self._is_fitted,
            "max_docs": self.max_docs,
            "vectorizer_features": getattr(self.vectorizer, "n_features_in_", 0)
            if self._is_fitted
            else 0,
        }


def test_rag() -> None:
    """Test the SimpleRAG implementation"""
    print("Testing SimpleRAG implementation...")

    # Initialize RAG
    rag = SimpleRAG()

    # Add sample documents
    rag.add_financial_documents()

    # Test queries
    test_queries = [
        "How do I manage portfolio risk?",
        "What is mean variance optimization?",
        "How to measure portfolio concentration?",
        "ESG integration strategies",
        "Factor investing approaches",
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        result = rag.query(query)
        print(f"Response: {result['response'][:200]}...")
        print(f"Found {result['num_documents_found']} relevant documents")

        if result["context_documents"]:
            top_doc = result["context_documents"][0]
            print(f"Top document relevance: {top_doc['relevance_score']:.3f}")

    # Print stats
    print(f"\nRAG Stats: {rag.get_stats()}")
    print("SimpleRAG test completed!")


if __name__ == "__main__":
    test_rag()
