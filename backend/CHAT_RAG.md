# Sistema de Chat con RAG

## Descripción

El sistema de chat integra Ollama con búsqueda semántica (RAG - Retrieval-Augmented Generation) para proporcionar respuestas contextualizadas basadas en el contenido almacenado.

## Arquitectura

### Flujo de procesamiento

```
[Mensaje Usuario] 
    ↓
[Generar Embedding Query] (all-MiniLM-L6-v2, Apache 2.0)
    ↓
[Búsqueda Semántica en Embeddings] (Top 5 chunks)
    ↓
[Filtrar por Similitud > 20%]
    ↓
[Construir Contexto con Fuentes]
    ↓
[Generar Prompt con Contexto + Pregunta]
    ↓
[Llamar a Ollama: gpt-oss:20b o llama3.2]
    ↓
[Retornar Respuesta]
```

**Nota**: Todos los modelos usados son software libre con licencias abiertas (Apache 2.0, Llama Community License), aunque en el caso de Llama la licencia no cumple totalmente la definición de software libre/open source al imponer ciertas restricciones sobre su ámbito de uso.

## Endpoint

### POST `/api/v1/chat`

**Request Body:**
```json
{
  "message": "¿Qué información tienes sobre clean code?",
  "retrieval_scope": [],      // Opcional: IDs de items específicos
  "delete_item_ids": []        // Opcional: IDs a eliminar
}
```

**Response:**
```json
{
  "text": "Clean Code es un término popularizado por Robert C. Martin...",
  "role": "ai"
}
```

## Ejemplo de Uso

### Desde curl

```bash
curl -X POST "http://localhost:5000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué es Vite?"}'
```

### Desde el Frontend

El componente `ChatInterface.jsx` envía automáticamente las consultas:

```jsx
// Configuración en ChatInterface.jsx
const chatRequest = {
  url: `${API_BASE_URL}/chat`,
  method: 'POST',
  serialize: (body) => {
    const lastMessage = body.messages[body.messages.length - 1];
    return JSON.stringify({ message: lastMessage.text });
  }
};
```

## Configuración

### Modelos de Lenguaje

En `main.py`, el chat soporta múltiples modelos abiertos:

**Principal: `gpt-oss:20b`** (Recomendado)
- Licencia: **Apache 2.0** (software libre)
- Parámetros: 20 mil millones
- Mejor balance rendimiento/calidad
- Tiempo respuesta: ~3-5 segundos

**Alternativa: `llama3.2`**
- Licencia: **Llama 3.2 Community License** (software libre para investigación y uso personal)
- Parámetros: 3.2 mil millones o superior
- Más ligero pero menos potente

```python
response = ollama.generate(
    model='gpt-oss:20b',  # O 'llama3.2' para versión más ligera
    prompt=prompt,
    options={
        'temperature': 0.7,  # Creatividad: 0.0-1.0
        'top_p': 0.9,        # Nucleus sampling
    }
)
```

### Parámetros de RAG

**Número de chunks a recuperar:**
```python
similar_chunks = await embedding_dao.search_similar(query_vector, limit=5)
```

**Threshold de similitud:**
```python
if similarity > 0.2:  # Solo chunks con >20% similitud
    context_parts.append(...)
```

### Prompt Engineering

El sistema usa dos tipos de prompts:

1. **Con contexto RAG:**
```python
prompt = f"""Eres un asistente inteligente. Responde basándote en el contexto.

CONTEXTO RELEVANTE:
{context_text}

PREGUNTA DEL USUARIO:
{user_message}

INSTRUCCIONES:
- Responde en español de forma clara y concisa
- Usa el contexto proporcionado
- Menciona las fuentes cuando sea relevante
- Sé conversacional y amigable
"""
```

2. **Sin contexto (fallback):**
```python
prompt = f"""Eres un asistente inteligente.

PREGUNTA DEL USUARIO:
{user_message}

NOTA: No tengo información específica en mi base de conocimiento.
"""
```

## Manejo de Errores

El sistema maneja varios escenarios:

1. **Ollama no disponible:**
```json
{"text": "⚠️ Ollama no está disponible. Por favor, asegúrate de que el servicio esté corriendo."}
```

2. **Embeddings no disponibles:**
- Responde sin contexto RAG usando Ollama directamente
- Muestra advertencia al usuario

3. **Sin contexto relevante:**
- Genera respuesta general
- Indica que no hay información específica

## Logs

El sistema imprime logs informativos:

```
🔍 Buscando contexto relevante para: ¿Qué es Vite?...
✓ Encontrados 5 chunks relevantes
  - Chunk 1: Vite | Next Generation Frontend Tooling... (similarity: 0.856)
  - Chunk 2: Vite | Next Generation Frontend Tooling... (similarity: 0.712)
  - Chunk 3: Vite | Next Generation Frontend Tooling... (similarity: 0.643)
🤖 Llamando a Ollama (modelo: gpt-oss:20b)...
✓ Respuesta generada (342 caracteres)
```

## Optimizaciones

### 1. Mejorar Relevancia

Aumentar el threshold de similitud para respuestas más precisas:

```python
if similarity > 0.4:  # Más estricto
```

### 2. Más Contexto

Recuperar más chunks si son necesarios:

```python
similar_chunks = await embedding_dao.search_similar(query_vector, limit=10)
```

### 3. Reranking

Implementar re-ranking de chunks con cross-encoder:

```python
# TODO: Agregar modelo de cross-encoder para reordenar resultados
from sentence_transformers import CrossEncoder
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
```

### 4. Caché de Respuestas

Cachear respuestas frecuentes:

```python
CHAT_CACHE: dict[str, str] = {}

# Antes de llamar a Ollama
cache_key = hashlib.md5(user_message.encode()).hexdigest()
if cache_key in CHAT_CACHE:
    return {"text": CHAT_CACHE[cache_key], "role": "ai"}
```

## Testing

### Test Manual

```bash
# Pregunta sobre contenido conocido
curl -X POST "http://localhost:5000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué es clean code?"}'

# Pregunta sobre contenido no disponible
curl -X POST "http://localhost:5000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Cuál es la capital de Francia?"}'
```

### Verificar Embeddings

```bash
curl http://localhost:5000/api/v1/embeddings/status
```

## Próximos Pasos

1. **Streaming de Respuestas**: Usar Server-Sent Events (SSE) para respuestas en tiempo real
2. **Historial de Conversación**: Almacenar contexto de conversación en tabla `chat_messages`
3. **Multi-turn Chat**: Mantener contexto entre múltiples mensajes
4. **Feedback Loop**: Permitir al usuario marcar respuestas como útiles/inútiles
5. **Citas de Fuentes**: Incluir referencias clickeables a los items originales
6. **Filtros por Tags**: Permitir acotar búsqueda por tags específicos

## Troubleshooting

### El chat no responde

1. Verificar que Ollama esté corriendo: `ollama list`
2. Verificar embeddings: `curl http://localhost:5000/api/v1/embeddings/status`
3. Revisar logs del servidor

### Respuestas sin contexto

1. Verificar que hay embeddings generados: `SELECT COUNT(*) FROM embeddings;`
2. Reducir threshold de similitud a 0.1
3. Aumentar número de chunks recuperados

### Ollama lento

1. Usar un modelo más ligero: `llama3.2` (~3.2B) en lugar de `gpt-oss:20b` (20B)
2. Reducir contexto enviado (menos chunks, cambiar `limit=5` a `limit=3`)
3. Implementar timeout y respuesta rápida
