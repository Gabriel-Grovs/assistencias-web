"""Produto: FCA FIAT (Plataforma Operacional)."""

from ..helpers import make_record, extract_data
from ._base import (
    set_assistencia,
    set_categoria,
    set_locais_cities,
    set_block_cities,
    set_km_model_a,
    set_valor,
)


def extract(text):
    record = make_record("FCA FIAT")
    set_assistencia(record, text, ["# Servico", "Assistencia"])
    set_categoria(record, text, ["Tipo de Servico", "Servico"])
    
    set_locais_cities(record, text)
    if not record["ORIGEM"]:
        set_block_cities(record, text)

    set_km_model_a(record, text)
    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
