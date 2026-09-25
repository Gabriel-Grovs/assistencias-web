"""Produto: SUHAI (Portal de Assistência — KM Modelo C se tarifa presente)."""

from ..helpers import make_record, extract_data
from .. import km_calculator
from ._base import (
    set_assistencia,
    set_categoria,
    set_portal_cities,
    set_valor,
)


def extract(text):
    record = make_record("SUHAI")
    set_assistencia(record, text, "Assistencia")
    set_categoria(record, text, "Servico")
    set_portal_cities(record, text)

    # Modelo C quando a tarifa de KM está presente; senão, KM explícito (Modelo A).
    km, obs = km_calculator.model_c(text)
    if not km:
        km, obs = km_calculator.model_a(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)

    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
