"""Orquestrador da extração.

Identifica o produto, delega a extração ao módulo específico e normaliza o
registro final para o schema padrão (``helpers.COLUMNS``). O campo extra
``PRODUTO`` (chave interna) é incluído apenas para exibição no frontend e não
faz parte das colunas gravadas na planilha.
"""

import importlib

from . import identifier
from .helpers import COLUMNS, extract_data

_PRODUCT_MODULES = {
    "allianz": "allianz",
    "azul": "azul",
    "bradesco": "bradesco",
    "caoa_chery": "caoa_chery",
    "fca_fiat": "fca_fiat",
    "hdi": "hdi",
    "movida": "movida",
    "porto": "porto",
    "resolve_assist": "resolve_assist",
    "santander": "santander",
    "suhai": "suhai",
    "sura": "sura",
    "tato_assist": "tato_assist",
    "tokio": "tokio",
    "universo_agv": "universo_agv",
    "velox": "velox",
    "yelum": "yelum",
    "youse": "youse",
    "unidas": "unidas",
    "unknown": "unknown",
}


def extract_record(text):
    """Extrai um registro completo a partir do texto colado."""
    key = identifier.identify(text)
    module_name = _PRODUCT_MODULES.get(key, "unknown")
    module = importlib.import_module("extractor.products." + module_name)
    record = module.extract(text)

    if not record.get("DATA"):
        record["DATA"] = extract_data(text)

    for col in COLUMNS:
        record.setdefault(col, "")

    obs = record["OBS"]
    if not isinstance(obs, list):
        obs = [obs]
    record["OBS"] = " | ".join(obs)

    record["PRODUTO"] = key
    return record
