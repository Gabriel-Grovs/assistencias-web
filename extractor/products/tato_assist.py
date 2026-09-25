"""Produto: TATO ASSIST (Plataforma Operacional — Protocolo)."""

from ..helpers import make_record, extract_data
from ._base import set_assistencia, set_categoria, set_block_cities, set_km_model_b, set_valor


def extract(text):
    record = make_record("TATO ASSIST")
    set_assistencia(record, text, "Protocolo")
    set_categoria(record, text, ["Tipo de Servico", "Servico"])
    set_block_cities(record, text)
    set_km_model_b(record, text)
    set_valor(record, text, ("VALOR",))
    record["DATA"] = extract_data(text)
    return record
