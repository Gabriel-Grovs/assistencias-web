"""Identificação do produto (seguradora/montadora) pelo conteúdo da mensagem.

A identificação é feita pela presença de strings-chave no texto, em ordem de
prioridade definida no briefing. O identificador retornado é a chave usada
para localizar o módulo de extração correspondente em ``extractor.products``.
"""

import re

from .helpers import accent_insensitive, strip_accents


def identify(text):
    """Retorna a chave do produto identificado ou ``"unknown"``.

    Exemplos de chave: ``"tokio"``, ``"allianz"``, ``"caoa_chery"``.
    """
    if not text:
        return "unknown"

    normalized = strip_accents(text).upper()
    # Remove marcação de negrito/itálico do WhatsApp (*, _)
    clean_text = re.sub(r"[*_~]", "", normalized)

    # TOKIO: marca explícita ou padrão de Ordem de Serviço com OS
    if re.search(r"\bTOKIO\b", clean_text) or re.search(r"\bTOKIO MARINE\b", clean_text):
        return "tokio"
    if re.search(r"ORDEM DE SERVIC", clean_text) and re.search(r"\bOS[\s-]*\d", clean_text):
        return "tokio"
    if re.search(r"NUMERO DA ASSIST", clean_text) and re.search(r"\bOS[\s-]*\d", clean_text):
        return "tokio"

    # Ordem de prioridade (briefing, seção 6 + histórico real).
    rules = [
        ("tokio", ["TOKIO MARINE", "TOKIO"]),
        ("allianz", ["ALLIANZ"]),
        ("azul", ["AZUL SEGUROS"]),
        ("bradesco", ["BRADESCO AUTORE", "BRADESCO SEGUROS", "BRADESCO"]),
        ("caoa_chery", ["CAOA CHERY", "CAOA MONTADORA", "CAOA"]),
        ("fca_fiat", ["FCA FIAT", "FIAT CHRYSLER"]),
        ("hdi", ["HDI SEGUROS", "HDI"]),
        ("movida", ["MOVIDA PARTICIPACOES", "MOVIDA"]),
        ("porto", ["PORTO SERVICO", "PORTO SEGURO", "LAUDO DE SERVICO - PORTO", "EMPRESA\tPORTO", "EMPRESA PORTO", "LAUDO DIGITAL", "PORTO"]),
        ("resolve_assist", ["RESOLVE ASSIST"]),
        ("santander", ["SANTANDER AUTO", "SANTANDER"]),
        ("suhai", ["SUHAI SEGURADORA", "SUHAI"]),
        ("sura", ["SURA SEGUROS", "SURA"]),
        ("tato_assist", ["TATO ASSIST"]),
        ("universo_agv", ["UNIVERSO AGV", "UNIVERSOAGV"]),
        ("velox", ["VELOX"]),
        ("yelum", ["YELUM"]),
        ("youse", ["YOUSE SEGUROS", "YOUSE"]),
        ("unidas", ["UNIDAS"]),
    ]

    for key, patterns in rules:
        for pattern in patterns:
            # Testa tanto no texto original quanto no limpo
            if re.search(r"\b" + accent_insensitive(pattern) + r"\b", clean_text, re.IGNORECASE) or \
               re.search(accent_insensitive(pattern), text, re.IGNORECASE):
                return key

    # Fallbacks por protocolo (sem marca explícita no corpo, inclusive via WhatsApp).
    if re.search(r"\bRES\d", clean_text):
        return "resolve_assist"
    if re.search(r"PROTOCOLO\s*[:=]\s*202", clean_text):
        return "tato_assist"

    return "unknown"
