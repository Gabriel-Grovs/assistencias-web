"""Produto: MAXPAR (Portal / WhatsApp Maxpar - Sancor / Autoglass)."""

import re

from ..helpers import (
    make_record,
    city_from_line,
    clean_city,
)
from ..category_mapper import normalize_category


def _extract_header_date(text):
    """Extrai data de envio apenas se estiver em cabeçalho ou timestamp."""
    if not text:
        return ""
    lines = text.strip().splitlines()
    for line in lines[:3]:
        m = re.match(r"^(?:\[?(\d{2}/\d{2}/\d{4})[,\s].*|(\d{2}/\d{2}/\d{4}))", line.strip())
        if m:
            return m.group(1) or m.group(2)
    return ""


def extract(text):
    record = make_record("")  # Cliente vazio até confirmação de nome padronizado

    obs_list = []

    # 1. DATA: Somente data de envio identificável no cabeçalho/timestamp
    data_envio = _extract_header_date(text)
    if data_envio:
        record["DATA"] = data_envio
    else:
        record["DATA"] = ""
        obs_list.append("DATA IMPOSSIVEL DE IDENTIFICAR; ANALISE MANUAL")

    # 2. CLIENTE: Deixar vazio até confirmação de nome padronizado
    record["CLIENTE"] = ""
    if not any("ANALISE MANUAL" in o for o in obs_list):
        obs_list.append("ANALISE MANUAL")

    # 3. ASSISTENCIA: Ordem de serviço
    m_os = re.search(r"Ordem\s+de\s+servi[çc]o\s*[:\n\r]*\s*([A-Za-z0-9/.\-]+)", text or "", re.IGNORECASE)
    if m_os:
        record["ASSISTENCIA"] = m_os.group(1).strip()
    else:
        obs_list.append("ANALISE MANUAL - Ordem de servico ausente")

    # 4. CATEGORIA: Mapear Item cobertura
    m_cat = re.search(r"Item\s+(?:de\s+)?cobertura\s*[:\n\r]*\s*([^\n\r]+)", text or "", re.IGNORECASE)
    if m_cat:
        cat_raw = m_cat.group(1).strip()
        cat, cat_obs = normalize_category(cat_raw)
        if cat:
            record["CATEGORIA"] = cat
        else:
            record["CATEGORIA"] = ""
            if cat_obs and not any(cat_obs in o for o in obs_list):
                obs_list.append(cat_obs)
    else:
        obs_list.append("ANALISE MANUAL - Item cobertura ausente")

    # 5. ORIGEM: Cidade informada no campo Origem
    m_orig = re.search(r"Origem\s*[:\n\r]*\s*([^\n\r]+)", text or "", re.IGNORECASE)
    if m_orig:
        cidade = city_from_line(m_orig.group(1).strip())
        record["ORIGEM"] = clean_city(cidade) if cidade else ""
    else:
        record["ORIGEM"] = ""

    # 6. DESTINO: Preencher apenas se houver destino explicitamente informado
    m_dest = re.search(r"Destino\s*[:\n\r]*\s*([^\n\r]+)", text or "", re.IGNORECASE)
    if m_dest:
        cidade_dest = city_from_line(m_dest.group(1).strip())
        record["DESTINO"] = clean_city(cidade_dest) if cidade_dest else ""
    else:
        record["DESTINO"] = ""

    # 7. KM TOTAL: Percurso total com vírgula decimal e sem km
    m_km = re.search(r"Percurso\s+total\s*[:\n\r]*\s*([0-9.,]+)\s*(?:km)?", text or "", re.IGNORECASE)
    if m_km:
        val_km = m_km.group(1).strip().replace(".", ",")
        record["KM TOTAL"] = val_km
    else:
        record["KM TOTAL"] = ""

    # 8. VALOR: Valor total do serviço ou Total Maxpar com vírgula decimal e sem R$
    m_val = re.search(
        r"(?:Valor\s+total(?:\s+do\s+servi[çc]o)?|Total\s+Maxpar)\s*[:\n\r]*\s*(?:R\$\s*[\n\r]*\s*)?([0-9]+[.,][0-9]{2})",
        text or "",
        re.IGNORECASE,
    )
    if m_val:
        val = m_val.group(1).strip()
        if "." in val and "," in val:
            record["VALOR"] = val
        elif "." in val:
            record["VALOR"] = val.replace(".", ",")
        else:
            record["VALOR"] = val
    else:
        record["VALOR"] = ""

    record["MOTORISTA"] = ""
    record["VEICULO"] = ""
    record["OBS"] = obs_list

    return record
