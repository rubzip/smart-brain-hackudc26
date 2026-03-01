#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Data Access Object for Items - handles all database operations for items.

Copyright (C) 2026 Smart Brain Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from uuid import UUID
from typing import Optional
from datetime import datetime

import asyncpg


class ItemDAO:
    """DAO for items table."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, item_data: dict) -> UUID:
        """Insert new item and return ID."""
        async with self.pool.acquire() as conn:
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
    
    async def get_by_id(self, item_id: UUID) -> Optional[dict]:
        """Get item by ID."""
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM items WHERE id = $1"
            row = await conn.fetchrow(query, item_id)
            return dict(row) if row else None
    
    async def list_all(self, limit: int = 100, offset: int = 0) -> list[dict]:
        """List all items with pagination."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, source_type, title, status, created_at
                FROM items
                ORDER BY created_at DESC
                LIMIT $1 OFFSET $2
            """
            rows = await conn.fetch(query, limit, offset)
            return [dict(row) for row in rows]
    
    async def list_by_search(self, search_term: str, limit: int = 100) -> list[dict]:
        """Search items by title or extracted_text."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, source_type, title, status, created_at
                FROM items
                WHERE LOWER(title) LIKE LOWER($1) OR LOWER(extracted_text) LIKE LOWER($1)
                ORDER BY created_at DESC
                LIMIT $2
            """
            search_pattern = f"%{search_term}%"
            rows = await conn.fetch(query, search_pattern, limit)
            return [dict(row) for row in rows]
    
    async def list_by_tags(self, query: str, tags: list[str], limit: int = 5) -> list[dict]:
        pass
    
    async def delete(self, item_id: UUID) -> bool:
        """Delete item and cascade to embeddings."""
        async with self.pool.acquire() as conn:
            query = "DELETE FROM items WHERE id = $1"
            result = await conn.execute(query, item_id)
            # Result format: "DELETE 1" or "DELETE 0"
            return "1" in result
    
    async def count(self) -> int:
        """Get total count of items."""
        async with self.pool.acquire() as conn:
            query = "SELECT COUNT(*) as count FROM items"
            row = await conn.fetchrow(query)
            return row["count"]
    
    async def get_all_for_cache(self) -> dict:
        """Get all items as a dict for compatibility with old STORAGE."""
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM items"
            rows = await conn.fetch(query)
            result = {}
            for row in rows:
                item_dict = dict(row)
                result[str(row["id"])] = item_dict
            return result
