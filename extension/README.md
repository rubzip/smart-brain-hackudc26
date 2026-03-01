# 🧠 Smart Brain Link Saver

Extensión minimalista multiplataforma para categorizar y guardar enlaces rápidamente. Funciona en **Chrome** y **Firefox**.

## 🚀 Configuración e instalación

Sigue estos pasos para activar la extensión en tu navegador:

### 1. Construir el proyecto
Asegúrate de tener dependencias instaladas y ejecuta el build:
```bash
cd extension
npm install
npm run build
```

### 2. Cargar en Chrome
1. Abre Google Chrome y entra en `chrome://extensions/`.
2. Activa el **Modo desarrollador** (arriba a la derecha).
3. Pulsa **Cargar descomprimida**.
4. Selecciona la carpeta **`extension/dist`** generada en el paso anterior.

### 3. Cargar en Firefox
1. Abre Firefox y entra en `about:debugging#/runtime/this-firefox`.
2. Pulsa **Cargar complemento temporal...**.
3. Ve a la carpeta **`extension/dist`** y selecciona el archivo **`manifest.json`**.

---

## 🛠️ Cómo funciona

- **Captura automática**: detecta automáticamente el título y la URL de la pestaña actual.
- **Categorías con emojis**:
  - 💼 **Work**: enlaces profesionales o de trabajo.
  - 🏠 **Personal**: enlaces personales e intereses.
  - ⏳ **Watch Later**: artículos o videos para revisar luego.
- **Guardado**: al pulsar "Save to Brain" envía un POST a `http://localhost:5000/api/save` (configurable en `App.jsx`).

## ⚡ Desarrollo

Si quieres modificar diseño o funcionalidad:
1. Edita archivos en `src/`.
2. Ejecuta `npm run build` para actualizar `dist`.
3. En `chrome://extensions/`, pulsa el icono **Actualizar** (flecha circular) de la tarjeta de la extensión.
