#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 Smart Brain Contributors
#
# This file is part of Smart Brain.
# See the LICENSE file at the project root for full terms.

import pytest

from utils.cleaner import clean_text

# --- TESTS ---

def test_invalid_inputs():
    """Prueba que los tipos no válidos devuelvan un string vacío."""
    assert clean_text(None) == ""
    assert clean_text(123) == ""
    assert clean_text(["texto"]) == ""
    assert clean_text({"clave": "valor"}) == ""

def test_empty_strings():
    """Prueba strings vacíos o compuestos solo de espacios."""
    assert clean_text("") == ""
    assert clean_text("    ") == ""
    assert clean_text("\n\n\t") == ""

def test_unicode_normalization():
    """Prueba la normalización NFKC (ej. ligaduras y caracteres compuestos)."""
    assert clean_text("clasiﬁcación y ﬁnanzas") == "clasificación y finanzas"
    assert clean_text("10 µm") == "10 μm"

def test_control_characters():
    """Prueba la eliminación de caracteres nulos e invisibles, conservando los saltos de línea."""
    messy_text = "Hola\x00Mundo\x08!\nAdiós\x1b"
    assert clean_text(messy_text) == "HolaMundo!\nAdiós"

def test_hyphenated_line_breaks():
    """Prueba la unión de palabras cortadas por un guion a final de línea."""
    assert clean_text("Esto es un embed-\nding.") == "Esto es un embedding."
    assert clean_text("inteli-\ngencia arti-\nficial") == "inteligencia artificial"
    # Un guion normal sin salto de línea NO debe unirse
    assert clean_text("costo-beneficio") == "costo-beneficio"

def test_line_break_standardization():
    """Prueba que 3 o más saltos de línea se reduzcan a exactamente 2."""
    assert clean_text("Párrafo 1\n\n\nPárrafo 2\n\n\n\n\nPárrafo 3") == "Párrafo 1\n\nPárrafo 2\n\nPárrafo 3"
    assert clean_text("Línea 1\nLínea 2") == "Línea 1\nLínea 2"

def test_whitespace_standardization():
    """Prueba que múltiples espacios o tabulaciones se reduzcan a un solo espacio."""
    assert clean_text("Muchos     espacios.") == "Muchos espacios."
    assert clean_text("Texto\tcon\ttabulaciones.") == "Texto con tabulaciones."
    assert clean_text("Mezcla \t  de   \t ambos.") == "Mezcla de ambos."

def test_edge_cleaning():
    """Prueba que se eliminen los espacios y saltos de línea al principio y al final."""
    assert clean_text("   Texto centrado   ") == "Texto centrado"
    assert clean_text("\n\nTexto con saltos\n\n") == "Texto con saltos"

def test_combined_real_world_scenario():
    """Prueba un texto 'sucio' extraído de un PDF que combina múltiples problemas."""
    dirty_pdf_text = (
        "\x00  \n\nEl análi-\nsis de \tda-\ntos   es\n\n\n\n"
        "fundamental para la eﬁciencia.\n  \t"
    )
    expected_clean_text = "El análisis de datos es\n\nfundamental para la eficiencia."
    assert clean_text(dirty_pdf_text) == expected_clean_text
