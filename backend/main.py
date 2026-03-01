import asyncio
import io
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import UUID

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, HttpUrl

try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

from database.connection import db
from database.item_dao import ItemDAO
from database.task_dao import TaskDAO
from database.embedding_dao import EmbeddingDAO
from utils.embeddings import get_embedding_model, generate_embeddings_for_text
from models import (
    ChatMessageCreate,
    DailyPlanResponse,
    DailyTask,
    FocusView,
    LocalItemCreate,
    SentimentCreate,
    SentimentResponse,
    StoredItemResponse,
    URLItemCreate,
    SearchRequest,
)
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
    description="API REST para items almacenados y chat RAG.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database DAOs
item_dao: ItemDAO | None = None
task_dao: TaskDAO | None = None
embedding_dao: EmbeddingDAO | None = None

# Background worker control
embedding_worker_task: asyncio.Task | None = None
embedding_worker_running = False

# Storage in-memory (sustituir por DB en producción)
STORAGE: dict[str, dict] = {}
SENTIMENTS_STORAGE: list[dict] = []

# Persistent tasks: {task_id -> {"text": str, "completed": bool, "generated_from_items": list[str]}}
PERSISTENT_TASKS: dict[str, dict] = {}

# Daily plan cache
DAILY_PLAN_LOCK = asyncio.Lock()
DAILY_PLAN_CACHE: DailyPlanResponse | None = None
DAILY_PLAN_REGENERATING = False

@app.on_event("startup")
async def startup():
    """Initialize database connection on startup."""
    global item_dao, task_dao, embedding_dao, embedding_worker_task, embedding_worker_running
    await db.connect()
    item_dao = ItemDAO(db.pool)
    task_dao = TaskDAO(db.pool)
    embedding_dao = EmbeddingDAO(db.pool)
    print("✓ DAOs initialized")
    
    # Start embedding background worker
    embedding_worker_running = True
    embedding_worker_task = asyncio.create_task(_embedding_background_worker())
    print("✓ Embedding background worker started")


@app.on_event("shutdown")
async def shutdown():
    """Close database connection on shutdown."""
    global embedding_worker_running, embedding_worker_task
    
    # Stop embedding worker
    embedding_worker_running = False
    if embedding_worker_task:
        embedding_worker_task.cancel()
        try:
            await embedding_worker_task
        except asyncio.CancelledError:
            pass
    print("✓ Embedding worker stopped")
    
    await db.disconnect()
    print("✓ Database disconnected")


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "database": "connected" if db.pool else "disconnected"}


@app.get("/api/v1/embeddings/status")
async def get_embeddings_status() -> dict:
    """Get status of embedding generation process."""
    if not embedding_dao:
        return {"error": "Embedding DAO not initialized"}
    
    try:
        items_without_embeddings = await embedding_dao.get_items_without_embeddings(limit=100)
        return {
            "worker_running": embedding_worker_running,
            "items_pending": len(items_without_embeddings),
            "model_loaded": get_embedding_model() is not None
        }
    except Exception as e:
        return {"error": str(e)}


