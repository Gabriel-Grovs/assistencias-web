"""Produto: PORTO (Laudo Digital)."""

from ..helpers import make_record, extract_data, assistencia_laudo, city_from_block, city_in_block
from ._base import set_categoria, set_km_model_a, set_valor


def extract(text):
    record = make_record("PORTO")
    record["ASSISTENCIA"] = assistencia_laudo(text) or ""
    if not record["ASSISTENCIA"]:
        from ._base import set_assistencia
        set_assistencia(record, text, ["Assistencia", "Ordem de Servico"])

    set_categoria(record, text, ["Tipo de Servico", "Problema", "Servico"])
    
    origem = city_from_block(text, "Endereco Ocorrencia")
    if not origem:
        origem = city_from_block(text, "Local da Ocorrencia")
    if not origem:
        origem = city_in_block(text, "Origem")
    if not origem:
        from ..helpers import extract_city_field
        origem = extract_city_field(text, 1)

    destino = city_from_block(text, "Endereco Destino")
    if not destino:
        destino = city_from_block(text, "Local de Destino")
    if not destino:
        destino = city_in_block(text, "Destino")
    if not destino:
        from ..helpers import extract_city_field
        c2 = extract_city_field(text, 2)
        if c2 and c2 != origem:
            destino = c2

    from ..helpers import clean_city
    record["ORIGEM"] = clean_city(origem) or ""
    record["DESTINO"] = clean_city(destino) or ""
    set_km_model_a(record, text)
    set_valor(record, text)
    record["DATA"] = extract_data(text)
    return record
