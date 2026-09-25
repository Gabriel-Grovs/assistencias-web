"""Produto: TOKIO (Ordem de Serviço)."""

import re

from ..helpers import make_record, extract_data, city_in_block
from ._base import set_categoria, set_km_model_a


def _assistencia(text):
    match = re.search(r"\bOS[\s-]*\d[\w/.-]*", text or "", re.IGNORECASE)
    return match.group(0).replace(" ", "") if match else ""


def extract(text):
    record = make_record("TOKIO")
    record["ASSISTENCIA"] = _assistencia(text)
    set_categoria(record, text, ["Tipo de Evento", "Tipo de Servico"])
    
    origem = city_in_block(text, "Origem")
    if not origem:
        for line in (text or "").splitlines():
            if re.search(r"Localidade\s*:", line, re.IGNORECASE):
                from ..helpers import city_from_line
                origem = city_from_line(line)
                if origem:
                    break
    if not origem:
        origem = city_in_block(text, "Local")

    from ..helpers import clean_city
    record["ORIGEM"] = clean_city(origem) or ""
    record["DESTINO"] = ""
    set_km_model_a(record, text)
    record["VALOR"] = ""
    record["DATA"] = extract_data(text)
    return record