async def _embedding_background_worker() -> None:
    """
    Background worker that continuously processes items without embeddings.
    Runs every 30 seconds and processes up to 5 items per iteration.
    """
    global embedding_dao, embedding_worker_running
    
    print("🔄 Embedding worker started, checking for items to process...")
    
    # Pre-load the model to avoid loading it on every iteration
    embedding_model = get_embedding_model()
    
    while embedding_worker_running:
        try:
            if not embedding_dao:
                await asyncio.sleep(5)
                continue
            
            # Get items without embeddings
            items_to_process = await embedding_dao.get_items_without_embeddings(limit=5)
            
            if not items_to_process:
                # No items to process, wait longer
                await asyncio.sleep(30)
                continue
            
            print(f"📊 Found {len(items_to_process)} items to process for embeddings")
            
            for item in items_to_process:
                if not embedding_worker_running:
                    break
                
                item_id = item["id"]
                extracted_text = item.get("extracted_text", "")
                title = item.get("title", "")
                
                if not extracted_text:
                    print(f"⚠️  Item {item_id} has no text to embed, skipping")
                    continue
                
                try:
                    # Include title in the text for better context
                    full_text = f"{title}\n\n{extracted_text}" if title else extracted_text
                    
                    # Generate embeddings
                    print(f"🔮 Generating embeddings for item: {title[:50]}...")
                    embeddings_data = await generate_embeddings_for_text(full_text, embedding_model)
                    
                    if not embeddings_data:
                        print(f"⚠️  No embeddings generated for item {item_id}")
                        continue
                    
                    # Store embeddings in database
                    for chunk_index, (chunk_text, embedding_vector) in enumerate(embeddings_data):
                        await embedding_dao.create(
                            item_id=item_id,
                            chunk_index=chunk_index,
                            chunk_text=chunk_text,
                            embedding=embedding_vector
                        )
                    
                    print(f"✓ Stored {len(embeddings_data)} embeddings for item: {title[:50]}")
                
                except Exception as e:
                    print(f"❌ Error generating embeddings for item {item_id}: {e}")
                    continue
            
            # Wait before next iteration
            await asyncio.sleep(10)
        
        except asyncio.CancelledError:
            print("🛑 Embedding worker cancelled")
            break
        except Exception as e:
            print(f"❌ Error in embedding worker: {e}")
            await asyncio.sleep(30)
    
    print("✓ Embedding worker stopped")


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
                prompt = await _generate_daily_plan_prompt()
                new_tasks = await _call_ollama_for_plan(prompt)
                if new_tasks:
                    for task in new_tasks:
                        # Crear tarea en la base de datos
                        task_data = {
                            "text": task.text,
                            "completed": False,
                            "generated_from_item": task.generated_from,
                            "generated_from_items": list(STORAGE.keys()),
                        }
                        task_id = await task_dao.create(task_data)
                        # Convertir UUID a string para PERSISTENT_TASKS
                        task_id_str = str(task_id)
                        # Actualizar cache en memoria para disponibilidad inmediata
                        PERSISTENT_TASKS[task_id_str] = {
                            "text": task.text,
                            "completed": False,
                            "generated_from_item": task.generated_from,
                            "generated_from_items": list(STORAGE.keys()),
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
        DailyTask(
            id=tid,
            text=data["text"],
            completed=False,
            generated_from=data.get("generated_from_item"),
        )
        for tid, data in PERSISTENT_TASKS.items()
        if not data["completed"]
    ]

    # Si no hay tareas activas, intentar generar nuevas
    if not active_tasks and OLLAMA_AVAILABLE:
        prompt = await _generate_daily_plan_prompt()
        if prompt:
            new_tasks = await _call_ollama_for_plan(prompt)
            if new_tasks:
                for task in new_tasks:
                    # Crear tarea en la base de datos
                    task_data = {
                        "text": task.text,
                        "completed": False,
                        "generated_from_item": task.generated_from,
                        "generated_from_items": list(STORAGE.keys()),
                    }
                    task_id = await task_dao.create(task_data)
                    # Convertir UUID a string para PERSISTENT_TASKS
                    task_id_str = str(task_id)
                    # Actualizar cache en memoria para disponibilidad inmediata
                    PERSISTENT_TASKS[task_id_str] = {
                        "text": task.text,
                        "completed": False,
                        "generated_from_item": task.generated_from,
                        "generated_from_items": list(STORAGE.keys()),
                    }
                active_tasks = new_tasks

    message = "Daily plan with persistent tasks."

    return DailyPlanResponse(
        tasks=active_tasks[:6],
        generated_at=datetime.utcnow().isoformat(),
        message=message,
    )


@app.get("/api/v1/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/items/urls", response_model=StoredItemResponse, status_code=201)
async def create_item_from_url(payload: URLItemCreate) -> StoredItemResponse:
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        extracted_text = get_webpage_text(str(payload.url))
        cleaned_text = clean_text(extracted_text)
        
        item_data = {
            "source_type": "url",
            "title": payload.title or str(payload.url),
            "url": str(payload.url),
            "tags": payload.tags,
            "extracted_text": cleaned_text,
            "status": "ready"
        }
        
        # Insert into database
        item_id = await item_dao.create(item_data)
        
        # Also update in-memory cache for immediate availability
        STORAGE[str(item_id)] = {**item_data, "id": str(item_id)}
        
        # Trigger background regeneration
        asyncio.create_task(_regenerate_daily_plan_background())
        
        return StoredItemResponse(
            id=str(item_id),
            source_type="url",
            title=item_data["title"],
            status="ready",
            extracted_text=cleaned_text[:500],
            youtube_url=(
                str(payload.url)
                if "youtube.com" in str(payload.url) or "youtu.be" in str(payload.url)
                else None
            ),
        )
    except Exception as e:
        print(f"Error creating URL item: {e}")
        return StoredItemResponse(
            id="error",
            source_type="url",
            title=payload.title or str(payload.url),
            status="failed",
            error_message=str(e),
        )


