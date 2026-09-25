"""Funções comuns reutilizadas pelos módulos de produto.

Cada produto tem peculiaridades, mas vários compartilham os mesmos padrões de
extração (Portal de Assistência, Plataforma Operacional, Laudo Digital). Estas
helpers evitam duplicação e mantêm os módulos de produto enxutos e fáceis de
ajustar.
"""

import re

from ..helpers import (
    accent_insensitive,
    city_from_line,
    city_in_block,
    extract_city_field,
    extract_number,
    labeled_value,
)
from ..category_mapper import normalize_category
from .. import km_calculator


def set_assistencia(record, text, labels):
    """Define ASSISTENCIA a partir do primeiro rótulo encontrado."""
    record["ASSISTENCIA"] = labeled_value(text, labels) or ""


def set_categoria(record, text, label="Servico"):
    """Define CATEGORIA a partir de um campo rotulado, adicionando OBS se preciso."""
    categoria, obs = normalize_category(labeled_value(text, label))
    if categoria:
        record["CATEGORIA"] = categoria
    if obs:
        record["OBS"].append(obs)


def set_categoria_raw(record, raw):
    """Define CATEGORIA a partir de uma string bruta."""
    categoria, obs = normalize_category(raw)
    if categoria:
        record["CATEGORIA"] = categoria
    if obs:
        record["OBS"].append(obs)


def set_portal_cities(record, text):
    """Origem = 1º campo Cidade, Destino = 2º campo Cidade (Portal de Assistência)."""
    record["ORIGEM"] = extract_city_field(text, 1) or ""
    record["DESTINO"] = extract_city_field(text, 2) or ""


def set_block_cities(record, text):
    """Origem/Destino a partir de blocos rotulados ``Origem`` e ``Destino``."""
    record["ORIGEM"] = city_in_block(text, "Origem") or ""
    record["DESTINO"] = city_in_block(text, "Destino") or ""


def set_locais_cities(record, text):
    """BRADESCO/FCA: ``LOCAIS DO ATENDIMENTO`` com endereços (1) e (2)."""
    block = text or ""
    match = re.search(accent_insensitive("LOCAIS DO ATENDIMENTO"), text or "", re.IGNORECASE)
    if match:
        block = text[match.end():]
    origem = destino = ""
    for line in block.splitlines()[:12]:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"\(\s*1\s*\)", stripped):
            origem = city_from_line(stripped) or ""
        elif re.match(r"\(\s*2\s*\)", stripped):
            destino = city_from_line(stripped) or ""
    record["ORIGEM"] = origem
    record["DESTINO"] = destino


def set_km_model_a(record, text):
    """Modelo A: KM somente se explícito."""
    km, obs = km_calculator.model_a(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_km_model_b(record, text):
    """Modelo B: Percurso Total com prioridades."""
    km, obs = km_calculator.model_b(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_km_model_c(record, text):
    """Modelo C: 40 + deslocamento + excedente."""
    km, obs = km_calculator.model_c(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_valor(record, text, labels=("VALOR TOTAL DO SERVICO", "VALOR TOTAL", "VALOR")):
    """Define VALOR a partir de um rótulo de valor explícito."""
    for label in labels:
        value = extract_number(text, label)
        if value is not None:
            record["VALOR"] = value
            return
    record["VALOR"] = ""
