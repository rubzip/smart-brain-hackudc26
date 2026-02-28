# 📓 Mini NotebookLM Backend

Una API construida con **FastAPI** diseñada para ingestar documentos, limpiar el texto extraído y generar embeddings vectoriales para sistemas RAG (Retrieval-Augmented Generation).

## 🚀 Características

* **Ingesta de documentos:** Extrae texto de diferentes formatos (PDF, TXT, etc.).
* **Limpieza semántica:** Procesamiento de texto (normalización Unicode, unión de guiones, limpieza de caracteres) optimizado para no perder contexto en la vectorización.
* **Generación de Embeddings:** Preparado para conectar con modelos de vectorización.
* **Backend rápido:** Construido sobre FastAPI para un rendimiento asíncrono y alta concurrencia.

---

## 🛠️ Requisitos Previos

Asegúrate de tener instalado [uv](https://github.com/astral-sh/uv), el gestor de paquetes y entornos ultrarrápido escrito en Rust.

Si no lo tienes, instálalo con:
```bash
uv venv --python 3.11
source venv/bin/activate
uv install
```

