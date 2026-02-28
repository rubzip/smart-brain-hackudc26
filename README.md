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

## Configuración de Google Calendar

Para que la sincronización de eventos funcione, es necesario configurar un proyecto en Google Cloud. Sigue estos pasos detallados:

1.  **Crear Proyecto**: Ve a [Google Cloud Console](https://console.cloud.google.com/) y crea un nuevo proyecto llamado `Smart Brain`.
2.  **Habilitar API**:
    *   En el buscador superior, escribe "Google Calendar API".
    *   Seleccion de la API y haz clic en **Habilitar**.
3.  **Configurar Pantalla de Consentimiento (OAuth Consent Screen)**:
    *   Ve a "API y servicios" > "Pantalla de consentimiento de OAuth".
    *   Selecciona "External" (si es para uso general) o "Internal" (si estás en una organización).
    *   Rellena los campos obligatorios (Nombre de la app, email de soporte).
    *   **Scopes**: Añade el scope `./auth/calendar.readonly`.
4.  **Crear Credenciales**:
    *   Ve a la pestaña "Credenciales".
    *   Haz clic en "Crear credenciales" > "ID de cliente de OAuth".
    *   **Tipo de aplicación**: Aplicación web.
    *   **Orígenes de JavaScript autorizados**: Añade `http://localhost:5175`.
5.  **Actualizar el Código**:
    *   Copia el **Client ID** generado.
    *   Pégalo en el archivo `frontend/src/App.jsx` en la constante `CLIENT_ID`:
      ```javascript
      const CLIENT_ID = 'TU_ID_AQUÍ.apps.googleusercontent.com';
      ```

> [!NOTE]
> La aplicación utiliza el flujo de **Google Identity Services (GIS)** para autenticación 100% frontend, lo que significa que no necesitas configurar un secreto de cliente ni un backend para que esto funcione localmente.

## Integración Frontend-Backend

El frontend está completamente conectado con el backend mediante los siguientes endpoints:

### Daily Plan (Tareas Diarias)
- **Endpoint**: `GET /api/v1/daily-plan`
- **Descripción**: Obtiene el plan diario generado por Ollama basado en los items almacenados
- **Funcionalidad**: Al cargar la app, el frontend obtiene automáticamente las tareas del backend cada 30 segundos
- **Fallback**: Si el backend no está disponible, muestra tareas por defecto

### Items Almacenados
El backend mantiene una API completa para gestionar items:
- `POST /api/v1/items/urls` - Guardar URL
- `POST /api/v1/items/local-files` - Guardar archivo local
- `POST /api/v1/items/files` - Subir archivo
- `GET /api/v1/items` - Listar items
- `GET /api/v1/items/{item_id}` - Detalle de item
- `DELETE /api/v1/items/{item_id}` - Eliminar item

> [!IMPORTANT]
> El backend debe estar corriendo en `http://localhost:5000` para que el frontend funcione correctamente. Puedes cambiar esta URL en la variable `API_BASE_URL` en `frontend/src/App.jsx`.

### How to run
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
```bash
cd frontend
npm install
npm run dev
```

### Extension
Carga la carpeta `extension` como una "Unpacked Extension" en `chrome://extensions/`.
