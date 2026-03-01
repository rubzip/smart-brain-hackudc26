#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Smart Brain Contributors
#
# This file is part of Smart Brain.
# Smart Brain is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# See the LICENSE file at the project root for full terms.

import ollama
from typing import List

def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Divida un texto en trozos (chunks) de tamaño fijo con solapamiento.
    """
    if not text:
        return []
    
    words = text.split()
    
    # Si el texto es muy corto, un solo chunk
    if len(words) <= chunk_size:
        return [text]
        
    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        # Avanzar el inicio restando el solapamiento
        start += (chunk_size - overlap)
        if end >= len(words):
            break
            
    return chunks

def get_embedding(text: str, model: str = "all-minilm") -> List[float]:
    """
    Calcula el embedding de un texto usando Ollama.
    Por defecto usa all-minilm (384 dimensiones) para coincidir con la DB.
    """
    try:
        response = ollama.embeddings(model=model, prompt=text)
        return response["embedding"]
    except Exception as e:
        print(f"Error calculando embedding: {e}")
        return []
