#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Smart Brain Contributors
#
# This file is part of Smart Brain.
# Smart Brain is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the LICENSE file at the project root for full terms.

"""Data Access Object for Tasks - handles all database operations for tasks."""
from uuid import UUID
from typing import Optional

import asyncpg


class TaskDAO:
    """DAO for tasks table."""
    
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool
    
    async def create(self, task_data: dict) -> UUID:
        """Create new task."""
        async with self.pool.acquire() as conn:
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
    
    async def get_by_id(self, task_id: UUID) -> Optional[dict]:
        """Get task by ID."""
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM tasks WHERE id = $1"
            row = await conn.fetchrow(query, task_id)
            return dict(row) if row else None
    
    async def get_active(self) -> list[dict]:
        """Get all non-completed tasks."""
        async with self.pool.acquire() as conn:
            query = """
                SELECT id, text, completed, generated_from_item, created_at
                FROM tasks
                WHERE completed = FALSE
                ORDER BY created_at DESC
            """
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    
    async def get_all(self) -> dict:
        """Get all tasks as dict for compatibility with PERSISTENT_TASKS."""
        async with self.pool.acquire() as conn:
            query = "SELECT * FROM tasks"
            rows = await conn.fetch(query)
            result = {}
            for row in rows:
                task_dict = dict(row)
                result[str(row["id"])] = task_dict
            return result
    
    async def update_completion(self, task_id: UUID, completed: bool) -> bool:
        """Mark task as completed or uncompleted."""
        async with self.pool.acquire() as conn:
            query = "UPDATE tasks SET completed = $1 WHERE id = $2"
            result = await conn.execute(query, completed, task_id)
            return "1" in result
    
    async def delete(self, task_id: UUID) -> bool:
        """Delete task."""
        async with self.pool.acquire() as conn:
            query = "DELETE FROM tasks WHERE id = $1"
            result = await conn.execute(query, task_id)
            return "1" in result
    
    async def delete_by_items(self, item_ids: list[UUID]) -> int:
        """Delete tasks that were generated from given items."""
        if not item_ids:
            return 0
        
        async with self.pool.acquire() as conn:
            # Delete tasks where generated_from_items contains any of the item_ids
            query = """
                DELETE FROM tasks 
                WHERE generated_from_items && $1::uuid[]
            """
            result = await conn.execute(query, item_ids)
            # Extract count from "DELETE N" response
            count = int(result.split()[-1])
            return count
    
    async def count_active(self) -> int:
        """Get count of non-completed tasks."""
        async with self.pool.acquire() as conn:
            query = "SELECT COUNT(*) as count FROM tasks WHERE completed = FALSE"
            row = await conn.fetchrow(query)
            return row["count"]
