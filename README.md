# Smart Brain HackUDC26
En la era de la sobrecarga informativa, sufrimos de **Diógenes Digital**: guardamos miles de enlaces, archivos y vídeos que nunca volvemos a ver. El ruido constante nos impide enfocarnos en lo que realmente importa. **Smart Brain** nace para solucionar esto, convirtiéndose en tu agente personal que recuerda por ti, analiza tu contenido y te ayuda a alcanzar tus metas diarias.

---

## ✨ Características Principales

### 🧠 Cerebro AI (Local First)
- **Ingesta**: Procesa PDFs, documentos Office (Docx, ODT), hojas de cálculo (Excel, CSV) y contenido web (URLs/YouTube).
- **IA Local**: Resúmenes y análisis de sentimiento sin que tus datos salgan de tu red local.
- **Búsqueda**: Encuentra cualquier cosa en tu cerebro mediante palabras clave o búsqueda semántica.

### 📅 Ecosistema Conectado
- **Google Calendar Sync** (Trabajo futuro): Visualiza tu día de un vistazo con integración nativa unidireccional.
- **Asistente de Chat**: Conversa con tus archivos (RAG).
- **Extensión para compatible con navegadores basados en Chromium y Firefox**: Captura conocimiento mientras navegas con un solo clic.

---
## Trabajo futuro
Debido a las limitaciones del reto no se han podido implementar todas las funcionalidades propuestas, que nos hubieran gustado implementar:
- `Google Calendar Sync`: Para obtener un token de Calendar API se requiere una URL pública para la webapp, lo que se escapa de nuestra capacidad.
- `Almacenamiento de datos no estructurados`: Hasta ahora solo almacenamos ficheros como texto plano (PDF, DOCX, excel, PDF(OCR)), pero no se han almacenado datos no estructurados como imágenes, vídeos, etc. Respecto a videos y audio la principal limitación se encuentra a no disponer modelos `Speech2Text` que puedan convertir el audio en texto.


---

## 🛠️ Stack Tecnológico

### [Frontend](./frontend)
- **Framework**: React 19 + Vite 7
- **UI**: Vanilla CSS + DeepChat para conversaciones con IA
- **State Management**: React Hooks

### [Backend](./backend)
- **Framework**: FastAPI 0.134.0
- **Database**: PostgreSQL 16 + pgvector para búsqueda por similitud vectorial
- **LLM**: Ollama con modelos libres (`gpt-oss:20b` por defecto, `llama3.2` como alternativa)
  - Licencias: Apache 2.0 (software y pesos libres) y Llama Community License (parcialmente libre, con restricciones de usos permitidos y limitaciones en número de usuarios)
- **Embeddings**: sentence-transformers/all-MiniLM-L6-v2 (384 dimensiones, Licencia Apache 2.0)
- **RAG**: Retrieval-Augmented Generation con búsqueda semántica
- **Methodology**: Test Driven Development (TDD)

### [Extensión](./extension)
- **UI**: React para consistencia visual
- **Comunicación**: Chrome/Firefox Extension API (Manifest v3)
- **Cross-Browser**: Compatible with Chromium-based browsers and Firefox

### Infraestructura
- **Dependency Management**: uv (instalador rápido de paquetes Python)
- **Containerization**: Docker Compose para PostgreSQL + pgvector
- **API Architecture**: RESTful API con patrones async/await

---

## 🚀 Instalación y Configuración

