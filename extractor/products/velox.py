"""Produto: VELOX (próprio — Endereço do Atendimento)."""

import re

from ..helpers import make_record, extract_data, accent_insensitive, city_from_line
from ._base import set_assistencia, set_categoria, set_km_model_b


def _cidade_dentro(text, campo):
    """Cidade de um subcampo (ORIGEM/DESTINO) dentro de ENDEREÇO DO ATENDIMENTO."""
    match = re.search(accent_insensitive("ENDEREÇO DO ATENDIMENTO") + r"\s*[:=]?", text or "", re.IGNORECASE)
    if not match:
        return ""
    bloco = text[match.end():]
    sub = re.search(
        accent_insensitive(campo) + r"\s*[:=]\s*([^\n\r]+)", bloco, re.IGNORECASE
    )
    if not sub:
        return ""
    return city_from_line(sub.group(1)) or ""


def extract(text):
    record = make_record("VELOX")
    set_assistencia(record, text, "Protocolo")
    set_categoria(record, text, ["Servico Assistencia", "Tipo de Servico", "Servico"])
    record["ORIGEM"] = _cidade_dentro(text, "Origem")
    record["DESTINO"] = _cidade_dentro(text, "Destino")
    set_km_model_b(record, text)
    record["VALOR"] = _valor(text)
    record["DATA"] = extract_data(text)
    return record


def _valor(text):
    from ..helpers import extract_number

    value = extract_number(text, "VALOR TOTAL DO SERVICO")
    return value or ""
