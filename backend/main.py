import io
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

from utils.loader import (
    get_docx_from_stream,
    get_excel_from_stream,
    get_odt_from_stream,
    get_pdf_from_stream,
    get_webpage_text,
)


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


app = FastAPI(
    title="Smart Brain API",
    version="0.1.0",
    description="API REST placeholder para items almacenados y chat RAG.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage in-memory (sustituir por DB en producción)
STORAGE: dict[str, dict] = {}


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/items/urls", response_model=StoredItemResponse, status_code=201)
async def create_item_from_url(payload: URLItemCreate) -> StoredItemResponse:
    item_id = str(uuid.uuid4())
    try:
        extracted_text = get_webpage_text(str(payload.url))
        item_data = {
            "id": item_id,
            "source_type": "url",
            "title": payload.title or str(payload.url),
            "url": str(payload.url),
            "tags": payload.tags,
            "extracted_text": extracted_text,
            "status": "ready",
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="url",
            title=item_data["title"],
            status="ready",
            extracted_text=extracted_text[:500],  # Preview
            summary=item_data.get("summary"),
            youtube_url=item_data.get("url") if "youtube.com" in str(payload.url) or "youtu.be" in str(payload.url) else None,
        )
    except Exception as e:
        item_data = {
            "id": item_id,
            "source_type": "url",
            "title": payload.title or str(payload.url),
            "url": str(payload.url),
            "tags": payload.tags,
            "status": "failed",
            "error_message": str(e),
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="url",
            title=item_data["title"],
            status="failed",
            error_message=str(e),
        )


@app.post("/api/v1/items/local-files", response_model=StoredItemResponse, status_code=201)
async def create_item_from_local_file(payload: LocalItemCreate) -> StoredItemResponse:
    item_id = str(uuid.uuid4())
    file_path = Path(payload.file_path)
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, "rb") as f:
            stream = io.BytesIO(f.read())
        
        suffix = file_path.suffix.lower()
        if suffix == ".pdf":
            extracted_text = get_pdf_from_stream(stream)
        elif suffix in [".docx"]:
            extracted_text = get_docx_from_stream(stream)
        elif suffix in [".odt"]:
            extracted_text = get_odt_from_stream(stream)
        elif suffix in [".xlsx", ".xls"]:
            extracted_text = get_excel_from_stream(stream)
        elif suffix in [".txt", ".csv"]:
            extracted_text = stream.read().decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        item_data = {
            "id": item_id,
            "source_type": "local_file",
            "title": payload.title or file_path.name,
            "file_path": str(file_path),
            "tags": payload.tags,
            "extracted_text": extracted_text,
            "status": "ready",
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="local_file",
            title=item_data["title"],
            status="ready",
            extracted_text=extracted_text[:500],
        )
    except Exception as e:
        item_data = {
            "id": item_id,
            "source_type": "local_file",
            "title": payload.title or file_path.name,
            "file_path": str(file_path),
            "tags": payload.tags,
            "status": "failed",
            "error_message": str(e),
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="local_file",
            title=item_data["title"],
            status="failed",
            error_message=str(e),
        )


@app.post("/api/v1/items/files", response_model=StoredItemResponse, status_code=201)
async def create_item_from_uploaded_file(file: UploadFile = File(...)) -> StoredItemResponse:
    item_id = str(uuid.uuid4())
    
    try:
        content = await file.read()
        stream = io.BytesIO(content)
        
        filename = file.filename or "unknown"
        suffix = Path(filename).suffix.lower()
        
        if suffix == ".pdf":
            extracted_text = get_pdf_from_stream(stream)
        elif suffix in [".docx"]:
            extracted_text = get_docx_from_stream(stream)
        elif suffix in [".odt"]:
            extracted_text = get_odt_from_stream(stream)
        elif suffix in [".xlsx", ".xls"]:
            extracted_text = get_excel_from_stream(stream)
        elif suffix in [".txt", ".csv"]:
            extracted_text = content.decode("utf-8")
        else:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        item_data = {
            "id": item_id,
            "source_type": "uploaded_file",
            "title": filename,
            "filename": filename,
            "extracted_text": extracted_text,
            "status": "ready",
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="uploaded_file",
            title=filename,
            status="ready",
            extracted_text=extracted_text[:500],
        )
    except Exception as e:
        item_data = {
            "id": item_id,
            "source_type": "uploaded_file",
            "title": filename,
            "status": "failed",
            "error_message": str(e),
            "created_at": datetime.utcnow().isoformat(),
        }
        STORAGE[item_id] = item_data
        return StoredItemResponse(
            id=item_id,
            source_type="uploaded_file",
            title=filename,
            status="failed",
            error_message=str(e),
        )


@app.get("/api/v1/items")
async def list_items(
    view: FocusView = Query(default=FocusView.ALL),
    q: str | None = Query(default=None, description="Filtro textual opcional"),
) -> dict[str, object]:
    items = list(STORAGE.values())
    
    if q:
        q_lower = q.lower()
        items = [
            item for item in items
            if q_lower in item.get("title", "").lower()
            or q_lower in item.get("extracted_text", "").lower()
        ]
    
    # Simplificar respuesta (sin texto completo)
    items_summary = [
        {
            "id": item["id"],
            "title": item.get("title"),
            "source_type": item["source_type"],
            "status": item["status"],
            "created_at": item.get("created_at"),
        }
        for item in items
    ]
    
    return {
        "view": view,
        "total": len(items_summary),
        "items": items_summary,
    }


@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: str) -> dict:
    if item_id not in STORAGE:
        raise HTTPException(status_code=404, detail="Item not found")
    return STORAGE[item_id]


@app.delete("/api/v1/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    if item_id not in STORAGE:
        raise HTTPException(status_code=404, detail="Item not found")
    del STORAGE[item_id]


@app.post("/api/v1/chats/{chat_id}/messages", response_model=ChatMessageResponse, status_code=202)
async def create_chat_message(chat_id: str, payload: ChatMessageCreate) -> ChatMessageResponse:
    _ = (chat_id, payload)
    raise HTTPException(status_code=501, detail="Not implemented yet")