"""Funções comuns reutilizadas pelos módulos de produto.

Cada produto tem peculiaridades, mas vários compartilham os mesmos padrões de
extração (Portal de Assistência, Plataforma Operacional, Laudo Digital). Estas
helpers evitam duplicação e mantêm os módulos de produto enxutos e fáceis de
ajustar.
"""

import re

from ..helpers import (
    accent_insensitive,
    city_from_line,
    city_in_block,
    city_from_block,
    clean_city,
    is_valid_city,
    extract_city_field,
    extract_number,
    labeled_value,
)
from ..category_mapper import normalize_category
from .. import km_calculator


def set_assistencia(record, text, labels):
    """Define ASSISTENCIA a partir de tabela ou rótulos, incluindo barra se houver."""
    # 1. Padrão tabular com cabeçalho (ex.: Assistência \t Solicitação ...)
    m = re.search(r"Assist[eê]ncia\s+Solicita[cç][aã]o", text or "", re.IGNORECASE)
    if m:
        rest = (text or "")[m.start():]
        lines = [l.strip() for l in rest.splitlines() if l.strip()]
        if len(lines) >= 3:
            num = lines[1]
            barra = lines[2]
            if re.match(r"^\d+$", num):
                if re.match(r"^\d+$", barra):
                    record["ASSISTENCIA"] = f"{num}/{barra}"
                    return
                record["ASSISTENCIA"] = num
                return

    # 2. Padrão labeled_value (com ou sem barra)
    val = labeled_value(text, labels)
    if val:
        solic = labeled_value(text, ["Solicitacao", "Solicitação", "Barra"])
        if solic and "/" not in val and re.match(r"^\d+$", solic):
            record["ASSISTENCIA"] = f"{val}/{solic}"
        else:
            record["ASSISTENCIA"] = val
    else:
        record["ASSISTENCIA"] = ""


def set_categoria(record, text, label="Servico"):
    """Define CATEGORIA a partir de SERVIÇO #1 ou campo rotulado."""
    # 1. Padrão SERVIÇO #1 \n Nome do serviço
    m = re.search(r"SERVI[ÇC]O\s*(?:#\d+)?\s*\n\s*([^\n]+)", text or "", re.IGNORECASE)
    if m:
        candidate = m.group(1).strip()
        cat, obs = normalize_category(candidate)
        if cat:
            record["CATEGORIA"] = cat
            return

    # 2. Padrão com múltiplas linhas após Serviço: (ex.: Serviço:\nREBOQUE\nEXTRA PESADO)
    lbl_first = label[0] if isinstance(label, list) else label
    pattern = re.compile(
        r"(?:^|[\n\r\t,;-])[ \t]*" + accent_insensitive(lbl_first) + r"\s*[:=]?\s*(.*)",
        re.IGNORECASE,
    )
    m_val = pattern.search(text or "")
    if m_val:
        lines = (text or "")[m_val.start():].splitlines()[:4]
        combined = " ".join(l.strip() for l in lines if l.strip())
        cat, obs = normalize_category(combined)
        if cat:
            record["CATEGORIA"] = cat
            return

    # 3. Padrão labeled_value padrão
    categoria, obs = normalize_category(labeled_value(text, label))
    if categoria:
        record["CATEGORIA"] = categoria
    elif obs:
        record["OBS"].append(obs)


def set_categoria_raw(record, raw):
    """Define CATEGORIA a partir de uma string bruta."""
    categoria, obs = normalize_category(raw)
    if categoria:
        record["CATEGORIA"] = categoria
    if obs:
        record["OBS"].append(obs)


def set_portal_cities(record, text):
    """Origem = 1º campo Cidade, Destino = 2º campo Cidade (Portal de Assistência)."""
    record["ORIGEM"] = extract_city_field(text, 1) or ""
    record["DESTINO"] = extract_city_field(text, 2) or ""


def set_block_cities(record, text):
    """Origem/Destino a partir de blocos rotulados ``Origem`` e ``Destino`` com fallbacks."""
    origem = city_in_block(text, "Origem")
    destino = city_in_block(text, "Destino")

    if not origem:
        origem = city_from_block(text, "Endereco Ocorrencia")
    if not origem:
        origem = city_from_block(text, "Localidade")
    if not origem:
        origem = city_from_block(text, "Local da Ocorrencia")
    if not origem:
        origem = city_from_block(text, "Local")
    if not origem:
        origem = extract_city_field(text, 1)

    if not destino:
        destino = city_from_block(text, "Endereco Destino")
    if not destino:
        destino = city_from_block(text, "Local de Destino")
    if not destino:
        c2 = extract_city_field(text, 2)
        if c2 and c2 != origem:
            destino = c2

    record["ORIGEM"] = clean_city(origem) or ""
    record["DESTINO"] = clean_city(destino) or ""


def set_locais_cities(record, text):
    """BRADESCO/FCA: ``LOCAIS DO ATENDIMENTO`` com endereços (1) e (2)."""
    block = text or ""
    match = re.search(accent_insensitive("LOCAIS DO ATENDIMENTO"), text or "", re.IGNORECASE)
    if match:
        block = text[match.end():]
    origem = destino = ""
    for line in block.splitlines()[:12]:
        stripped = line.strip()
        if not stripped:
            continue
        if re.match(r"\(\s*1\s*\)", stripped):
            origem = city_from_line(stripped) or ""
        elif re.match(r"\(\s*2\s*\)", stripped):
            destino = city_from_line(stripped) or ""
    record["ORIGEM"] = origem
    record["DESTINO"] = destino


def set_km_model_a(record, text):
    """Modelo A: KM somente se explícito."""
    km, obs = km_calculator.model_a(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_km_model_b(record, text):
    """Modelo B: Percurso Total com prioridades."""
    km, obs = km_calculator.model_b(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_km_model_c(record, text):
    """Modelo C: 40 + deslocamento + excedente."""
    km, obs = km_calculator.model_c(text)
    record["KM TOTAL"] = km
    if obs:
        record["OBS"].append(obs)


def set_valor(record, text, labels=("VALOR TOTAL DO SERVICO", "VALOR TOTAL", "VALOR")):
    """Define VALOR a partir de um rótulo de valor explícito."""
    for label in labels:
        value = extract_number(text, label)
        if value is not None:
            record["VALOR"] = value
            return
    record["VALOR"] = ""
