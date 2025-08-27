-- PostgreSQL schema with pgvector extension for RAG system
-- This script sets up the database schema for storing document embeddings
-- and performing efficient similarity search

-- Enable the pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema for RAG system
CREATE SCHEMA IF NOT EXISTS rag;

-- Documents table for storing text content and embeddings
CREATE TABLE IF NOT EXISTS rag.financial_documents (
    id SERIAL PRIMARY KEY,
    doc_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(500),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    embedding vector(384),  -- Adjust dimension based on your embedding model
    content_hash VARCHAR(64), -- For deduplication
    source VARCHAR(100),
    document_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT financial_documents_content_not_empty CHECK (LENGTH(content) > 0),
    CONSTRAINT financial_documents_embedding_not_null CHECK (embedding IS NOT NULL)
);

-- Create indexes for efficient querying
-- Index for similarity search using ivfflat
CREATE INDEX IF NOT EXISTS financial_documents_embedding_idx 
ON rag.financial_documents 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Alternative index using hnsw (if available in your pgvector version)
-- CREATE INDEX IF NOT EXISTS financial_documents_embedding_hnsw_idx 
-- ON rag.financial_documents 
-- USING hnsw (embedding vector_cosine_ops)
-- WITH (m = 16, ef_construction = 64);

-- Index on metadata for filtering
CREATE INDEX IF NOT EXISTS financial_documents_metadata_idx 
ON rag.financial_documents 
USING gin (metadata);

-- Index on document type for filtering
CREATE INDEX IF NOT EXISTS financial_documents_type_idx 
ON rag.financial_documents (document_type);

-- Index on source for filtering
CREATE INDEX IF NOT EXISTS financial_documents_source_idx 
ON rag.financial_documents (source);

-- Index on created_at for time-based queries
CREATE INDEX IF NOT EXISTS financial_documents_created_at_idx 
ON rag.financial_documents (created_at);

-- Index for content deduplication
CREATE INDEX IF NOT EXISTS financial_documents_content_hash_idx 
ON rag.financial_documents (content_hash);

-- Document chunks table for splitting large documents
CREATE TABLE IF NOT EXISTS rag.document_chunks (
    id SERIAL PRIMARY KEY,
    document_id INTEGER REFERENCES rag.financial_documents(id) ON DELETE CASCADE,
    chunk_id VARCHAR(255) NOT NULL,
    chunk_content TEXT NOT NULL,
    chunk_metadata JSONB DEFAULT '{}',
    embedding vector(384),
    chunk_order INTEGER DEFAULT 0,
    chunk_overlap INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(document_id, chunk_order),
    CONSTRAINT document_chunks_content_not_empty CHECK (LENGTH(chunk_content) > 0)
);

-- Index for chunk similarity search
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx 
ON rag.document_chunks 
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index for finding chunks by document
CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx 
ON rag.document_chunks (document_id, chunk_order);

-- Query logs table for tracking usage and performance
CREATE TABLE IF NOT EXISTS rag.query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    query_embedding vector(384),
    num_results INTEGER,
    response_time_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index for query analysis
CREATE INDEX IF NOT EXISTS query_logs_created_at_idx 
ON rag.query_logs (created_at);

