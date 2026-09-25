"""Produto: TOKIO (Ordem de Serviço)."""

import re

from ..helpers import make_record, extract_data, city_in_block
from ._base import set_categoria, set_km_model_a


def _assistencia(text):
    match = re.search(r"\bOS[\s-]*\d[\w/.-]*", text or "", re.IGNORECASE)
    if match:
        return match.group(0).replace(" ", "")
    m_num = re.search(r"(?:Numero\s+da\s+)?Assist[eê]ncia\s*[:=]?\s*(\d[\w/.-]*)", text or "", re.IGNORECASE)
    if m_num:
        return m_num.group(1).strip()
    return ""


def extract(text):
    record = make_record("TOKIO")
    record["ASSISTENCIA"] = _assistencia(text)
    set_categoria(record, text, ["Tipo de Servico", "Tipo de Evento"])
    
    # Origem
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

    # Destino
    destino = city_in_block(text, "Destino")
    if not destino:
        for line in (text or "").splitlines():
            if re.search(r"Destino\s*:", line, re.IGNORECASE):
                from ..helpers import city_from_line
                destino = city_from_line(line)
                if destino:
                    break

    from ..helpers import clean_city
    record["ORIGEM"] = clean_city(origem) or ""
    record["DESTINO"] = clean_city(destino) or ""

    # KM: modelo A explícito ou extração da linha KM nos Serviços
    set_km_model_a(record, text)
    if not record["KM TOTAL"]:
        m_km = re.search(r"\bKM\s+(\d+)\b", text or "", re.IGNORECASE)
        if not m_km:
            m_km = re.search(r"\bKM\t+(\d+)\b", text or "", re.IGNORECASE)
        if m_km:
            record["KM TOTAL"] = m_km.group(1)

    record["VALOR"] = ""
    record["DATA"] = extract_data(text)
    return record
