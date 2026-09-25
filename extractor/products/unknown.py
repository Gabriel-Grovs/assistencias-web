"""Produto: DESCONHECIDO (fallback)."""

from ..helpers import make_record, extract_data


def extract(text):
    record = make_record("")
    record["OBS"].append("ANALISE MANUAL - produto nao identificado")
    record["DATA"] = extract_data(text)
    return record
