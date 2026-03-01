"""Data Access Object for Embeddings - handles vector storage and retrieval."""
from uuid import UUID
from typing import Optional

import asyncpg


class EmbeddingDAO:
    """DAO for embeddings table."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, item_id: UUID, chunk_index: int, chunk_text: str, embedding: list[float]) -> UUID:
        """Insert new embedding chunk."""
        async with self.pool.acquire() as conn:
            query = """
                INSERT INTO embeddings (item_id, chunk_index, chunk_text, embedding)
                VALUES ($1, $2, $3, $4::vector)
                ON CONFLICT (item_id, chunk_index) 
                DO UPDATE SET chunk_text = $3, embedding = $4::vector
                RETURNING id
            """
            # Convert list to pgvector string format: '[1.0, 2.0, 3.0]'
            embedding_str = '[' + ','.join(map(str, embedding)) + ']'
            row = await conn.fetchrow(query, item_id, chunk_index, chunk_text, embedding_str)
            return row["id"]
    
    async def get_by_item(self, item_id: UUID) -> list[dict]:
        """Get all embedding chunks for an item."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, item_id, chunk_index, chunk_text, created_at
                FROM embeddings
                WHERE item_id = $1
                ORDER BY chunk_index
            """
            rows = await conn.fetch(query, item_id)
            return [dict(row) for row in rows]
    
    async def count_by_item(self, item_id: UUID) -> int:
        """Count embeddings for an item."""
        async with self.pool.acquire() as conn:
            query = "SELECT COUNT(*) as count FROM embeddings WHERE item_id = $1"
            row = await conn.fetchrow(query, item_id)
            return row["count"]
    
    async def delete_by_item(self, item_id: UUID) -> int:
        """Delete all embeddings for an item."""
        async with self.pool.acquire() as conn:
            query = "DELETE FROM embeddings WHERE item_id = $1"
            result = await conn.execute(query, item_id)
            return int(result.split()[-1]) if result else 0
    
    async def get_items_without_embeddings(self, limit: int = 10) -> list[dict]:
        """Get items that don't have any embeddings yet."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT i.id, i.title, i.extracted_text, i.source_type
                FROM items i
                LEFT JOIN embeddings e ON i.id = e.item_id
                WHERE e.id IS NULL 
                  AND i.status = 'ready'
                  AND i.extracted_text IS NOT NULL
                  AND i.extracted_text != ''
                ORDER BY i.created_at ASC
                LIMIT $1
            """
            rows = await conn.fetch(query, limit)
            return [dict(row) for row in rows]
    
    async def search_similar(self, query_embedding: list[float], limit: int = 5) -> list[dict]:
        """Search for similar embeddings using cosine similarity."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT 
                    e.id,
                    e.item_id,
                    e.chunk_text,
                    i.title,
                    i.source_type,
                    i.url,
                    1 - (e.embedding <=> $1::vector) as similarity
                FROM embeddings e
                JOIN items i ON e.item_id = i.id
                WHERE i.status = 'ready'
                ORDER BY e.embedding <=> $1::vector
                LIMIT $2
            """
            # Convert list to pgvector string format
            embedding_str = '[' + ','.join(map(str, query_embedding)) + ']'
            rows = await conn.fetch(query, embedding_str, limit)
            return [dict(row) for row in rows]
