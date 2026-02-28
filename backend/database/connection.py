"""PostgreSQL database connection management."""
import os
from typing import AsyncGenerator

import asyncpg
from asyncpg import Pool


class Database:
    """Async PostgreSQL database connection pool."""
    
    def __init__(self):
        self.pool: Pool | None = None
    
    async def connect(self):
        """Initialize connection pool."""
        database_url = os.getenv(
            "DATABASE_URL",
            "postgresql://user:password@localhost:5432/smartbrain"
        )
        
        self.pool = await asyncpg.create_pool(
            database_url,
            min_size=2,
            max_size=10,
            command_timeout=60
        )
        print("✓ Connected to PostgreSQL")
    
    async def disconnect(self):
        """Close connection pool."""
        if self.pool:
            await self.pool.close()
            print("✓ Disconnected from PostgreSQL")
    
    async def get_connection(self) -> AsyncGenerator:
        """Get a connection from the pool."""
        if not self.pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self.pool.acquire() as connection:
            yield connection


# Global database instance
db = Database()


async def get_db_connection():
    """Dependency for FastAPI endpoints."""
    async for connection in db.get_connection():
        yield connection
