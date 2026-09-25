"""Produto: SANTANDER (Portal de Assistência — blocos Origem/Destino)."""

import re

from ..helpers import (
    make_record,
    extract_data,
    accent_insensitive,
    city_in_block,
)
from ._base import set_assistencia, set_categoria, set_km_model_c


def _origem(text):
    cidade = city_in_block(text, "Origem")
    if cidade:
        return cidade
    # Fallback: se o bloco Origem só indicar a base do prestador.
    match = re.search(accent_insensitive("Origem") + r"\s*[:=]?", text or "", re.IGNORECASE)
    if match:
        bloco = "\n".join(text[match.end():].splitlines()[:5])
        if re.search(accent_insensitive("BASE DO PRESTADOR"), bloco, re.IGNORECASE):
            return "BASE DO PRESTADOR"
    return ""


def extract(text):
    record = make_record("SANTANDER")
    set_assistencia(record, text, "Assistencia")
    set_categoria(record, text, "Servico")
    record["ORIGEM"] = _origem(text)
    record["DESTINO"] = city_in_block(text, "Destino") or ""
    set_km_model_c(record, text)
    record["VALOR"] = ""
    record["DATA"] = extract_data(text)
    return record
