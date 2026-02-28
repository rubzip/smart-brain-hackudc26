from enum import Enum
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
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


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/items/urls", response_model=StoredItemResponse, status_code=201)
async def create_item_from_url(payload: URLItemCreate) -> StoredItemResponse:
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/v1/items/local-files", response_model=StoredItemResponse, status_code=201)
async def create_item_from_local_file(payload: LocalItemCreate) -> StoredItemResponse:
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/v1/items/files", response_model=StoredItemResponse, status_code=201)
async def create_item_from_uploaded_file(file: UploadFile = File(...)) -> StoredItemResponse:
    _ = file
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.get("/api/v1/items")
async def list_items(
    view: FocusView = Query(default=FocusView.ALL),
    q: str | None = Query(default=None, description="Filtro textual opcional"),
) -> dict[str, object]:
    _ = q
    return {
        "view": view,
        "items": [],
        "note": "Endpoint creado; lógica de negocio pendiente.",
    }


@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: str) -> dict[str, str]:
    _ = item_id
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.delete("/api/v1/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    _ = item_id
    raise HTTPException(status_code=501, detail="Not implemented yet")


@app.post("/api/v1/chats/{chat_id}/messages", response_model=ChatMessageResponse, status_code=202)
async def create_chat_message(chat_id: str, payload: ChatMessageCreate) -> ChatMessageResponse:
    _ = (chat_id, payload)
    raise HTTPException(status_code=501, detail="Not implemented yet")