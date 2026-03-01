#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Text cleaning and normalization utilities.

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
import re
import unicodedata

def clean_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    # 1. Normalización Unicode (NFKC)
    # Convierte caracteres raros, ligaduras (ej. 'ﬁ' -> 'fi') y comillas tipográficas a texto estándar.
    text = unicodedata.normalize("NFKC", text)

    # 2. Eliminar caracteres de control y nulos (excepto \n)
    # Los PDFs y archivos de Word suelen traer caracteres no imprimibles que confunden al tokenizador.
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # 3. Unir palabras separadas por guiones a final de línea (típico de PDFs)
    # Ej: "embeb-\nding" -> "embedding"
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)

    # 4. Estandarizar saltos de línea
    # Convertimos 3 o más saltos de línea consecutivos en solo 2 (para mantener la separación de párrafos).
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 5. Estandarizar espacios en blanco
    # Convertimos múltiples espacios o tabulaciones en un solo espacio.
    text = re.sub(r'[ \t]+', ' ', text)

    # 6. Limpieza final de bordes
    text = text.strip()

    return text