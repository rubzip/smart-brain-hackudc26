"""Database models and query helpers."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ItemDB(BaseModel):
    """Database model for items table."""
    id: UUID
    source_type: str
    title: Optional[str] = None
    url: Optional[str] = None
    file_path: Optional[str] = None
    filename: Optional[str] = None
    tags: list[str] = []
    extracted_text: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None


class EmbeddingDB(BaseModel):
    """Database model for embeddings table."""
    id: UUID
    item_id: UUID
    chunk_index: int
    chunk_text: str
    embedding: list[float]  # Vector representation


class TaskDB(BaseModel):
    """Database model for tasks table."""
    id: UUID
    text: str
    completed: bool = False
    generated_from_item: Optional[UUID] = None
    generated_from_items: list[UUID] = []


class ChatMessageDB(BaseModel):
    """Database model for chat messages table."""
    id: UUID
    chat_id: UUID
    role: str  # 'user', 'assistant', 'system'
    content: str
    retrieval_scope: list[UUID] = []


# Query helpers
class ItemQueries:
    """SQL queries for items table."""
    
    @staticmethod
    async def create_item(conn, item_data: dict) -> UUID:
        """Insert new item and return ID."""
        query = """
            INSERT INTO items (source_type, title, url, file_path, filename, tags, extracted_text, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id
        """
        row = await conn.fetchrow(
            query,
            item_data.get("source_type"),
            item_data.get("title"),
            item_data.get("url"),
            item_data.get("file_path"),
            item_data.get("filename"),
            item_data.get("tags", []),
            item_data.get("extracted_text"),
            item_data.get("status", "ready")
        )
        return row["id"]
    
    @staticmethod
    async def get_item(conn, item_id: UUID) -> Optional[dict]:
        """Get item by ID."""
        query = "SELECT * FROM items WHERE id = $1"
        row = await conn.fetchrow(query, item_id)
        return dict(row) if row else None
    
    @staticmethod
    async def list_items(conn, limit: int = 100, offset: int = 0) -> list[dict]:
        """List all items with pagination."""
        query = """
            SELECT id, source_type, title, status, created_at
            FROM items
            ORDER BY created_at DESC
            LIMIT $1 OFFSET $2
        """
        rows = await conn.fetch(query, limit, offset)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def delete_item(conn, item_id: UUID) -> bool:
        """Delete item and cascade to embeddings."""
        query = "DELETE FROM items WHERE id = $1"
        result = await conn.execute(query, item_id)
        return result.split()[-1] == "1"  # Returns "DELETE 1"


class EmbeddingQueries:
    """SQL queries for embeddings table."""
    
    @staticmethod
    async def insert_embeddings(conn, item_id: UUID, chunks: list[dict]):
        """Insert multiple embeddings for an item."""
        query = """
            INSERT INTO embeddings (item_id, chunk_index, chunk_text, embedding)
            VALUES ($1, $2, $3, $4::vector)
        """
        await conn.executemany(
            query,
            [(item_id, chunk["index"], chunk["text"], chunk["embedding"]) for chunk in chunks]
        )
    
    @staticmethod
    async def search_similar(conn, query_embedding: list[float], limit: int = 5) -> list[dict]:
        """Vector similarity search using cosine distance."""
        query = """
            SELECT 
                e.item_id,
                e.chunk_text,
                i.title,
                1 - (e.embedding <=> $1::vector) as similarity
            FROM embeddings e
            JOIN items i ON e.item_id = i.id
            ORDER BY e.embedding <=> $1::vector
            LIMIT $2
        """
        rows = await conn.fetch(query, query_embedding, limit)
        return [dict(row) for row in rows]


class TaskQueries:
    """SQL queries for tasks table."""
    
    @staticmethod
    async def create_task(conn, task_data: dict) -> UUID:
        """Create new task."""
        query = """
            INSERT INTO tasks (text, completed, generated_from_item, generated_from_items)
            VALUES ($1, $2, $3, $4)
            RETURNING id
        """
        row = await conn.fetchrow(
            query,
            task_data["text"],
            task_data.get("completed", False),
            task_data.get("generated_from_item"),
            task_data.get("generated_from_items", [])
        )
        return row["id"]
    
    @staticmethod
    async def get_active_tasks(conn) -> list[dict]:
        """Get all non-completed tasks."""
        query = """
            SELECT id, text, completed, generated_from_item, created_at
            FROM tasks
            WHERE completed = FALSE
            ORDER BY created_at DESC
        """
        rows = await conn.fetch(query)
        return [dict(row) for row in rows]
    
    @staticmethod
    async def complete_task(conn, task_id: UUID) -> bool:
        """Mark task as completed."""
        query = "UPDATE tasks SET completed = TRUE WHERE id = $1"
        result = await conn.execute(query, task_id)
        return result.split()[-1] == "1"
