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
