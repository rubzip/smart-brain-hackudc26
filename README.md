# Smart Brain HackUDC26

En nuestro dia a dia, vivimos con muchas interacciones, problemas. El diogenes digital dice que el ..% de enlaces que guardamos nunca son vistos. El sindrome de ... dice que las personas no pueden desconectar porque tienen la sensacion de que se estan olvidando de algo importante. 

Es por esto que hemos implementado el Smart Brain, un sistema que hace que los humanos puedan centrarse en lo que realmente importa y tu agente en recordar todo lo que necesites. 

Entre las multiples funcionalidades que ofrece el Smart Brain, destacan:
 * Trackeo de propósitos diarios. Establece unos propósitos diarios y Smart Brain te ayudara a alcanzarlos.
 * Trackeo de emociones.
 * Recordatorio de tareas.

## Dependencias y Stack Tecnológico

El proyecto está dividido en tres componentes principales, cada uno con sus propias herramientas especializadas:

### 🎨 Frontend (Dashboard)
Desarrollado con **React + Vite** para una experiencia de usuario rápida y fluida.
*   **Recharts**: Para la visualización de datos y analíticas semanales.
*   **Canvas-confetti**: Añade efectos de celebración (gamificación) al completar tareas.
*   **Google Identity Services**: Integración directa con Google Calendar para sincronización de eventos.

### ⚙️ Backend (Cerebro)
Una API robusta construida con **FastAPI** que gestiona toda la lógica de procesamiento.
*   **Ollama**: Integración con modelos de lenguaje locales (LLMs) para el análisis de contenido.
*   **PyMuPDF (fitz)**: Extracción de texto y procesamiento de archivos **PDF**.
*   **python-docx / odfpy**: Soporte completo para documentos de **Office** y **OpenDocument**.
*   **Pandas / OpenPyXL**: Procesamiento avanzado de datos estructurados y hojas de cálculo (**Excel/CSV**).
*   **BeautifulSoup4 / Requests**: Web scraping para la ingesta de contenido desde cualquier URL.
*   **PyTest**: Batería de pruebas intensiva para asegurar la fiabilidad del procesamiento (TDD).

### 🧩 Extensión (Capturador)
Una extensión de navegador para capturar contenido al vuelo.
*   **Vite + React**: Mantiene la coherencia visual con la webapp principal.
*   **Content Scripts**: Para la extracción de metadatos (URLs, títulos, marcadores) de las pestañas activas.

## Arquitectura monolítica

## Test Driven Development
Hemos utilizado una metodologia TDD para el desarrollo de la aplicacion. Todas las utilidades del backend se han evaluado sobre una batería intensiva de pruebas unitarias.

## Formatos Aceptados
 * Texto plano
 * Webpages
 * PDF
 * Office like (Odt, Docx, Xlsx)
 * Video / audio ????
 * YouTube ??? 

## How to run
### Backend
```bash
cd backend
```

```bash
make setup && make install
source .venv/bin/activate
```

```bash
make run
```

### Frontend

### Extension
