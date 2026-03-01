# Configuración del Backend

Esta guía explica cómo levantar el backend de Smart Brain con PostgreSQL, embeddings y RAG.

## Requisitos previos

- **Python 3.12+**
- **Docker y Docker Compose** (para PostgreSQL + pgvector)
- **uv** (instalador rápido de paquetes Python) - [Instalación](https://github.com/astral-sh/uv)
- **Ollama** con el modelo `llama3.2` - [Instalación](https://ollama.ai)

## Inicio rápido

```bash
# 1. Levantar PostgreSQL con pgvector
docker-compose up -d

# 2. Crear entorno virtual e instalar dependencias
make setup && make install

# 3. Activar entorno
source .venv/bin/activate

# 4. Crear archivo .env
cat > .env << EOF
DATABASE_URL=postgresql://smartbrain_user:smartbrain_dev_password@localhost:5432/smartbrain
EOF

# 5. Ejecutar servidor
make run
# O manualmente: uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

La API estará disponible en `http://localhost:5000`.

## Configuración manual (detallada)

### 1. Crear entorno virtual
Crear un entorno virtual con Python 3.12:
```bash
uv venv --python 3.12
```

### 2. Activar entorno
**Linux / macOS:**
```bash
source .venv/bin/activate
```

**Windows:**
```powershell
.venv\Scripts\activate
```

### 3. Instalar dependencias
Instalar los paquetes necesarios:
```bash
uv pip install -r requierements.txt
```

**Nota:** si te quedas sin espacio durante la instalación (especialmente con PyTorch), usa la versión CPU-only:
```bash
uv pip install sentence-transformers --extra-index-url https://download.pytorch.org/whl/cpu
```

### 4. Configurar base de datos
La base de datos se crea automáticamente al iniciar Docker Compose:
```bash
docker-compose up -d
```

Verifica que esté corriendo:
```bash
docker exec smartbrain-postgres psql -U smartbrain_user -d smartbrain -c "SELECT 1;"
```

### 5. Configurar variables de entorno
Crear archivo `.env` en la carpeta backend:
```bash
DATABASE_URL=postgresql://smartbrain_user:smartbrain_dev_password@localhost:5432/smartbrain
```

## Arquitectura

### Capa de base de datos
- **Driver**: asyncpg para operaciones asíncronas con PostgreSQL
- **Connection pooling**: `min_size=2`, `max_size=10`
- **Tablas**: `items`, `tasks`, `embeddings` (con pgvector), `chat_messages`
- **DAOs**: `ItemDAO`, `TaskDAO`, `EmbeddingDAO`

### Capa AI/ML
- **LLM**: Ollama `llama3.2` para chat y generación de tareas
- **Embeddings**: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensiones)
- **RAG**: búsqueda semántica por similitud coseno con pgvector
- **Worker en segundo plano**: generación automática de embeddings para nuevos ítems

### Endpoints API
- `POST /api/v1/items/urls` - Añadir URL/video de YouTube
- `POST /api/v1/items/files` - Subir archivo (PDF, DOCX, Excel, etc.)
- `POST /api/v1/items/local-files` - Añadir ruta de archivo local
- `GET /api/v1/items` - Listar/buscar ítems
- `DELETE /api/v1/items/{id}` - Eliminar ítem
- `GET /api/v1/daily-plan` - Obtener tareas diarias
- `POST /api/v1/daily-plan/tasks/{id}/complete` - Marcar tarea como completada
- `POST /api/v1/chat` - Chat con RAG
- `GET /api/v1/embeddings/status` - Estado del worker de embeddings

## Automatización con Makefile

Comandos disponibles:

- **`make setup`** - Crear entorno virtual
- **`make install`** - Instalar dependencias
- **`make activate`** - Mostrar comando de activación
- **`make run`** - Iniciar FastAPI con hot-reload
- **`make test`** - Ejecutar tests con pytest
- **`make clean`** - Eliminar entorno virtual
- **`make help`** - Ver todos los comandos

## Solución de problemas

### Errores de conexión a la base de datos

**Problema:** `ConnectionRefusedError` o `database does not exist`

**Solución:**
```bash
# Comprobar si PostgreSQL está activo
docker ps | grep smartbrain-postgres

# Si no está activo, iniciarlo
docker-compose up -d

# Verificar conexión y tablas
docker exec smartbrain-postgres psql -U smartbrain_user -d smartbrain -c "\dt"
```

### Ollama no disponible

**Problema:** El chat devuelve "Ollama is not available"

**Solución:**
```bash
# Verificar que Ollama está corriendo
ollama list

# Descargar llama3.2 si no está instalado
ollama pull llama3.2

# Probar modelo
ollama run llama3.2 "Hello, how are you?"
```

### Embeddings no generados

**Problema:** Se añaden ítems pero no aparecen embeddings

**Solución:**
```bash
# Comprobar estado del worker
curl http://localhost:5000/api/v1/embeddings/status

# Revisar logs del backend para mensajes como:
# "📦 Loading embedding model..."
# "✓ Embedding model loaded"
# "📊 Found X items to process for embeddings"

# Verificar embeddings en la base de datos
docker exec smartbrain-postgres psql -U smartbrain_user -d smartbrain -c "SELECT COUNT(*) FROM embeddings;"
```

### Sin espacio en disco durante la instalación

**Problema:** `No space left on device (os error 28)` al instalar dependencias

**Solución:**
```bash
# Usar PyTorch CPU-only (mucho más ligero)
uv pip install sentence-transformers --extra-index-url https://download.pytorch.org/whl/cpu

# O liberar espacio y reintentar
docker system prune -a
```

### Errores de importación

**Problema:** `ModuleNotFoundError` al ejecutar el servidor

**Solución:**
```bash
# Asegurar entorno virtual activo
source .venv/bin/activate

# Reinstalar dependencias
uv pip install -r requierements.txt

# Verificar imports
python -c "import fastapi; import asyncpg; import sentence_transformers; print('All imports OK')"
```

### Puerto en uso

**Problema:** `Address already in use` al iniciar el servidor

**Solución:**
```bash
# Encontrar proceso en puerto 5000
lsof -i :5000

# Matar proceso (reemplazar PID)
kill -9 <PID>

# O usar otro puerto
uvicorn main:app --host 0.0.0.0 --port 5001 --reload
```

## Documentación adicional

- **[EMBEDDINGS.md](./EMBEDDINGS.md)** - Guía detallada del sistema de embeddings
- **[CHAT_RAG.md](./CHAT_RAG.md)** - Implementación y configuración de RAG
- **[database/README.md](./database/README.md)** - Esquema de base de datos y DAOs

## Testing

Ejecutar tests con pytest:
```bash
make test
# O manualmente: pytest tests/ -v
```

Los tests están en `tests/` y cubren:
- Extracción de texto (PDF, DOCX, Excel, CSV, etc.)
- Limpieza y preprocesado de texto
- Cargadores estáticos