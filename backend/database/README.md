# Database Setup

## PostgreSQL con pgvector

### Instalación de PostgreSQL y pgvector

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Instalar pgvector
sudo apt install postgresql-15-pgvector

# O compilar desde source
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Crear base de datos

```bash
sudo -u postgres psql

CREATE DATABASE smartbrain;
CREATE USER smartbrain_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE smartbrain TO smartbrain_user;
\q
```

### Aplicar schema

```bash
psql -U smartbrain_user -d smartbrain -f schemas/init.sql
```

### Variables de entorno

Crear archivo `.env` en la raíz del backend:

```env
DATABASE_URL=postgresql://smartbrain_user:your_password@localhost:5432/smartbrain
```

### Dependencias Python

```bash
pip install asyncpg pgvector
```

O añadir a `requirements.txt`:
```
asyncpg==0.29.0
pgvector==0.2.4
```

## Estructura de carpetas

```
backend/
├── database/
│   ├── __init__.py          # Package marker
│   ├── connection.py        # Pool de conexiones asyncpg
│   └── models.py            # Modelos Pydantic y queries
├── schemas/
│   ├── init.sql             # Schema inicial con pgvector
│   └── migrations/          # Migraciones futuras
│       └── README.md
```

## Uso en FastAPI

```python
from database.connection import db, get_db_connection
from database.models import ItemQueries

@app.on_event("startup")
async def startup():
    await db.connect()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/items/{item_id}")
async def get_item(item_id: UUID, conn = Depends(get_db_connection)):
    item = await ItemQueries.get_item(conn, item_id)
    return item
```

## Vector Embeddings

El schema soporta embeddings de 384 dimensiones (all-MiniLM-L6-v2). 
Para otros modelos, modificar:

```sql
embedding vector(768)  -- Para sentence-transformers más grandes
```

## Búsqueda vectorial

```python
from database.models import EmbeddingQueries

# Generar embedding de la consulta
query_embedding = model.encode("texto de búsqueda")

# Buscar chunks similares
results = await EmbeddingQueries.search_similar(conn, query_embedding.tolist(), limit=5)
```
