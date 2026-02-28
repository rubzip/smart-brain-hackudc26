-- Smart Brain Database Schema
-- PostgreSQL with pgvector extension for RAG

-- Enable pgvector extension for vector similarity search
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Items table: stores all knowledge base entries
CREATE TABLE IF NOT EXISTS items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    source_type VARCHAR(50) NOT NULL CHECK (source_type IN ('url', 'local_file', 'uploaded_file')),
    title VARCHAR(500),
    url TEXT,
    file_path TEXT,
    filename VARCHAR(255),
    tags TEXT[], -- Array of tags
    extracted_text TEXT,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'ready', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Embeddings table: stores vector embeddings for RAG
CREATE TABLE IF NOT EXISTS embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id UUID NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL, -- Order of chunk within the document
    chunk_text TEXT NOT NULL,
    embedding vector(384), -- Dimension depends on embedding model (384 for all-MiniLM-L6-v2)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(item_id, chunk_index)
);

-- Tasks table: stores persistent daily tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    text TEXT NOT NULL,
    completed BOOLEAN DEFAULT FALSE,
    generated_from_item UUID REFERENCES items(id) ON DELETE SET NULL, -- Single item that inspired this task
    generated_from_items UUID[] DEFAULT '{}', -- All items present when task was generated
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_items_source_type ON items(source_type);
CREATE INDEX IF NOT EXISTS idx_items_status ON items(status);
CREATE INDEX IF NOT EXISTS idx_items_created_at ON items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_items_tags ON items USING GIN(tags);

-- Vector similarity search index (HNSW for fast approximate nearest neighbor)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON embeddings USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_embeddings_item_id ON embeddings(item_id);

CREATE INDEX IF NOT EXISTS idx_tasks_completed ON tasks(completed);
CREATE INDEX IF NOT EXISTS idx_tasks_created_at ON tasks(created_at DESC);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply trigger to items table
CREATE TRIGGER update_items_updated_at BEFORE UPDATE ON items
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Completed_at trigger for tasks
CREATE OR REPLACE FUNCTION update_task_completed_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.completed = TRUE AND OLD.completed = FALSE THEN
        NEW.completed_at = CURRENT_TIMESTAMP;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER set_task_completed_at BEFORE UPDATE ON tasks
FOR EACH ROW EXECUTE FUNCTION update_task_completed_at();

-- Comments for documentation
COMMENT ON TABLE items IS 'Stores all knowledge base items (URLs, files, documents)';
COMMENT ON TABLE embeddings IS 'Vector embeddings for semantic search and RAG';
COMMENT ON TABLE tasks IS 'Persistent daily tasks generated from items';

COMMENT ON COLUMN embeddings.embedding IS 'Vector embedding (384d for all-MiniLM-L6-v2, adjust based on model)';
COMMENT ON COLUMN tasks.generated_from_items IS 'Snapshot of all item IDs present when task was generated';
