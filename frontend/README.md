# Frontend de Smart Brain

Aplicación React moderna construida con Vite para el asistente de productividad Smart Brain.

## Stack tecnológico

- **React 19.2.0** - React con funcionalidades concurrentes
- **Vite 7.3.1** - Tooling de frontend rápido
- **Node.js 22+** - Runtime de JavaScript
- **DeepChat** - Componente de interfaz de chat con IA
- **Vanilla CSS** - Estilos personalizados con variables CSS

## Inicio rápido

```bash
# Instalar dependencias
npm install

# Crear archivo .env
cat > .env << EOF
VITE_API_BASE_URL=http://localhost:5000/api/v1
EOF

# Iniciar servidor de desarrollo
npm run dev
```

La app estará disponible en `http://localhost:5173`.

## Estructura del proyecto

```
frontend/
├── src/
│   ├── components/        # Componentes React
│   │   ├── AddItem.jsx       # Panel de subida de archivos/URLs
│   │   ├── ChatInterface.jsx # Chat con IA y RAG
│   │   ├── Header.jsx        # Navegación superior
│   │   ├── MoodDock.jsx      # Seguimiento de estado de ánimo
│   │   ├── Schedule.jsx      # Integración de calendario
│   │   ├── SearchTool.jsx    # Búsqueda global
│   │   ├── StatsModal.jsx    # Modal de analíticas
│   │   ├── Suggestions.jsx   # Carrusel de contenido
│   │   └── TodoList.jsx      # Tareas diarias
│   ├── config.js          # Configuración de API
│   ├── App.jsx            # Aplicación principal
│   ├── App.css            # Estilos globales
│   └── main.jsx           # Punto de entrada
├── public/                # Activos estáticos
├── .env                   # Variables de entorno
└── vite.config.js         # Configuración de Vite
```

## Funcionalidades

### 📝 Objetivos diarios
- Tareas generadas automáticamente desde el contenido almacenado
- Seguimiento de progreso en tiempo real con animaciones
- Actualizaciones optimistas de UI con estrategia merge
- Spinner con delay de 1.2s para respuestas lentas

### 🗂️ Gestión de contenido
- **Añadir ítems**: URLs, videos de YouTube, archivos (PDF, DOCX, Excel, TXT, CSV)
- **Buscar**: búsqueda de texto completo con filtrado por etiquetas
- **Carrusel**: navegación por contenido con paginación

### 💬 Chat con IA
- **Con RAG**: búsqueda semántica sobre contenido guardado
- **Con contexto**: menciona fuentes relevantes
- **En tiempo real**: respuestas desde Ollama
- **Persistente**: mantiene el contexto conversacional

### 😊 Seguimiento emocional
- Registro diario de estado (Happy, Tired, Sad)
- Feedback contextual y sugerencias
- Sistema de recompensa visual

### 📅 Integración de agenda
- Sincronización con Google Calendar (trabajo futuro)
- Vista de eventos del día
- Sección rápida de "Up Next"

## Configuración

### Variables de entorno

Crea un archivo `.env` en la carpeta frontend:

```env
# URL de la API backend
VITE_API_BASE_URL=http://localhost:5000/api/v1
```

### Configuración de API

La URL base de la API está centralizada en `src/config.js`:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';
export { API_BASE_URL };
```

Todos los componentes importan desde ese archivo:
```javascript
import { API_BASE_URL } from '../config';
```

## Desarrollo

### Scripts disponibles

- **`npm run dev`** - Inicia servidor de desarrollo con HMR
- **`npm run build`** - Genera build de producción
- **`npm run preview`** - Previsualiza el build de producción
- **`npm run lint`** - Ejecuta ESLint

### Hot Module Replacement (HMR)

Vite ofrece HMR rápido para feedback inmediato durante desarrollo. Cambios en componentes React, CSS o configuración se aplican sin recarga completa.

## Solución de problemas

### Puerto en uso

**Problema:** `Port 5173 is already in use`

**Solución:**
```bash
# Matar proceso en puerto 5173
lsof -i :5173 | grep LISTEN | awk '{print $2}' | xargs kill -9

# O usar otro puerto
npm run dev -- --port 5174
```

### No conecta con el backend

**Problema:** errores de red o CORS en la consola del navegador

**Solución:**
```bash
# 1. Verificar backend
curl http://localhost:5000/api/v1/health

# 2. Revisar .env
cat .env
# Debe contener: VITE_API_BASE_URL=http://localhost:5000/api/v1

# 3. Reiniciar servidor de desarrollo
npm run dev
```

### Error en build

**Problema:** errores al ejecutar `npm run build`

**Solución:**
```bash
# Limpiar y reconstruir
rm -rf node_modules/.vite dist
npm install
npm run build

# Revisar errores de lint
npm run lint
```

### Variables de entorno no funcionan

**Problema:** `import.meta.env.VITE_API_BASE_URL` aparece como undefined

**Solución:**
- Las variables deben empezar por `VITE_`
- Reiniciar `npm run dev` tras cambiar `.env`
- Verificar que el archivo sea exactamente `.env`
- Comprobar que `.env` está en la raíz de frontend

## Compatibilidad de navegadores

- **Chrome/Edge**: soporte completo (2 últimas versiones)
- **Firefox**: soporte completo (2 últimas versiones)

## Recursos adicionales

- **[Documentación de Vite](https://vite.dev)**
- **[Documentación de React](https://react.dev)**
- **[DeepChat](https://deepchat.dev)** - Componente de chat con IA
