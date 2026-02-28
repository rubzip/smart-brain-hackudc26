import asyncio
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from models import (
    DailyPlanResponse, DailyTask,
    SentimentCreate, SentimentResponse,
    URLItemCreate, StoredItemResponse,
    LocalItemCreate, FocusView
    )



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
from utils.cleaner import clean_text





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
SENTIMENTS_STORAGE: list[dict] = []

# Persistent tasks: {task_id -> {"text": str, "completed": bool, "generated_from_items": list[str]}}
PERSISTENT_TASKS: dict[str, dict] = {}

# Caching system for daily plan
DAILY_PLAN_CACHE: DailyPlanResponse | None = None
DAILY_PLAN_LOCK = asyncio.Lock()
DAILY_PLAN_REGENERATING = False


async def _regenerate_daily_plan_background() -> None:
    """Regenera el plan diario en background solo si hay menos de 5 tareas no completadas."""
    global DAILY_PLAN_CACHE, DAILY_PLAN_REGENERATING
    
    async with DAILY_PLAN_LOCK:
        DAILY_PLAN_REGENERATING = True
        try:
            if not OLLAMA_AVAILABLE:
                DAILY_PLAN_REGENERATING = False
                return
            
            # Contar tareas no completadas
            active_tasks = [t for t in PERSISTENT_TASKS.values() if not t["completed"]]
            
            # Solo generar nuevas si hay menos de 5 activas
            if len(active_tasks) < 5:
                new_tasks = await _call_ollama_for_plan(_generate_daily_plan_prompt())
                if new_tasks:
                    for task in new_tasks:
                        task_id = str(uuid.uuid4())
                        PERSISTENT_TASKS[task_id] = {
                            "text": task.text,
                            "completed": False,
                            "generated_from_item": task.generated_from,
                            "generated_from_items": list(STORAGE.keys())
                        }
            
            # Construir respuesta con tareas actuales
            DAILY_PLAN_CACHE = await _build_daily_plan_from_persistent()
        except Exception as e:
            print(f"Error regenerating daily plan: {e}")
        finally:
            DAILY_PLAN_REGENERATING = False