@app.post(
    "/api/v1/items/local-files", response_model=StoredItemResponse, status_code=201
)
async def create_item_from_local_file(payload: LocalItemCreate) -> StoredItemResponse:
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
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
            "source_type": "local_file",
            "title": payload.title or file_path.name,
            "file_path": str(file_path),
            "filename": file_path.name,
            "tags": payload.tags,
            "extracted_text": cleaned_text,
            "status": "ready",
        }
        item_id = await item_dao.create(item_data)
        item_id_str = str(item_id)
        # Actualizar STORAGE para disponibilidad inmediata en frontend
        STORAGE[item_id_str] = {
            "id": item_id_str,
            **item_data,
            "created_at": datetime.utcnow().isoformat(),
        }
        asyncio.create_task(_regenerate_daily_plan_background())
        return StoredItemResponse(
            id=item_id_str,
            source_type="local_file",
            title=item_data["title"],
            status="ready",
            extracted_text=cleaned_text[:500],
        )
    except Exception as e:
        item_data = {
            "source_type": "local_file",
            "title": payload.title or file_path.name,
            "file_path": str(file_path),
            "filename": file_path.name,
            "tags": payload.tags,
            "status": "failed",
            "extracted_text": str(e),
        }
        # Intentar guardar en DB el error
        try:
            item_id = await item_dao.create(item_data)
            item_id_str = str(item_id)
        except:
            item_id_str = str(uuid.uuid4())
        
        STORAGE[item_id_str] = {
            "id": item_id_str,
            **item_data,
            "created_at": datetime.utcnow().isoformat(),
        }
        asyncio.create_task(_regenerate_daily_plan_background())
        return StoredItemResponse(
            id=item_id_str,
            source_type="local_file",
            title=item_data["title"],
            status="failed",
            error_message=str(e),
        )


