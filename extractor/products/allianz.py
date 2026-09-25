"""Produto: ALLIANZ (Portal de Assistência)."""

from ..helpers import make_record, extract_data
from ._base import (
    set_assistencia,
    set_categoria,
    set_portal_cities,
    set_km_model_a,
    set_valor,
)


def extract(text):
    record = make_record("ALLIANZ")
    set_assistencia(record, text, "Assistencia")
    set_categoria(record, text, "Servico")
    set_portal_cities(record, text)
    set_km_model_a(record, text)
    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
