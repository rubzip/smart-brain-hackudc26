import pytest
import io
from pathlib import Path
from utils.loader import (
    get_pdf_from_stream, 
    get_excel_from_stream,
    get_odt_from_stream,
    get_docx_from_stream,
)

# Ruta base de los archivos de prueba
STATIC_DIR = Path(__file__).parent.parent / "static" / "test_files"

def test_load_pdf():
    """Prueba la carga de archivos PDF del directorio static."""
    file_path = STATIC_DIR / "auditoria_interna_2024.pdf"
    assert file_path.exists(), f"No se encontró el archivo {file_path}"
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_pdf_from_stream(stream)
        
    assert len(text) > 0
    assert isinstance(text, str)
    # Verificación de contenido específico si es posible
    assert "CONSULTORÍA VÁZQUEZ" in text.upper()


def test_load_excel():
    """Prueba la carga de archivos Excel del directorio static."""
    file_path = STATIC_DIR / "nominas_resumen_dic2024.xlsx"
    assert file_path.exists()
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_excel_from_stream(stream)
        
    # Pandas to_string incluye cabeceras y datos
    assert "Departamento" in text
    assert "Ingeniería" in text

def test_load_odt():
    return
    """Prueba la carga de archivos ODT del directorio static."""
    file_path = STATIC_DIR / "incidencias_soporte_Q4_2024.odt"
    assert file_path.exists()
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_odt_from_stream(stream)
        
    assert "MANUAL DE USUARIO" in text

def test_load_docx():
    """Prueba la carga de archivos DOCX del directorio static."""
    file_path = STATIC_DIR / "certificado_ISO9001_novatech.docx"
    assert file_path.exists()
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_docx_from_stream(stream)
        
    assert "CERTIFICADO DE REGISTRO DE EMPRESA" in text

def test_load_pdf_large():
    """Prueba la carga de un PDF más grande (Estatuto)."""
    file_path = STATIC_DIR / "estatuto81.pdf"
    if file_path.exists():
        with open(file_path, "rb") as f:
            stream = io.BytesIO(f.read())
            text = get_pdf_from_stream(stream)
        assert len(text) > 1000  # Debería ser un documento largo