@app.post("/api/v1/items/files", response_model=StoredItemResponse, status_code=201)
async def create_item_from_uploaded_file(
    file: UploadFile = File(...),
) -> StoredItemResponse:
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")

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
            "source_type": "uploaded_file",
            "title": filename,
            "filename": filename,
            "extracted_text": cleaned_text,
            "status": "ready",
        }
        item_id = await item_dao.create(item_data)
        item_id_str = str(item_id)
        # Actualizar STORAGE para disponibilidad inmediata en frontend
        STORAGE[item_id_str] = {
            "id": item_id_str,
            **item_data,
            "created_at": datetime.utcnow().isoformat(),
        }
        asyncio.create_task(_regenerate_daily_plan_background())
        return StoredItemResponse(
            id=item_id_str,
            source_type="uploaded_file",
            title=filename,
            status="ready",
            extracted_text=cleaned_text[:500],
        )
    except Exception as e:
        filename = file.filename or "unknown"
        item_data = {
            "source_type": "uploaded_file",
            "title": filename,
            "filename": filename,
            "status": "failed",
            "extracted_text": str(e),
        }
        # Intentar guardar en DB el error
        try:
            item_id = await item_dao.create(item_data)
            item_id_str = str(item_id)
        except:
            item_id_str = str(uuid.uuid4())
        
        STORAGE[item_id_str] = {
            "id": item_id_str,
            **item_data,
            "created_at": datetime.utcnow().isoformat(),
        }
        asyncio.create_task(_regenerate_daily_plan_background())
        return StoredItemResponse(
            id=item_id_str,
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
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    if q:
        items = await item_dao.list_by_search(q)
    else:
        items = await item_dao.list_all()

    # Simplificar respuesta (sin texto completo)
    items_summary = [
        {
            "id": str(item["id"]),
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


@app.post("/api/v1/search")
async def search_items(payload: SearchRequest) -> list[dict]:
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    items = await item_dao.list_by_search(payload.query, payload.tags)
    return items


@app.get("/api/v1/items/{item_id}")
async def get_item(item_id: str) -> dict:
    if not item_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        item_uuid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    item = await item_dao.get_by_id(item_uuid)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return STORAGE[item_id]


@app.delete("/api/v1/items/{item_id}", status_code=204)
async def delete_item(item_id: str) -> None:
    if not item_dao or not task_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        item_uuid = UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid item ID format")
    
    # Delete from database
    deleted = await item_dao.delete(item_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="Item not found")
    
    # Delete associated tasks from database
    await task_dao.delete_by_items([item_uuid])
    
    # Also update in-memory cache
    if item_id in STORAGE:
        del STORAGE[item_id]
    
    # Remove from persistent tasks cache
    tasks_to_remove = [
        tid
        for tid, data in PERSISTENT_TASKS.items()
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
            detail="Ollama is not available. Install the 'ollama' Python package and ensure ollama service is running.",
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
    if not task_dao:
        raise HTTPException(status_code=503, detail="Database not initialized")
    
    try:
        task_uuid = UUID(task_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid task ID format")
    
    # Update in database
    updated = await task_dao.update_completion(task_uuid, True)
    if not updated:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Also update in-memory cache
    if task_id in PERSISTENT_TASKS:
        PERSISTENT_TASKS[task_id]["completed"] = True
    
    # Regenerate plan if less than 5 active tasks
    active_count = await task_dao.count_active()
    if active_count < 5:
        asyncio.create_task(_regenerate_daily_plan_background())

    return {"completed": True}


async def _generate_daily_plan_prompt() -> str:
    """Sintetiza un prompt con todos los elementos almacenados desde la BD."""
    if not item_dao:
        return ""
    
    items_summary = []
    all_items = await item_dao.list_all(limit=50)

    for item_data in all_items:
        source_type = item_data.get("source_type", "unknown")
        title = item_data.get("title", "Untitled")
        item_id = str(item_data.get("id", "unknown"))

        item_summary = f"<id>{item_id}</id> [{source_type}] {title}"
        items_summary.append(item_summary)

    if not items_summary:
        return ""

    prompt = (
        "You are a task planner. Generate 4-6 specific daily tasks based EXCLUSIVELY on the stored items below.\n\n"
        "STORED ITEMS:\n" + "\n".join(items_summary) + "\n\n"
        "CRITICAL RULES:\n"
        "1. Every task MUST explicitly reference a stored item by its title or content\n"
        "2. NO generic tasks like 'Review stored resources' or 'Work on project'\n"
        "3. Format: [Emoji] [Action verb] [item reference]\n"
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
    sentiment_data = {"sentiment": payload.sentiment, "generated_at": datetime.utcnow()}
    SENTIMENTS_STORAGE.append(sentiment_data)
    return SentimentResponse(**sentiment_data)


@app.get("/api/v1/sentiments")
async def list_sentiments() -> list[dict]:
    """Lista el historial de sentimientos registrados."""
    return SENTIMENTS_STORAGE


@app.post("/api/v1/chat")
async def chat_with_rag(payload: ChatMessageCreate) -> dict:
    """
    Chat endpoint with RAG (Retrieval-Augmented Generation).
    Retrieves relevant context from embeddings and generates response with Ollama.
    """
    if not OLLAMA_AVAILABLE:
        return {
            "text": "⚠️ Ollama is not available. Please make sure the service is running.",
            "role": "ai"
        }
    
    if not embedding_dao:
        return {
            "text": "⚠️ Embedding system is not initialized.",
            "role": "ai"
        }
    
    try:
        user_message = payload.message
        
        # Step 1: Generate embedding for user query
        embedding_model = get_embedding_model()
        if not embedding_model:
            return {
                "text": "⚠️ Embedding model not available. Responding without context...\n\n" + 
                        await _call_ollama_simple(user_message),
                "role": "ai"
            }
        
        # Generate query embedding
        query_embeddings = await generate_embeddings_for_text(user_message, embedding_model)
        if not query_embeddings:
            return {
                "text": "⚠️ Could not generate embedding. Responding without context...\n\n" + 
                        await _call_ollama_simple(user_message),
                "role": "ai"
            }
        
        query_vector = query_embeddings[0][1]  # First chunk's embedding
        
        # Step 2: Search for similar embeddings (RAG retrieval)
        print(f"🔍 Searching for relevant context: {user_message[:50]}...")
        similar_chunks = await embedding_dao.search_similar(query_vector, limit=5)
        
        # Step 3: Build context from retrieved chunks
        context_parts = []
        if similar_chunks:
            print(f"✓ Found {len(similar_chunks)} relevant chunks")
            for i, chunk in enumerate(similar_chunks, 1):
                similarity = chunk.get('similarity', 0)
                print(f"  - Chunk {i}: {chunk['title'][:50]}... (similarity: {similarity:.3f})")
                if similarity > 0.2:  # Only use chunks with >20% similarity (lowered threshold)
                    context_parts.append(
                        f"[Source {i}: {chunk['title']}]\n{chunk['chunk_text']}\n"
                    )
        
        # Step 4: Generate response with Ollama
        if context_parts:
            context_text = "\n---\n".join(context_parts)
            prompt = f"""You are an intelligent assistant. Answer the user's question based on the provided context.

RELEVANT CONTEXT:
{context_text}

USER QUESTION:
{user_message}

INSTRUCTIONS:
- Respond in English clearly and concisely
- Use the provided context to give accurate information
- If the context is not sufficient, say you don't have specific information
- Mention the sources when relevant
- Be conversational and friendly

RESPONSE:"""
        else:
            print("⚠️  No relevant context found, responding generally")
            prompt = f"""You are an intelligent assistant. Answer the user's question helpfully.

USER QUESTION:
{user_message}

NOTE: I don't have access to specific information about this topic in my current knowledge base.

RESPONSE:"""
        
        # Call Ollama
        print(f"🤖 Calling Ollama (model: gpt-oss:20b)...")
        response = ollama.generate(
            model='gpt-oss:20b',
            prompt=prompt,
            options={
                'temperature': 0.7,
                'top_p': 0.9,
            }
        )
        
        ai_response = response.get('response', '').strip()
        
        if not ai_response:
            return {
                "text": "⚠️ Could not generate a response. Please try again.",
                "role": "ai"
            }
        
        print(f"✓ Response generated ({len(ai_response)} characters)")
        
        return {
            "text": ai_response,
            "role": "ai"
        }
    
    except Exception as e:
        print(f"❌ Error in chat: {e}")
        return {
            "text": f"⚠️ Error processing your message: {str(e)}",
            "role": "ai"
        }


async def _call_ollama_simple(message: str) -> str:
    """Simple Ollama call without RAG context."""
    try:
        response = ollama.generate(
            model='gpt-oss:20b',
            prompt=f"Answer this question briefly: {message}",
            options={'temperature': 0.7}
        )
        return response.get('response', 'Could not generate response.').strip()
    except Exception as e:
        return f"Error: {str(e)}"
        return f"Error: {str(e)}"


async def _call_ollama_for_plan(prompt: str) -> list[DailyTask] | None:
    """Llama a ollama para generar el plan diario, reintentando hasta 3 veces si el formato es inválido."""
    if not OLLAMA_AVAILABLE:
        return None

    max_retries = 3

    for attempt in range(1, max_retries + 1):
        try:
            print(f"Ollama attempt {attempt}/{max_retries}")

            response = ollama.generate(
                model="gpt-oss:20b",
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

                cleaned_text = re.sub(
                    r"```[^`]*```", "", response_text, flags=re.DOTALL
                ).strip()

            # Procesar líneas
            lines = [line.strip() for line in cleaned_text.split("\n") if line.strip()]

            # Filtrar líneas que parecen tareas (no vacías, no son cabeceras)
            tasks = []
            for line in lines:
                # Ignorar líneas comunes que no son tareas
                if any(
                    skip in line.lower()
                    for skip in ["output:", "tasks:", "example", "---", "==="]
                ):
                    continue
                # Ignorar líneas que empiezan con - o * (lista markdown)
                if line.startswith(("-", "*", "•")):
                    line = line[1:].strip()
                # Ignorar líneas numeradas como "1.", "2."
                if len(line) > 2 and line[0].isdigit() and line[1] in ".)":
                    line = line[2:].strip()

                # Verificar que tenga contenido sustancial
                if len(line) >= 10:  # Al menos 10 caracteres
                    # Extraer ID del item si está presente en formato <id>...</id>
                    item_id = None
                    if "<id>" in line and "</id>" in line:
                        import re

                        id_match = re.search(r"<id>([^<]+)</id>", line)
                        if id_match:
                            item_id = id_match.group(1).strip()
                            # Limpiar la línea del tag de ID
                            line = re.sub(r"\s*<id>[^<]+</id>\s*", "", line).strip()

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
                        generated_from=task["item_id"],
                    )
                    for idx, task in enumerate(tasks, 1)
                ]

            print(
                f"Invalid format on attempt {attempt}: only found {len(tasks)} tasks (need at least 3)"
            )
            if attempt < max_retries:
                print(f"Retrying...")
                continue

        except Exception as e:
            print(f"Error calling ollama on attempt {attempt}: {e}")
            if attempt < max_retries:
                continue

    print(f"Failed to generate valid tasks after {max_retries} attempts")
    return None
