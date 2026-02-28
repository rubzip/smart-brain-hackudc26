# Smart Brain HackUDC26
En la era de la sobrecarga informativa, sufrimos de **Diógenes Digital**: guardamos miles de enlaces, archivos y vídeos que nunca volvemos a ver. El ruido constante nos impide enfocarnos en lo que realmente importa. **Smart Brain** nace para solucionar esto, convirtiéndose en tu agente personal que recuerda por ti, analiza tu contenido y te ayuda a alcanzar tus metas diarias.

---

## ✨ Características Principales

### 🧠 Cerebro AI (Local First)
- **Ingesta**: Procesa PDFs, documentos Office (Docx, ODT), hojas de cálculo (Excel, CSV) y contenido web (URLs/YouTube).
- **IA Local**: Resúmenes y análisis de sentimiento sin que tus datos salgan de tu red local.
- **Búsqueda**: Encuentra cualquier cosa en tu cerebro mediante palabras clave o búsqueda semántica.

### 📅 Ecosistema Conectado
- **Google Calendar Sync** (Future work): Visualiza tu día a un vistazo con integración nativa unidireccional.
- **Asistente de Chat**: Conversa con tus archivos (RAG).
- **Extensión para compatible con navegadores basados en Chromium y Firefox**: Captura conocimiento mientras navegas con un solo clic.

---

## 🛠️ Stack Tecnológico

### [Frontend](./frontend)
- **Framework**: React + Vite + Vanilla CSS

### [Backend](./backend)
- **Framework**: FastAPI
- **LLM**: Ollama (Llama 3 (**Pesos abiertos**))
- **Metodología**: Test Driven Development (TDD)

### [Extensión](./extension)
- **UI**: React para coherencia visual total.
- **Comunicación**: Chrome/Firefox Extension API para captura de metadatos en tiempo real.

---

## 🚀 Instalación y Configuración

### 1. Preparación del Backend
```bash
cd backend
# Configuración automática del entorno
make setup && make install
source .venv/bin/activate
# Iniciar servidor
make run
```
*Asegúrate de tener [Ollama](https://ollama.ai) instalado y corriendo localmente.*

### 2. Preparación del Frontend
```bash
cd frontend
npm install
npm run dev
```
*La aplicación estará disponible en `http://localhost:5175`.*

### 3. Instalación de la Extensión
0. *(Opcional)* `cd extension && npm run build`
1. Ve a `chrome://extensions/` en tu navegador.
2. Activa el "Modo desarrollador".
3. Haz clic en "Cargar descomprimida" y selecciona la carpeta `./extension/dist`.

---

## 🤝 Contribuir
¿Quieres ayudarnos a resolver el problema de Diógenes Digital? Revisa nuestro [CONTRIBUTING.md](CONTRIBUTING.md) y únete a la revolución de la productividad.

---

## 📄 Licencia
Este proyecto está bajo la Licencia MIT. Para más detalles, consulta el archivo [LICENSE](LICENSE).

---
*Desarrollado en 36 horas por [https://github.com/alejandro2406](Alejandro), [https://github.com/cosme8](Cosme) y [https://github.com/rubzip](Rubén) para el HackUDC 2026 durante el 27 de Febrero de 2026 y el 1 de Marzo de 2026*.
