import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

def get_pdf(pdf_bytes: bytes) -> str:
    if not isinstance(pdf_bytes, bytes):
        raise TypeError("El documento debe ser proporcionado como bytes.")

    try:
        # Abrir el documento directamente desde la memoria
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        
        extracted_text = []
        
        # Iterar sobre las páginas y extraer el texto
        for page in doc:
            text = page.get_text("text")
            if text:
                extracted_text.append(text)
                
        doc.close()
        
        # Unir todas las páginas preservando la separación espacial
        return "\n\n".join(extracted_text)
        
    except Exception as e:
        raise RuntimeError(f"Error al procesar el PDF desde memoria: {e}")


def get_webpage_text(url) -> str:
    """Obtiene el texto de una página web dada su URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    raise ...

def load_file() -> str:
    pass


def load_youtube() -> str:
    pass

def load_audio() -> str:
    pass
