import requests
from bs4 import BeautifulSoup


def get_webpage_text(url) -> str:
    """Obtiene el texto de una página web dada su URL."""
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    return ""

def load_file() -> str:
    pass

def load_pdf(pdf_file) -> str:
    pass

def load_youtube() -> str:
    pass

def load_audio() -> str:
    pass
