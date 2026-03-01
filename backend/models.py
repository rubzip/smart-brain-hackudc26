#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Smart Brain - Data models for the API
# Copyright (C) 2026 Smart Brain Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from datetime import datetime
from typing import Literal
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl


class FocusView(str, Enum):
    ALL = "all"
    TODAY = "today"


class URLItemCreate(BaseModel):
    url: HttpUrl
    title: str | None = Field(default=None, max_length=200)
    tags: list[str] = Field(default_factory=list)


class LocalItemCreate(BaseModel):
    file_path: str = Field(..., description="Ruta local del archivo")
    title: str | None = Field(default=None, max_length=200)
    tags: list[str] = Field(default_factory=list)


class StoredItemResponse(BaseModel):
    id: str
    source_type: Literal["url", "local_file", "uploaded_file"]
    title: str | None = None
    status: Literal["pending", "ready", "failed"] = "pending"
    extracted_text: str | None = None
    summary: str | None = None
    youtube_url: str | None = None
    error_message: str | None = None


class ChatMessageCreate(BaseModel):
    message: str = Field(..., min_length=1)
    retrieval_scope: list[str] = Field(
        default_factory=list,
        description="IDs opcionales de items para acotar recuperación",
    )
    delete_item_ids: list[str] = Field(
        default_factory=list,
        description="IDs de items que el usuario pide eliminar desde el chat",
    )


class ChatMessageResponse(BaseModel):
    chat_id: str
    message_id: str
    status: Literal["queued", "processing", "done"] = "queued"


class DailyTask(BaseModel):
    id: str
    text: str
    completed: bool = False
    generated_from: str | None = None  # ID del item desde el que se generó la tarea


class DailyPlanResponse(BaseModel):
    tasks: list[DailyTask]
    generated_at: str
    message: str


class SentimentCreate(BaseModel):
    sentiment: Literal["happy", "sad", "tired"]


class SentimentResponse(BaseModel):
    sentiment: Literal["happy", "sad", "tired"]
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class SearchRequest(BaseModel):
    query: str | None = None
    tags: list[str] = Field(default_factory=list)