-- User feedback table for improving results
CREATE TABLE IF NOT EXISTS rag.query_feedback (
    id SERIAL PRIMARY KEY,
    query_log_id INTEGER REFERENCES rag.query_logs(id) ON DELETE CASCADE,
    document_id INTEGER REFERENCES rag.financial_documents(id) ON DELETE CASCADE,
    relevance_score INTEGER CHECK (relevance_score BETWEEN 1 AND 5),
    feedback_text TEXT,
    user_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Document collections for organizing content
CREATE TABLE IF NOT EXISTS rag.document_collections (
    id SERIAL PRIMARY KEY,
    collection_name VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Many-to-many relationship between documents and collections
CREATE TABLE IF NOT EXISTS rag.document_collection_mapping (
    document_id INTEGER REFERENCES rag.financial_documents(id) ON DELETE CASCADE,
    collection_id INTEGER REFERENCES rag.document_collections(id) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (document_id, collection_id)
);

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION rag.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_financial_documents_updated_at 
    BEFORE UPDATE ON rag.financial_documents 
    FOR EACH ROW EXECUTE FUNCTION rag.update_updated_at_column();

-- Function for similarity search with optional filtering
CREATE OR REPLACE FUNCTION rag.search_similar_documents(
    query_embedding vector(384),
    similarity_threshold float DEFAULT 0.1,
    max_results integer DEFAULT 10,
    doc_type_filter varchar DEFAULT NULL,
    source_filter varchar DEFAULT NULL,
    metadata_filter jsonb DEFAULT NULL
)
RETURNS TABLE (
    doc_id varchar,
    title varchar,
    content text,
    metadata jsonb,
    similarity_score float,
    source varchar,
    document_type varchar,
    created_at timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        fd.doc_id,
        fd.title,
        fd.content,
        fd.metadata,
        1 - (fd.embedding <=> query_embedding) as similarity_score,
        fd.source,
        fd.document_type,
        fd.created_at
    FROM rag.financial_documents fd
    WHERE 
        (doc_type_filter IS NULL OR fd.document_type = doc_type_filter)
        AND (source_filter IS NULL OR fd.source = source_filter)
        AND (metadata_filter IS NULL OR fd.metadata @> metadata_filter)
        AND (1 - (fd.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY fd.embedding <=> query_embedding
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function to get document statistics
CREATE OR REPLACE FUNCTION rag.get_document_stats()
RETURNS TABLE (
    total_documents bigint,
    total_chunks bigint,
    avg_content_length numeric,
    unique_sources bigint,
    unique_types bigint,
    oldest_document timestamp,
    newest_document timestamp
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_documents,
        (SELECT COUNT(*) FROM rag.document_chunks) as total_chunks,
        AVG(LENGTH(content)) as avg_content_length,
        COUNT(DISTINCT source) as unique_sources,
        COUNT(DISTINCT document_type) as unique_types,
        MIN(created_at) as oldest_document,
        MAX(created_at) as newest_document
    FROM rag.financial_documents;
END;
$$ LANGUAGE plpgsql;

-- Insert sample document collections
INSERT INTO rag.document_collections (collection_name, description, metadata) 
VALUES 
    ('risk_management', 'Documents related to portfolio risk management', '{"category": "risk"}'),
    ('optimization_theory', 'Modern portfolio theory and optimization', '{"category": "theory"}'),
    ('factor_investing', 'Factor models and smart beta strategies', '{"category": "factors"}'),
    ('esg_integration', 'ESG and sustainable investing materials', '{"category": "esg"}'),
    ('market_analysis', 'Market research and analysis reports', '{"category": "research"}')
ON CONFLICT (collection_name) DO NOTHING;

-- Grant permissions (adjust schema and user as needed)
-- GRANT USAGE ON SCHEMA rag TO rag_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA rag TO rag_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA rag TO rag_user;

-- Create view for easy document search
CREATE OR REPLACE VIEW rag.document_search_view AS
SELECT 
    fd.id,
    fd.doc_id,
    fd.title,
    fd.content,
    fd.metadata,
    fd.source,
    fd.document_type,
    fd.created_at,
    fd.updated_at,
    string_agg(dc.collection_name, ', ') as collections
FROM rag.financial_documents fd
LEFT JOIN rag.document_collection_mapping dcm ON fd.id = dcm.document_id
LEFT JOIN rag.document_collections dc ON dcm.collection_id = dc.id
GROUP BY fd.id, fd.doc_id, fd.title, fd.content, fd.metadata, fd.source, fd.document_type, fd.created_at, fd.updated_at;

-- Example usage:
-- 
-- 1. Insert a document:
-- INSERT INTO rag.financial_documents (doc_id, title, content, metadata, embedding, source, document_type)
-- VALUES ('doc_001', 'Portfolio Theory', 'Modern Portfolio Theory content...', 
--         '{"author": "Markowitz", "year": 1952}', '[0.1, 0.2, ...]', 'research', 'theory');
--
-- 2. Search for similar documents:
-- SELECT * FROM rag.search_similar_documents('[0.1, 0.2, ...]'::vector, 0.7, 5);
--
-- 3. Get statistics:
-- SELECT * FROM rag.get_document_stats();