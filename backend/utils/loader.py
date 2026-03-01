#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text extraction utilities from various file formats.

Copyright (C) 2026 Smart Brain Contributors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
import requests
import io 
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import pandas as pd


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


def get_excel_from_stream(stream: io.BytesIO) -> str:
    try:
        stream.seek(0)
        df = pd.read_excel(stream)
        return df.to_string()
    except Exception as e:
        raise RuntimeError(f"Error al procesar Excel: {e}") 

import yt_dlp
import io
import sys

def get_audio_bytes(video_id) -> bytes:
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    # Configuramos para capturar el flujo
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'outtmpl': '-',  # Salida a stdout
        'logtostderr': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # En lugar de download(), usamos extract_info
        # Pero para obtener los bytes reales de forma limpia:
        info = ydl.extract_info(url, download=False)
        audio_url = info['url']
        
        # Aquí es donde 'yt-dlp' brilla: te da la URL directa del stream
        return audio_url # Esta URL la puedes pasar a un transcriptor directamente

def load_audio() -> str:
    pass
