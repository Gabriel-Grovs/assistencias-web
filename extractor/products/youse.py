"""Produto: YOUSE (Plataforma Operacional — Ordem de Serviço)."""

from ..helpers import make_record, extract_data
from ._base import set_assistencia, set_categoria, set_block_cities, set_km_model_b, set_valor


def extract(text):
    record = make_record("YOUSE")
    set_assistencia(record, text, "Ordem de Servico")
    set_categoria(record, text, ["Tipo de Servico", "Servico"])
    set_block_cities(record, text)
    set_km_model_b(record, text)
    set_valor(record, text, ("VALOR TOTAL",))
    record["DATA"] = extract_data(text)
    return record