async def _build_daily_plan_from_persistent() -> DailyPlanResponse:
    """Construye DailyPlanResponse desde tareas persistentes, mostrando solo las no completadas."""
    # Filtrar tareas no completadas
    active_tasks = [
        DailyTask(id=tid, text=data["text"], completed=False, generated_from=data.get("generated_from_item"))
        for tid, data in PERSISTENT_TASKS.items()
        if not data["completed"]
    ]
    
    # Si no hay tareas activas, intentar generar nuevas
    if not active_tasks and OLLAMA_AVAILABLE:
        prompt = _generate_daily_plan_prompt()
        if prompt:
            new_tasks = await _call_ollama_for_plan(prompt)
            if new_tasks:
                for task in new_tasks:
                    task_id = str(uuid.uuid4())
                    PERSISTENT_TASKS[task_id] = {
                        "text": task.text,
                        "completed": False,
                        "generated_from_item": task.generated_from,
                        "generated_from_items": list(STORAGE.keys())
                    }
                active_tasks = new_tasks
    
    message = "Daily plan with persistent tasks."
    
    return DailyPlanResponse(
        tasks=active_tasks[:6],
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
        cleaned_text = clean_text(extracted_text)
        item_data = {
            "id": item_id,
            "source_type": "url",
            "title": payload.title or str(payload.url),
            "url": str(payload.url),
            "tags": payload.tags,
            "extracted_text": cleaned_text,
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
            extracted_text=cleaned_text[:500],  # Preview
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
        
        cleaned_text = clean_text(extracted_text)
        item_data = {
            "id": item_id,
            "source_type": "local_file",
            "title": payload.title or file_path.name,
            "file_path": str(file_path),
            "tags": payload.tags,
            "extracted_text": cleaned_text,
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
            extracted_text=cleaned_text[:500],
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
        
        cleaned_text = clean_text(extracted_text)
        item_data = {
            "id": item_id,
            "source_type": "uploaded_file",
            "title": filename,
            "filename": filename,
            "extracted_text": cleaned_text,
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
            extracted_text=cleaned_text[:500],
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
    
    # Eliminar tareas asociadas a este item
    tasks_to_remove = [
        tid for tid, data in PERSISTENT_TASKS.items()
        if item_id in data.get("generated_from_items", [])
    ]
    for tid in tasks_to_remove:
        del PERSISTENT_TASKS[tid]
    
    asyncio.create_task(_regenerate_daily_plan_background())


@app.get("/api/v1/daily-plan", response_model=DailyPlanResponse)
async def generate_daily_plan() -> DailyPlanResponse:
    """Retorna el plan diario cacheado con tareas persistentes, esperando si está regenerando."""
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
        DAILY_PLAN_CACHE = await _build_daily_plan_from_persistent()
        return DAILY_PLAN_CACHE


@app.post("/api/v1/daily-plan/tasks/{task_id}/complete", status_code=200)
async def complete_task(task_id: str) -> dict[str, bool]:
    """Marca una tarea como completada."""
    if task_id not in PERSISTENT_TASKS:
        raise HTTPException(status_code=404, detail="Task not found")
    
    PERSISTENT_TASKS[task_id]["completed"] = True
    
    # Regenerar el plan si hay menos de 5 tareas activas
    active_tasks = [t for t in PERSISTENT_TASKS.values() if not t["completed"]]
    if len(active_tasks) < 5:
        asyncio.create_task(_regenerate_daily_plan_background())
    
    return {"completed": True}


def _generate_daily_plan_prompt() -> str:
    """Sintetiza un prompt con todos los elementos almacenados."""
    items_summary = []
    
    for item_id, item_data in STORAGE.items():
        source_type = item_data.get("source_type", "unknown")
        id = item_data.get("id", "unknown_id")
        title = item_data.get("title", "Untitled")
        tags = item_data.get("tags", [])
        text_preview = item_data.get("extracted_text", "")[:300]
        
        item_summary = f"<id>{id}</id> [{source_type}] {title}"
        if tags:
            item_summary += f" (Tags: {', '.join(tags)})"
        if text_preview:
            item_summary += f"\n  Preview: {text_preview}..."
        
        items_summary.append(item_summary)
    
    if not items_summary:
        return ""
    
    prompt = (
        "You are a task planner. Generate 4-6 specific daily tasks based EXCLUSIVELY on the stored items below.\n\n"
        "STORED ITEMS:\n"
        + "\n".join(items_summary)
        + "\n\n"
        "CRITICAL RULES:\n"
        "1. Every task MUST explicitly reference a stored item by its title or content\n"
        "2. NO generic tasks like 'Review stored resources' or 'Work on project'\n"
        "3. Format: [Emoji] [Action verb] <id>[item_id]</id>\n"
        "4. Examples:\n"
        "   - ✅ '📄 Read memo_teletrabajo_2024.txt about remote work policy'\n"
        "   - ✅ '📊 Analyze Q4 2024 support incidents from incidencias_soporte_Q4_2024.csv'\n"
        "   - ❌ 'Review stored resources' (too generic)\n"
        "   - ❌ 'Work on project' (no item reference)\n\n"
        "OUTPUT FORMAT:\n"
        "Write ONE task per line. Start each task with an emoji.\n"
        "Do NOT use JSON, code blocks, or markdown. Just plain text, one task per line.\n\n"
        "Example output:\n"
        "📄 Read memo_teletrabajo_2024.txt about remote work policy\n"
        "📊 Analyze Q4 2024 support incidents\n\n"
        "Generate the tasks now:"
    )
    
    return prompt


@app.post("/api/v1/sentiments", response_model=SentimentResponse, status_code=201)
async def record_sentiment(payload: SentimentCreate) -> SentimentResponse:
    """Registra el sentimiento/humor del usuario."""
    sentiment_data = {
        "sentiment": payload.sentiment,
        "generated_at": datetime.utcnow()
    }
    SENTIMENTS_STORAGE.append(sentiment_data)
    return SentimentResponse(**sentiment_data)


@app.get("/api/v1/sentiments")
async def list_sentiments() -> list[dict]:
    """Lista el historial de sentimientos registrados."""
    return SENTIMENTS_STORAGE


async def _call_ollama_for_plan(prompt: str) -> list[DailyTask] | None:
    """Llama a ollama para generar el plan diario, reintentando hasta 3 veces si el formato es inválido."""
    if not OLLAMA_AVAILABLE:
        return None
    
    max_retries = 3
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"Ollama attempt {attempt}/{max_retries}")
            
            response = ollama.generate(
                model="llama3.2",
                prompt=prompt,
                stream=False,
            )
            
            response_text = response.get("response", "").strip()

            # Imprimir prompt y respuesta para debugging
            if attempt == 1:
                print("Prompt sent to Ollama:")
                print(prompt)
            print(f"Raw response from Ollama (attempt {attempt}):")
            print(response_text)
            
            # Limpiar markdown si está presente
            cleaned_text = response_text
            if "```" in response_text:
                # Eliminar bloques de código markdown
                import re
                cleaned_text = re.sub(r'```[^`]*```', '', response_text, flags=re.DOTALL).strip()
            
            # Procesar líneas
            lines = [line.strip() for line in cleaned_text.split('\n') if line.strip()]
            
            # Filtrar líneas que parecen tareas (no vacías, no son cabeceras)
            tasks = []
            for line in lines:
                # Ignorar líneas comunes que no son tareas
                if any(skip in line.lower() for skip in ['output:', 'tasks:', 'example', '---', '===']):
                    continue
                # Ignorar líneas que empiezan con - o * (lista markdown)
                if line.startswith(('-', '*', '•')):
                    line = line[1:].strip()
                # Ignorar líneas numeradas como "1.", "2."
                if len(line) > 2 and line[0].isdigit() and line[1] in '.)':
                    line = line[2:].strip()
                
                # Verificar que tenga contenido sustancial
                if len(line) >= 10:  # Al menos 10 caracteres
                    # Extraer ID del item si está presente en formato <id>...</id>
                    item_id = None
                    if '<id>' in line and '</id>' in line:
                        import re
                        id_match = re.search(r'<id>([^<]+)</id>', line)
                        if id_match:
                            item_id = id_match.group(1).strip()
                            # Limpiar la línea del tag de ID
                            line = re.sub(r'\s*<id>[^<]+</id>\s*', '', line).strip()
                    
                    tasks.append({"text": line, "item_id": item_id})

            # Limitar a 6 tareas máximo
            tasks = tasks[:6]
            
            # Validar que tengamos al menos 3 tareas
            if len(tasks) >= 3:
                print(f"Successfully parsed {len(tasks)} tasks on attempt {attempt}")
                return [
                    DailyTask(
                        id=str(idx),
                        text=task["text"],
                        completed=False,
                        generated_from=task["item_id"]
                    )
                    for idx, task in enumerate(tasks, 1)
                ]
            
            print(f"Invalid format on attempt {attempt}: only found {len(tasks)} tasks (need at least 3)")
            if attempt < max_retries:
                print(f"Retrying...")
                continue
        
        except Exception as e:
            print(f"Error calling ollama on attempt {attempt}: {e}")
            if attempt < max_retries:
                continue
    
    print(f"Failed to generate valid tasks after {max_retries} attempts")
    return None