"""Produto: UNIVERSO AGV (próprio — Endereço de Acionamento)."""

import re

from ..helpers import make_record, extract_data, accent_insensitive, city_from_line
from ._base import set_assistencia, set_categoria, set_km_model_b, set_valor


def _cidade_dentro(text, campo):
    """Cidade de um subcampo (Origem/Destino) dentro de Endereço de Acionamento."""
    match = re.search(accent_insensitive("Endereco de Acionamento") + r"\s*[:=]?", text or "", re.IGNORECASE)
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
    record = make_record("UNIVERSO AGV")
    set_assistencia(record, text, "Protocolo")
    set_categoria(record, text, ["Tipo de Servico", "Servico"])
    record["ORIGEM"] = _cidade_dentro(text, "Origem")
    record["DESTINO"] = _cidade_dentro(text, "Destino")
    set_km_model_b(record, text)
    set_valor(record, text, ("VALOR",))
    record["DATA"] = extract_data(text)
    return record