### Requisitos Previos
- **Python 3.12+**
- **Node.js 22+**
- **Docker & Docker Compose** (para PostgreSQL)
- **Ollama** ([ollama.ai](https://ollama.ai)) - Asegúrate de que esté corriendo y tenga el modelo `llama3.2` descargado
  ```bash
  ollama pull llama3.2
  ```

### 1. Preparación de la Base de Datos
```bash
# Iniciar PostgreSQL con pgvector
docker-compose up -d

# Verificar que esté corriendo
docker ps | grep smartbrain-postgres
```

### 2. Preparación del Backend
```bash
cd backend

# Instalación automática (crea virtualenv e instala dependencias)
make setup && make install
source .venv/bin/activate

# Crear archivo .env con credenciales de base de datos
cat > .env << EOF
DATABASE_URL=postgresql://smartbrain_user:smartbrain_dev_password@localhost:5432/smartbrain
EOF

# Iniciar servidor FastAPI
make run
# O manualmente: uvicorn main:app --host 0.0.0.0 --port 5000 --reload
```

**El backend estará disponible en `http://localhost:5000`**

### 3. Preparación del Frontend
```bash
cd frontend

# Instalar dependencias
npm install

# Crear archivo .env con URL del backend
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5000/api/v1
EOF

# Iniciar servidor de desarrollo
npm run dev
```

**La aplicación estará disponible en `http://localhost:5173`**

### 4. Instalación de la Extensión (Opcional)
```bash
cd extension

# Construir la extensión
npm install
npm run build
```

**Instalar en navegador:**
1. Ve a `chrome://extensions/` (Chrome) o `about:debugging#/runtime/this-firefox` (Firefox)
2. Activa el "Modo desarrollador"
3. Haz clic en "Cargar descomprimida" y selecciona la carpeta `./extension/dist`

---

## 🔧 Solución de problemas

### Backend no se conecta a la base de datos
**Síntoma:** `ConnectionRefusedError` o `database "smartbrain" does not exist`

**Solución:**
```bash
# Verificar que PostgreSQL esté corriendo
docker ps | grep smartbrain-postgres

# Si no está corriendo, iniciarlo
docker-compose up -d

# Verificar la conexión
docker exec smartbrain-postgres psql -U smartbrain_user -d smartbrain -c "SELECT 1;"
```

### Error al generar embeddings: "No space left on device"
**Síntoma:** `No space left on device (os error 28)` al instalar sentence-transformers

**Solución:**
```bash
# Usar versión CPU de PyTorch (más ligera)
cd backend
uv pip install sentence-transformers --extra-index-url https://download.pytorch.org/whl/cpu
```

### Ollama no responde o modelo no encontrado
**Síntoma:** Chat devuelve errores o "Ollama is not available"

**Solución:**
```bash
# Verificar que Ollama esté corriendo
ollama list

# Descargar modelo si no existe
ollama pull llama3.2

# Verificar que el modelo responde
ollama run llama3.2 "Hello"
```

### Frontend no encuentra el backend
**Síntoma:** Errores de red o CORS en la consola del navegador

**Solución:**
```bash
# Verificar que backend esté corriendo
curl http://localhost:5000/api/v1/health

# Verificar el archivo .env del frontend
cat frontend/.env
# Debe contener: VITE_API_BASE_URL=http://localhost:5000/api/v1

# Reiniciar el servidor de desarrollo
cd frontend
npm run dev
```

### Embeddings no se generan automáticamente
**Síntoma:** Los items se agregan pero no se pueden buscar semánticamente

**Solución:**
```bash
# Verificar estado del worker de embeddings
curl http://localhost:5000/api/v1/embeddings/status

# Verificar logs del backend para mensajes como:
# "📊 Found X items to process for embeddings"

# Verificar manualmente en la base de datos
docker exec smartbrain-postgres psql -U smartbrain_user -d smartbrain -c "SELECT COUNT(*) FROM embeddings;"
```

### Dependencias de Python no se instalan
**Síntoma:** Errores al ejecutar `uv pip install`

**Solución:**
```bash
# Asegurarse de tener uv instalado
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar versión
uv --version

# Si uv no funciona, usar pip tradicional
pip install -r backend/requierements.txt
```

---

## 🤝 Contribuir
¿Quieres ayudarnos a resolver el problema de Diógenes Digital? Revisa nuestro [CONTRIBUTING.md](CONTRIBUTING.md) y únete a la revolución de la productividad.

---

## 📄 Licencia

**GNU Affero General Public License v3 (AGPL-3.0)**

Este proyecto es **software libre** bajo licencia AGPL v3. Consulta el archivo [LICENSE](LICENSE) para más detalles.

### ¿Qué significa?

- ✅ **Libertad de usar**: Puedes ejecutar Smart Brain para cualquier propósito
- ✅ **Libertad de estudiar**: Acceso total al código fuente
- ✅ **Libertad de modificar**: Puedes adaptar el código a tus necesidades
- ✅ **Libertad de compartir**: Puedes distribuir copias y mejoras
- ⚖️ **Restricción de copyleft**: Las modificaciones y servicios basados en este código **deben permanecer bajo AGPL v3**
- ⚖️ **Acceso a fuentes**: Si lo ofreces como servicio online, debes permitir a los usuarios acceder al código modificado

### Dependencias libres

Todas las dependencias principales son software libre:
- **Backend**: FastAPI, Ollama, sentence-transformers (Apache 2.0, BSD)
- **Frontend**: React, Vite (MIT)
- **Base de datos**: PostgreSQL (PostgreSQL License)

---
*Desarrollado en 36 horas por [Alejandro](https://github.com/alejandro2406), [Cosme](https://github.com/cosme8) y [Rubén](https://github.com/rubzip) para el HackUDC 2026 entre el 27 de Febrero de 2026 y el 1 de Marzo de 2026*.
