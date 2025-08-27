"""
RAG (Retrieval Augmented Generation) package for Financial Decision Engine.

This package provides functionality for document ingestion, vector storage,
and retrieval-augmented generation for financial analysis and decision support.
"""

__version__ = "0.1.0"

from .rag_minimal import SimpleRAG, test_rag
from .rag_pgvector import PGVectorRAG

__all__ = ["SimpleRAG", "PGVectorRAG", "test_rag"]
