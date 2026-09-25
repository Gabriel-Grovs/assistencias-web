"""Produto: UNIDAS (Portal de Assistência — locadora)."""

from ..helpers import make_record, extract_data
from ._base import set_assistencia, set_categoria, set_block_cities, set_km_model_a


def extract(text):
    record = make_record("UNIDAS")
    set_assistencia(record, text, "Assistencia")
    set_categoria(record, text, "Servico")
    set_block_cities(record, text)
    set_km_model_a(record, text)
    record["VALOR"] = ""
    record["DATA"] = extract_data(text)
    return record
