"""Produto: MOVIDA (Plataforma Operacional)."""

import re

from ..helpers import make_record, extract_data, labeled_value
from ._base import set_categoria, set_block_cities, set_km_model_b, set_valor


def _assistencia(text):
    value = labeled_value(text, ["Protocolo", "Atendimento", "Numero do Atendimento"])
    if value:
        return value
    # Fallback: primeiro número "grande" no topo da mensagem.
    match = re.search(r"\b\d{4,}\b", text or "")
    return match.group(0) if match else ""


def extract(text):
    record = make_record("MOVIDA")
    record["ASSISTENCIA"] = _assistencia(text)
    set_categoria(record, text, ["Tipo de Servico", "Servico"])
    set_block_cities(record, text)
    set_km_model_b(record, text)
    set_valor(record, text, ("VALOR TOTAL",))
    record["DATA"] = extract_data(text)
    return record
