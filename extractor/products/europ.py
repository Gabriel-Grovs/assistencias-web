"""Produto: EUROP (Plataforma Operacional / Sem Parar)."""

from ..helpers import make_record, extract_data
from ._base import (
    set_assistencia,
    set_categoria,
    set_locais_cities,
    set_block_cities,
)


def extract(text):
    record = make_record("EUROP")
    # Assistência: campo "# Serviço"
    set_assistencia(record, text, ["# Servico", "# Serviço", "Servico", "Serviço", "Assistencia"])
    set_categoria(record, text, ["Tipo de servico", "Tipo de serviço", "Servico", "Serviço"])

    # Locais do atendimento: (1) = ORIGEM, (2) = DESTINO
    set_locais_cities(record, text)
    if not record["ORIGEM"]:
        set_block_cities(record, text)

    # KM TOTAL e VALOR: sempre vazios conforme especificação EUROP.MD
    record["KM TOTAL"] = ""
    record["VALOR"] = ""
    record["DATA"] = extract_data(text)
    return record
