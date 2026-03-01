# Sistema de Embeddings en Segundo Plano

## Descripción

Este sistema genera automáticamente embeddings vectoriales para todos los items almacenados en la base de datos, permitiendo búsqueda semántica y RAG (Retrieval-Augmented Generation).

## Arquitectura

### Componentes

1. **`utils/embeddings.py`**: Utilidades para generar embeddings
   - Modelo: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensiones)
   - Chunking: Divide textos largos en fragmentos de ~500 caracteres con overlap de 50
   - Proceso asíncrono con thread pool para operaciones CPU-bound

2. **`database/embedding_dao.py`**: Acceso a datos de embeddings
   - `create()`: Almacena embedding chunk con upsert
   - `get_items_without_embeddings()`: Encuentra items pendientes de procesar
   - `search_similar()`: Búsqueda por similitud coseno usando pgvector

3. **Background Worker en `main.py`**:
   - Se inicia automáticamente con el servidor FastAPI
   - Procesa 5 items por iteración cada 10-30 segundos
   - Pre-carga el modelo de embeddings al inicio
   - Manejo de errores y cancelación limpia

## Flujo de Procesamiento

```
[Item Creado] → [Extraer Texto] → [Cola de Procesamiento]
                                          ↓
                                   [Background Worker]
                                          ↓
                            [Chunking + Generate Embeddings]
                                          ↓
                              [Almacenar en tabla embeddings]
                                          ↓
                            [Disponible para búsqueda RAG]
```

## Uso

### Verificar Estado

```bash
curl http://localhost:5000/api/v1/embeddings/status
```

Respuesta:
```json
{
  "worker_running": true,
  "items_pending": 3,
  "model_loaded": true
}
```

### Generar Embeddings Manualmente (Código)

```python
from utils.embeddings import generate_embeddings_for_text

text = "Tu texto largo aquí..."
embeddings = await generate_embeddings_for_text(text)

# Resultado: [(chunk_text, embedding_vector), ...]
for chunk, vector in embeddings:
    print(f"Chunk: {chunk[:50]}...")
    print(f"Vector dim: {len(vector)}")  # 384
```

### Búsqueda Semántica

```python
from database.embedding_dao import EmbeddingDAO
from utils.embeddings import generate_embeddings_for_text, get_embedding_model

# Generar embedding de la consulta
model = get_embedding_model()
query_text = "Cómo mejorar la productividad"
query_embeddings = await generate_embeddings_for_text(query_text, model)
query_vector = query_embeddings[0][1]  # Primer chunk

# Buscar similares
dao = EmbeddingDAO(db.pool)
results = await dao.search_similar(query_vector, limit=5)

for result in results:
    print(f"Similitud: {result['similarity']:.3f}")
    print(f"Texto: {result['chunk_text']}")
    print(f"Item: {result['title']}")
```

## Configuración

### Ajustar Tamaño de Chunks

En `utils/embeddings.py`:

```python
chunks = chunk_text(text, max_chunk_size=500, overlap=50)
```

- `max_chunk_size`: Caracteres máximos por chunk (default: 500)
- `overlap`: Caracteres de solapamiento entre chunks (default: 50)

### Ajustar Frecuencia del Worker

En `main.py` → `_embedding_background_worker()`:

```python
await asyncio.sleep(10)  # Espera entre iteraciones
```

### Cambiar Modelo de Embeddings

En `utils/embeddings.py`:

```python
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
```

**Importante**: Si cambias el modelo, actualiza la dimensión en `init.sql`:

```sql
embedding vector(384)  -- Cambiar según dimensión del modelo
```

## Requisitos

- `sentence-transformers>=5.0.0`
- `torch>=2.0.0` (versión CPU incluida para ahorrar espacio)
- PostgreSQL con extensión `pgvector`

## Monitoreo

El worker imprime logs en la salida estándar:

```
✓ Embedding background worker started
📊 Found 3 items to process for embeddings
🔮 Generating embeddings for item: Clean Code Principles...
✓ Stored 5 embeddings for item: Clean Code Principles
```

## Troubleshooting

### El worker no procesa items

1. Verificar que los items tengan `extracted_text` no vacío
2. Verificar estado: `curl .../embeddings/status`
3. Revisar logs del servidor

### Error de dimensión en vectores

Asegúrate de que la tabla `embeddings` tenga la dimensión correcta:

```sql
ALTER TABLE embeddings 
ALTER COLUMN embedding TYPE vector(384);  -- O la dimensión de tu modelo
```

### El modelo no se carga

Verifica que `sentence-transformers` esté instalado:

```bash
uv pip install sentence-transformers
```

La primera vez descargará el modelo (~90MB), tarda unos segundos.

## Próximos Pasos

1. **Implementar endpoint de búsqueda semántica**: `GET /api/v1/items/search-semantic`
2. **Integrar RAG en el chat**: Usar embeddings para recuperar contexto relevante
3. **Reindexación**: Endpoint para regenerar embeddings de items existentes
4. **Métricas**: Tracking de tiempo de procesamiento y calidad de embeddings
