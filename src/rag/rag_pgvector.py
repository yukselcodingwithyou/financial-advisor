"""
PGVector-based RAG implementation for the Financial Decision Engine.

This module provides a production-ready RAG system using PostgreSQL with pgvector
extension for efficient similarity search on embeddings.
"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import json

import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
import pandas as pd

logger = logging.getLogger(__name__)


class PGVectorRAG:
    """
    Production RAG implementation using PostgreSQL with pgvector extension.
    
    Requires pgvector extension to be installed in PostgreSQL.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize PGVectorRAG
        
        Args:
            connection_string: PostgreSQL connection string
        """
        self.connection_string = connection_string or os.getenv(
            "PGVECTOR_URL",
            "postgresql://postgres:password@localhost:5432/vector_db"
        )
        self.embedding_dim = 384  # Default for sentence transformers
        self.table_name = "financial_documents"
        
        # Initialize database connection
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database tables and extensions"""
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    # Enable pgvector extension
                    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
                    
                    # Create documents table
                    cur.execute(f"""
                        CREATE TABLE IF NOT EXISTS {self.table_name} (
                            id SERIAL PRIMARY KEY,
                            doc_id VARCHAR(255) UNIQUE NOT NULL,
                            content TEXT NOT NULL,
                            metadata JSONB,
                            embedding vector({self.embedding_dim}),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """)
                    
                    # Create index on embedding for faster similarity search
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS {self.table_name}_embedding_idx 
                        ON {self.table_name} USING ivfflat (embedding vector_cosine_ops)
                        WITH (lists = 100);
                    """)
                    
                    # Create index on metadata for filtering
                    cur.execute(f"""
                        CREATE INDEX IF NOT EXISTS {self.table_name}_metadata_idx 
                        ON {self.table_name} USING gin (metadata);
                    """)
                    
                conn.commit()
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization failed: {e}")
            raise
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text using a placeholder method.
        
        In production, replace with actual embedding model like:
        - sentence-transformers
        - OpenAI embeddings
        - Hugging Face transformers
        """
        # Placeholder: simple hash-based embedding for testing
        # Replace with actual embedding model in production
        import hashlib
        
        # Create deterministic embedding from text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        embedding = np.array([
            int(text_hash[i:i+2], 16) / 255.0 
            for i in range(0, min(len(text_hash), self.embedding_dim * 2), 2)
        ])
        
        # Pad or truncate to correct dimension
        if len(embedding) < self.embedding_dim:
            embedding = np.pad(embedding, (0, self.embedding_dim - len(embedding)))
        else:
            embedding = embedding[:self.embedding_dim]
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
            
        return embedding
    
    def add_document(self, content: str, metadata: Optional[Dict[str, Any]] = None,
                    doc_id: Optional[str] = None) -> str:
        """
        Add a document to the vector database
        
        Args:
            content: Document text content
            metadata: Optional metadata dictionary
            doc_id: Optional document ID (auto-generated if not provided)
            
        Returns:
            Document ID
        """
        if doc_id is None:
            doc_id = f"doc_{datetime.now().timestamp()}"
        
        if metadata is None:
            metadata = {}
        
        # Add timestamp to metadata
        metadata["created_at"] = datetime.now().isoformat()
        metadata["content_length"] = len(content)
        
        # Generate embedding
        embedding = self._generate_embedding(content)
        
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        INSERT INTO {self.table_name} (doc_id, content, metadata, embedding)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (doc_id) DO UPDATE SET
                            content = EXCLUDED.content,
                            metadata = EXCLUDED.metadata,
                            embedding = EXCLUDED.embedding,
                            updated_at = CURRENT_TIMESTAMP;
                    """, (doc_id, content, json.dumps(metadata), embedding.tolist()))
                
                conn.commit()
            
            logger.info(f"Added document {doc_id}")
            return doc_id
            
        except Exception as e:
            logger.error(f"Failed to add document: {e}")
            raise
    
    def retrieve(self, query: str, top_k: int = 5, 
                metadata_filter: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Retrieve most similar documents to query
        
        Args:
            query: Search query
            top_k: Number of documents to return
            metadata_filter: Optional metadata filter
            
        Returns:
            List of documents with similarity scores
        """
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    # Build query with optional metadata filtering
                    where_clause = ""
                    params = [query_embedding.tolist(), top_k]
                    
                    if metadata_filter:
                        where_conditions = []
                        for key, value in metadata_filter.items():
                            where_conditions.append(f"metadata ->> %s = %s")
                            params.extend([key, str(value)])
                        
                        if where_conditions:
                            where_clause = "WHERE " + " AND ".join(where_conditions)
                    
                    cur.execute(f"""
                        SELECT 
                            doc_id,
                            content,
                            metadata,
                            created_at,
                            1 - (embedding <=> %s::vector) as similarity_score
                        FROM {self.table_name}
                        {where_clause}
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """, params)
                    
                    results = cur.fetchall()
                    
                    # Convert to list of dictionaries
                    documents = []
                    for row in results:
                        doc = dict(row)
                        doc["metadata"] = json.loads(doc["metadata"]) if doc["metadata"] else {}
                        documents.append(doc)
                    
                    return documents
                    
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {e}")
            return []
    
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the database
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"DELETE FROM {self.table_name} WHERE doc_id = %s;", (doc_id,))
                    deleted = cur.rowcount > 0
                
                conn.commit()
                
            if deleted:
                logger.info(f"Deleted document {doc_id}")
            
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete document {doc_id}: {e}")
            return False
    
    def query(self, query: str, top_k: int = 3, 
             metadata_filter: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Complete RAG query: retrieve and generate response
        
        Args:
            query: User query
            top_k: Number of documents to retrieve
            metadata_filter: Optional metadata filter
            
        Returns:
            Response with context and metadata
        """
        # Retrieve relevant documents
        context_docs = self.retrieve(query, top_k, metadata_filter)
        
        # Generate response (placeholder)
        if not context_docs:
            response = "I don't have enough information to answer that question."
        else:
            context = "\n\n".join([doc["content"] for doc in context_docs[:2]])
            response = f"""Based on the available information:

{context}

This information is relevant to your query: "{query}"

Note: This response is generated from retrieved documents. For specific financial advice, please consult with a qualified financial advisor."""
        
        return {
            "query": query,
            "response": response,
            "context_documents": context_docs,
            "num_documents_found": len(context_docs),
            "timestamp": datetime.now().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            with psycopg2.connect(self.connection_string) as conn:
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {self.table_name};")
                    doc_count = cur.fetchone()[0]
                    
                    cur.execute(f"""
                        SELECT 
                            AVG(LENGTH(content)) as avg_content_length,
                            MIN(created_at) as oldest_doc,
                            MAX(created_at) as newest_doc
                        FROM {self.table_name};
                    """)
                    stats = cur.fetchone()
                    
                    return {
                        "num_documents": doc_count,
                        "avg_content_length": float(stats[0]) if stats[0] else 0,
                        "oldest_document": stats[1].isoformat() if stats[1] else None,
                        "newest_document": stats[2].isoformat() if stats[2] else None,
                        "embedding_dimension": self.embedding_dim
                    }
                    
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}


def test_pgvector_rag() -> None:
    """Test PGVectorRAG implementation (requires running PostgreSQL with pgvector)"""
    print("Testing PGVectorRAG implementation...")
    
    try:
        # Initialize RAG
        rag = PGVectorRAG()
        
        # Add sample document
        doc_id = rag.add_document(
            content="Portfolio optimization involves balancing risk and return through diversification.",
            metadata={"type": "education", "topic": "optimization"}
        )
        
        # Test query
        result = rag.query("How to optimize a portfolio?")
        print(f"Query result: {result}")
        
        # Get stats
        stats = rag.get_stats()
        print(f"Database stats: {stats}")
        
        print("PGVectorRAG test completed!")
        
    except Exception as e:
        print(f"PGVectorRAG test failed (this is expected if PostgreSQL/pgvector not available): {e}")


if __name__ == "__main__":
    test_pgvector_rag()