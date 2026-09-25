"""Produto: PORTO (Laudo Digital)."""

from ..helpers import make_record, extract_data, assistencia_laudo, city_from_block
from ._base import set_categoria, set_km_model_a, set_valor


def extract(text):
    record = make_record("PORTO")
    record["ASSISTENCIA"] = assistencia_laudo(text) or ""
    set_categoria(record, text, "Tipo de Servico")
    record["ORIGEM"] = city_from_block(text, "Endereco Ocorrencia") or ""
    record["DESTINO"] = city_from_block(text, "Endereco Destino") or ""
    set_km_model_a(record, text)
    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
