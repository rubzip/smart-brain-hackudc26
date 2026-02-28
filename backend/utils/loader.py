import requests
import io 
from bs4 import BeautifulSoup
import fitz  # PyMuPDF

def get_pdf_from_stream(stream: io.BytesIO) -> str:
    try:
        # Abrir el documento directamente desde la memoria
        doc = fitz.open(stream=stream, filetype="pdf")
        
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


def get_webpage_text(url: str) -> str:
    """Obtiene el texto de una página web dada su URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    raise ...

# pip install python-docx
import docx
import io

def get_docx_from_stream(stream: io.BytesIO) -> str:
    try:
        # Aseguramos que el puntero esté al inicio del "archivo"
        stream.seek(0)
        doc = docx.Document(stream)
        full_text = [para.text for para in doc.paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        raise RuntimeError(f"Error al procesar DOCX: {e}")

# pip install odfpy
from odf import text, teletype
from odf.opendocument import load
import io

def get_odt_from_stream(stream: io.BytesIO) -> str:
    try:
        stream.seek(0)
        textdoc = load(stream)
        all_paragraphs = textdoc.getElementsByType(text.P)
        full_text = [teletype.extractText(p) for p in all_paragraphs]
        return "\n".join(full_text)
    except Exception as e:
        raise RuntimeError(f"Error al procesar ODT: {e}")


def load_file() -> str:
    pass


def load_youtube() -> str:
    pass

def load_audio() -> str:
    pass
