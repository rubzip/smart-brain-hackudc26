#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Embedding generation utilities using sentence-transformers.

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
import asyncio
from typing import Optional
from functools import lru_cache

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None


@lru_cache(maxsize=1)
def get_embedding_model() -> Optional[SentenceTransformer]:
    """Get or initialize the embedding model (cached)."""
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("⚠️  sentence-transformers not available, embeddings disabled")
        return None
    
    try:
        print("📦 Loading embedding model: all-MiniLM-L6-v2 (384 dimensions)...")
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        print("✓ Embedding model loaded")
        return model
    except Exception as e:
        print(f"❌ Failed to load embedding model: {e}")
        return None


def chunk_text(text: str, max_chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= max_chunk_size:
        return [text] if text else []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_chunk_size
        
        # If not the last chunk, try to break at a sentence or word boundary
        if end < len(text):
            # Look for sentence endings
            for delimiter in ['. ', '.\n', '! ', '?\n', '? ', '\n\n']:
                last_delim = text[start:end].rfind(delimiter)
                if last_delim > max_chunk_size * 0.5:  # At least 50% into chunk
                    end = start + last_delim + len(delimiter)
                    break
            else:
                # Fallback to word boundary
                last_space = text[start:end].rfind(' ')
                if last_space > max_chunk_size * 0.5:
                    end = start + last_space
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        # Move start forward, accounting for overlap
        start = end - overlap
        if start >= len(text):
            break
    
    return chunks


async def generate_embeddings_for_text(text: str, model: Optional[SentenceTransformer] = None) -> list[tuple[str, list[float]]]:
    """
    Generate embeddings for text by chunking and encoding.
    
    Args:
        text: Text to embed
        model: Optional pre-loaded model, otherwise will load default
    
    Returns:
        List of (chunk_text, embedding_vector) tuples
    """
    if not text:
        return []
    
    if model is None:
        model = get_embedding_model()
    
    if model is None:
        print("⚠️  Embedding model not available")
        return []
    
    # Chunk the text
    chunks = chunk_text(text, max_chunk_size=500, overlap=50)
    
    if not chunks:
        return []
    
    print(f"📝 Generating embeddings for {len(chunks)} chunks...")
    
    # Generate embeddings in a thread pool (sentence-transformers is CPU-bound)
    loop = asyncio.get_event_loop()
    embeddings = await loop.run_in_executor(None, model.encode, chunks)
    
    # Convert numpy arrays to lists
    result = []
    for chunk, embedding in zip(chunks, embeddings):
        result.append((chunk, embedding.tolist()))
    
    return result
