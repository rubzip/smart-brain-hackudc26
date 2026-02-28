import pytest
from pathlib import Path
from utils.loader import get_pdf_from_stream

def test_get_pdf_with_real_file():
    """
    Prueba de integración: Lee un PDF real ('estatuto81.pdf') desde el disco local 
    y verifica que se extrae texto de él.
    """
    # 1. Definir la ruta al archivo. 
    # __file__ es la ruta de este script de test. 
    # Ajusta esto si tu PDF está en otra carpeta, ej: file_path = Path(__file__).parent / "data" / "estatuto81.pdf"
    file_path = Path(__file__).parent / "estatuto81.pdf" 
    
    # 2. Saltar el test si el archivo no existe en la máquina de quien ejecuta las pruebas.
    # Esto evita que el test falle si alguien más clona el repo y no tiene ese archivo específico.
    if not file_path.exists():
        pytest.skip(f"Archivo de prueba real no encontrado en {file_path}")
    

    # 3. Leer el archivo en modo binario ('rb')
    with open(file_path, "rb") as f:
        pdf_bytes = f.read()

    # 4. Extraer el texto
    extracted_text = get_pdf_from_stream(pdf_bytes)
    print(len(extracted_text))  # Imprime la longitud del texto extraído para verificar que no esté vacío
    print(extracted_text[:500])  # Imprime los primeros 500 caracteres para inspección visual rápida

    # 5. Aserciones básicas para comprobar que funcionó
    # Verificamos que no esté vacío
    assert len(extracted_text) > 0, "El texto extraído del PDF real está vacío."
    
    # Verificamos que sea un string
    assert isinstance(extracted_text, str)

    # OPCIONAL: Si sabes que el Estatuto contiene una palabra específica (ej. "Artículo", "Estatuto", "Galicia"),
    # puedes añadir una aserción específica para comprobar que la extracción es correcta:
    # assert "Artículo" in extracted_text 
    # assert "Galicia" in extracted_text

if __name__ == "__main__":
    test_get_pdf_with_real_file()