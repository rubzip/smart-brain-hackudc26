import asyncio
import io
import json
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

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


class DailyTask(BaseModel):
    id: str
    text: str
    completed: bool = False


class DailyPlanResponse(BaseModel):
    tasks: list[DailyTask]
    generated_at: str
    message: str


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

# Caching system for daily plan
DAILY_PLAN_CACHE: DailyPlanResponse | None = None
DAILY_PLAN_LOCK = asyncio.Lock()
DAILY_PLAN_REGENERATING = False


async def _regenerate_daily_plan_background() -> None:
    """Regenera el plan diario en background cuando hay cambios."""
    global DAILY_PLAN_CACHE, DAILY_PLAN_REGENERATING
    
    async with DAILY_PLAN_LOCK:
        DAILY_PLAN_REGENERATING = True
        try:
            if not OLLAMA_AVAILABLE:
                DAILY_PLAN_REGENERATING = False
                return
            
            DAILY_PLAN_CACHE = await _build_daily_plan()
        except Exception as e:
            print(f"Error regenerating daily plan: {e}")
        finally:
            DAILY_PLAN_REGENERATING = False


async def _build_daily_plan() -> DailyPlanResponse:
    """Construye un DailyPlanResponse basado en los items almacenados."""
    prompt = _generate_daily_plan_prompt()
    
    if not prompt:
        return DailyPlanResponse(
            tasks=[],
            generated_at=datetime.utcnow().isoformat(),
            message="No stored items found to generate a plan."
        )
    
    tasks = await _call_ollama_for_plan(prompt)
    
    if tasks is None:
        tasks = [
            DailyTask(id="1", text="📖 Review your stored resources", completed=False),
            DailyTask(id="2", text="💻 Work on a project task", completed=False),
            DailyTask(id="3", text="🏋️ Exercise", completed=False),
            DailyTask(id="4", text="📝 Reflect on learnings", completed=False),
        ]
        message = "LLM response could not be parsed. Using fallback tasks."
    else:
        message = "Daily plan generated successfully from your stored items."
    
    return DailyPlanResponse(
        tasks=tasks,
        generated_at=datetime.utcnow().isoformat(),
        message=message
    )


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
        asyncio.create_task(_regenerate_daily_plan_background())
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
        asyncio.create_task(_regenerate_daily_plan_background())
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
        asyncio.create_task(_regenerate_daily_plan_background())
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
        asyncio.create_task(_regenerate_daily_plan_background())
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
        asyncio.create_task(_regenerate_daily_plan_background())
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
        asyncio.create_task(_regenerate_daily_plan_background())
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
    asyncio.create_task(_regenerate_daily_plan_background())


@app.get("/api/v1/daily-plan", response_model=DailyPlanResponse)
async def generate_daily_plan() -> DailyPlanResponse:
    """Retorna el plan diario cacheado, esperando si está regenerando."""
    global DAILY_PLAN_CACHE
    
    if not OLLAMA_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Ollama is not available. Install the 'ollama' Python package and ensure ollama service is running."
        )
    
    # Esperar a que termine la regeneración si está ocurriendo
    async with DAILY_PLAN_LOCK:
        if DAILY_PLAN_CACHE is not None:
            return DAILY_PLAN_CACHE
        
        # Si no hay caché, generar ahora
        DAILY_PLAN_CACHE = await _build_daily_plan()
        return DAILY_PLAN_CACHE


def _generate_daily_plan_prompt() -> str:
    """Sintetiza un prompt con todos los elementos almacenados."""
    items_summary = []
    
    for item_id, item_data in STORAGE.items():
        source_type = item_data.get("source_type", "unknown")
        title = item_data.get("title", "Untitled")
        tags = item_data.get("tags", [])
        text_preview = item_data.get("extracted_text", "")[:300]
        
        item_summary = f"- [{source_type}] {title}"
        if tags:
            item_summary += f" (Tags: {', '.join(tags)})"
        if text_preview:
            item_summary += f"\n  Preview: {text_preview}..."
        
        items_summary.append(item_summary)
    
    if not items_summary:
        return ""
    
    prompt = (
        "You are a task planner. Based on the following stored items in a personal knowledge base, "
        "generate ONLY a JSON array with 4-6 daily goals/tasks.\n\n"
        "STORED ITEMS:\n"
        + "\n".join(items_summary)
        + "\n\n"
        "Return ONLY valid JSON (no code, no markdown, no extra text):\n"
        '[\n'
        '  {"id": "1", "text": "📖 Read X from resource Y", "completed": false},\n'
        '  {"id": "2", "text": "💻 Work on Z project", "completed": false}\n'
        ']\n\n'
        "Requirements:\n"
        "- Include an emoji at the start of each task\n"
        "- Make tasks specific and actionable\n"
        "- Keep each task under 60 characters\n"
        "- Return ONLY the JSON array, nothing else"
    )
    
    return prompt


async def _call_ollama_for_plan(prompt: str) -> list[DailyTask] | None:
    """Llama a ollama para generar el plan diario."""
    if not OLLAMA_AVAILABLE:
        return None
    
    try:
        response = ollama.generate(
            model="phi",
            prompt=prompt,
            stream=False,
        )
        
        response_text = response.get("response", "").strip()
        
        # Intentar parsear JSON de la respuesta
        try:
            tasks_data = json.loads(response_text)
            if isinstance(tasks_data, list):
                return [
                    DailyTask(
                        id=str(task.get("id", str(uuid.uuid4()))),
                        text=task.get("text", ""),
                        completed=task.get("completed", False)
                    )
                    for task in tasks_data
                ]
        except json.JSONDecodeError:
            # Si falla el parsing, intentar extraer JSON del texto
            import re
            # Buscar JSON array entre [ y ] (incluyendo anidados)
            json_match = re.search(r'\[(?:[^\[\]]|(?:\[.*?\]))*\]', response_text, re.DOTALL)
            if json_match:
                try:
                    tasks_data = json.loads(json_match.group())
                    return [
                        DailyTask(
                            id=str(task.get("id", str(uuid.uuid4()))),
                            text=task.get("text", ""),
                            completed=task.get("completed", False)
                        )
                        for task in tasks_data
                    ]
                except (json.JSONDecodeError, TypeError):
                    pass
        
        return None
    
    except Exception as e:
        print(f"Error calling ollama: {e}")
        return None