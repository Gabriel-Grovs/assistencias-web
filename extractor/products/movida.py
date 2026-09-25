"""Produto: MOVIDA (Plataforma Operacional / WebPrestador / Movida 24h)."""

import re

from ..helpers import (
    make_record,
    extract_data,
    labeled_value,
    city_in_block,
    clean_city,
    extract_number,
    _parse_number,
)
from ..category_mapper import normalize_category


def _assistencia(text):
    # 1. WebPrestador: linha com tag seguida de número/código
    m_tag = re.search(r"\btag\s*\n\s*([A-Za-z0-9_#-]+)", text or "", re.IGNORECASE)
    if m_tag:
        return m_tag.group(1).strip()

    # 2. WebPrestador cabeçalho: #2026068380_B1 - Reboque Leve
    m_hash = re.search(r"#([A-Za-z0-9_]+(?:_[A-Za-z0-9]+)?)\s*-", text or "")
    if m_hash:
        return m_hash.group(1).strip()

    # 3. Portal Movida 24h: Protocolo:2026059419 ou Protocolo: 2026059419_B1
    m_proto = re.search(r"\bProtocolo\s*[:=]?\s*([A-Za-z0-9_#-]+)", text or "", re.IGNORECASE)
    if m_proto:
        return m_proto.group(1).strip()

    # 4. Atendimento especificamente rotulado com dois pontos ou número
    m_atend = re.search(r"\bAtendimento\s*[:=]\s*([A-Za-z0-9_#-]+)", text or "", re.IGNORECASE)
    if m_atend:
        return m_atend.group(1).strip()

    # 5. Fallback padrão labeled_value
    value = labeled_value(text, ["Protocolo", "Numero do Atendimento"])
    if value:
        return value.split()[0].strip()

    # 6. Fallback número grande no topo da mensagem
    match = re.search(r"\b\d{6,}\b", text or "")
    return match.group(0) if match else ""


def _categoria(text):
    # 1. WebPrestador: WebPrestador: Reboque Leve ou Assistência: Reboque Leve
    for lbl in ["WebPrestador", "Assistência", "Assistencia"]:
        val = labeled_value(text, lbl)
        if val:
            cat, _ = normalize_category(val)
            if cat:
                return cat

    # 2. Cabeçalho #2026068380_B1 - Reboque Leve
    m_hdr = re.search(r"#[A-Za-z0-9_#-]+\s*-\s*([^\n\r]+)", text or "")
    if m_hdr:
        cat, _ = normalize_category(m_hdr.group(1))
        if cat:
            return cat

    # 3. Movida 24h: Servico:REBOQUE LEVE / TROCA DE PNEU
    m_serv = re.search(r"\bServi[cç]o\s*[:=]\s*([^\n\r]+)", text or "", re.IGNORECASE)
    if m_serv:
        s_text = re.split(r"\b(?:Solicitante|Telefone|Previs[aã]o)\b", m_serv.group(1), flags=re.IGNORECASE)[0]
        cat, _ = normalize_category(s_text)
        if cat:
            return cat

    # 4. Labeled value padrão
    val = labeled_value(text, ["Tipo de Servico", "Tipo de Serviço", "Servico", "Serviço"])
    if val:
        cat, _ = normalize_category(val)
        if cat:
            return cat

    return ""


def _cidades(text):
    origem = city_in_block(text, "Origem")
    destino = city_in_block(text, "Destino")
    return clean_city(origem) or "", clean_city(destino) or ""


def _km(text):
    # 1. WebPrestador: route \n 70.00 Km
    m_route = re.search(r"\broute\s*\n\s*([0-9.,]+)\s*km", text or "", re.IGNORECASE)
    if m_route:
        val = _parse_number(m_route.group(1))
        if val:
            return val, ""

    # 2. Modelo B (Distância Total, Percurso Total, etc.)
    from ..km_calculator import model_b
    return model_b(text)


def _valor(text):
    # 1. WebPrestador: attach_money \n R$ 212,00
    m_money = re.search(r"\battach_money\s*\n\s*(?:R\$\s*)?([0-9.,]+)", text or "", re.IGNORECASE)
    if m_money:
        val = _parse_number(m_money.group(1))
        if val:
            return val

    # 2. Labeled values tradicionais
    for label in ("VALOR TOTAL DO SERVICO", "VALOR TOTAL", "VALOR"):
        val = extract_number(text, label)
        if val is not None:
            return val

    return ""


def extract(text):
    record = make_record("MOVIDA")
    record["ASSISTENCIA"] = _assistencia(text)
    
    cat = _categoria(text)
    if cat:
        record["CATEGORIA"] = cat
    else:
        record["OBS"].append("ANALISE MANUAL - categoria nao identificada")

    record["ORIGEM"], record["DESTINO"] = _cidades(text)

    km, obs_km = _km(text)
    record["KM TOTAL"] = km
    if obs_km:
        record["OBS"].append(obs_km)

    record["VALOR"] = _valor(text)
    record["DATA"] = extract_data(text)
    return record
