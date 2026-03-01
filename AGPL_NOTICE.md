# Aviso de Licencia AGPL v3

## Smart Brain - Licencia GNU Affero General Public License v3

Este proyecto y **todos sus archivos de código fuente** están bajo la licencia **GNU Affero General Public License v3 (AGPL-3.0)**.

### Archivos con Headers AGPL

Los siguientes archivos contienen headers explícitos de AGPL v3:

#### Backend (Python)
- `backend/main.py` - API principal con FastAPI
- `backend/models.py` - Modelos de datos
- `backend/utils/embeddings.py` - Generación de embeddings
- `backend/utils/loader.py` - Extracción de texto
- `backend/utils/cleaner.py` - Limpieza de texto
- `backend/database/embedding_dao.py` - Acceso a embeddings
- `backend/database/item_dao.py` - Acceso a items

#### Frontend (JavaScript/React)
- `frontend/src/App.jsx` - Componente principal
- `frontend/src/config.js` - Configuración de API
- `frontend/src/components/ChatInterface.jsx` - Chat con IA

### Qué significa AGPL v3?

**AGPL es un copyleft fuerte** que garantiza:

1. **Libertad de usuario final** ✓
   - Cualquiera puede usar, ejecutar y modificar el software

2. **Libertad de fuente** ✓
   - Acceso al código fuente
   - Derecho a redistribuir el código modificado

3. **Copyleft red** ⚠️
   - **Importante**: Si ofreces este software como servicio en línea (SaaS), debes:
     - Proporcionar acceso a tu código fuente modificado a los usuarios
     - Mantener la licencia AGPL v3
   - Cualquier trabajo derivado debe también ser AGPL v3

### Dependencias y sus licencias

Todas las dependencias son software libre:

| Componente | Librería | Licencia | Copyleft |
|-----------|----------|----------|----------|
| **Backend AI** | gpt-oss:20b, llama3.2 | Apache 2.0, Llama Community | ❌ No |
| **Embeddings** | sentence-transformers | Apache 2.0 | ❌ No |
| **Web Framework** | FastAPI | BSD 3-Clause | ❌ No |
| **Database** | PostgreSQL | PostgreSQL License | ❌ No |
| **Frontend** | React, Vite | MIT | ❌ No |

**Nota**: PyMuPDF (fitz) usa AGPL v3, lo que contribuye a la licencia general del proyecto.

### Para desarrolladores

Si haces un fork de este proyecto:

1. Mantén el archivo LICENSE en la raíz
2. Añade headers AGPL a archivos nuevos o modificados
3. Documenta cambios significativos
4. Si lo despliegas como servicio: expón el código fuente a usuarios
5. Redistribuye bajo AGPL v3

### Para usuarios/empresas

Si integras Smart Brain en tu infraestructura:

- ✅ Uso interno: sin restricciones
- ✅ Modificaciones internas: permitidas pero...
- ⚠️ Si lo ofreces como servicio: **debe ser AGPL v3**
- ⚠️ Si lo integras en un producto: **el producto debe ser AGPL v3**

Para usar bajo otras licencias, contacta con el equipo de desarrollo.

### Referencias

- [Licencia AGPL v3 completa](LICENSE)
- [GNU Affero General Public License](https://www.gnu.org/licenses/agpl-3.0.html)
- [¿Por qué AGPL?](https://www.gnu.org/licenses/why-affero-gpl.html)

---

**Última actualización**: 1 de Marzo de 2026
**Versión del proyecto**: Smart Brain HackUDC 2026
