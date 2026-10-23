"""Produto: PIER (Portal de Assistência)."""

import re
from ..helpers import make_record, extract_data, extract_city_field, labeled_value
from ._base import (
    set_categoria,
    set_km_model_a,
    set_valor,
)


def _extract_aceito_em(text):
    """Extrai data do campo 'Aceito em' no formato DD/MM/AAAA (desconsiderando horário)."""
    if not text:
        return ""
    m = re.search(r"Aceito\s+em\s*[:\n\r\t]*\s*(\d{2}/\d{2}/\d{4})", text, re.IGNORECASE)
    if m:
        return m.group(1)
    return ""


def extract(text):
    record = make_record("PIER")
    # Assistência: primeiro valor de Assistência (ignorar Solicitação conforme PIER.md)
    val = labeled_value(text, "Assistencia")
    record["ASSISTENCIA"] = val or ""
    set_categoria(record, text, "Servico")

    # Origem e Destino do bloco Local / Destino
    record["ORIGEM"] = extract_city_field(text, 1) or ""
    record["DESTINO"] = extract_city_field(text, 2) or ""

    # KM TOTAL: apenas se explícito (não usar Prazo)
    set_km_model_a(record, text)
    set_valor(record, text)

    # Data: "Aceito em" tem prioridade no PIER; fallback para data da mensagem
    data_aceito = _extract_aceito_em(text)
    if data_aceito:
        record["DATA"] = data_aceito
    else:
        record["DATA"] = extract_data(text)

    return record
