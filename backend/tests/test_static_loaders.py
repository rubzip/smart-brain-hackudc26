import pytest
import io
from pathlib import Path
from utils.loader import (
    get_pdf_from_stream, 
    get_txt_from_stream, 
    get_csv_from_stream
)

# Ruta base de los archivos de prueba
STATIC_DIR = Path(__file__).parent.parent / "static" / "test_files"

def test_load_pdf():
    """Prueba la carga de archivos PDF del directorio static."""
    file_path = STATIC_DIR / "acta_constitucion_novatech.pdf"
    assert file_path.exists(), f"No se encontró el archivo {file_path}"
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_pdf_from_stream(stream)
        
    assert len(text) > 0
    assert isinstance(text, str)
    # Verificación de contenido específico si es posible
    assert "NOVATECH" in text.upper()

def test_load_txt():
    """Prueba la carga de archivos TXT del directorio static."""
    file_path = STATIC_DIR / "acta_reunion_aurora_20250110.txt"
    assert file_path.exists()
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_txt_from_stream(stream)
        
    assert "PROYECTO AURORA" in text
    assert "Carlos Méndez" in text

def test_load_csv():
    """Prueba la carga de archivos CSV del directorio static."""
    file_path = STATIC_DIR / "incidencias_soporte_Q4_2024.csv"
    assert file_path.exists()
    
    with open(file_path, "rb") as f:
        stream = io.BytesIO(f.read())
        text = get_csv_from_stream(stream)
        
    # Pandas to_string incluye cabeceras y datos
    assert "id_ticket" in text
    assert "TK-2024-0401" in text

def test_load_pdf_large():
    """Prueba la carga de un PDF más grande (Estatuto)."""
    file_path = STATIC_DIR / "estatuto81.pdf"
    if file_path.exists():
        with open(file_path, "rb") as f:
            stream = io.BytesIO(f.read())
            text = get_pdf_from_stream(stream)
        assert len(text) > 1000  # Debería ser un documento largo
