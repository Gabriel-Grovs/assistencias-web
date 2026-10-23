"""Produto: RENAULT (Portal de Assistência)."""

from ..helpers import make_record, extract_data, extract_city_field
from ._base import (
    set_assistencia,
    set_categoria,
    set_km_model_a,
    set_valor,
)


def extract(text):
    record = make_record("RENAULT")
    set_assistencia(record, text, "Assistencia")
    set_categoria(record, text, ["Servico", "Tipo de Servico"])
    record["ORIGEM"] = extract_city_field(text, 1) or ""
    record["DESTINO"] = extract_city_field(text, 2) or ""
    set_km_model_a(record, text)
    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
