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

    # TOKIO: "Ordem de Serviço" + token iniciado por "OS".
    if re.search(r"ORDEM DE SERVIC", normalized) and re.search(r"\bOS\d", normalized):
        return "tokio"

    # Ordem de prioridade (briefing, seção 6).
    rules = [
        ("allianz", ["ALLIANZ"]),
        ("azul", ["AZUL SEGUROS"]),
        ("bradesco", ["BRADESCO AUTORE"]),
        ("caoa_chery", ["CAOA"]),
        ("fca_fiat", ["FCA FIAT", "FIAT CHRYSLER"]),
        ("hdi", ["HDI SEGUROS"]),
        ("movida", ["MOVIDA PARTICIPACOES", "MOVIDA"]),
        ("porto", ["PORTO SERVICO", "PORTO SEGURO"]),
        ("resolve_assist", ["RESOLVE ASSIST"]),
        ("santander", ["SANTANDER AUTO"]),
        ("suhai", ["SUHAI SEGURADORA"]),
        ("sura", ["SURA SEGUROS"]),
        ("tato_assist", ["TATO ASSIST"]),
        ("universo_agv", ["UNIVERSO AGV", "UNIVERSOAGV"]),
        ("velox", ["VELOX"]),
        ("yelum", ["YELUM"]),
        ("youse", ["YOUSE SEGUROS"]),
    ]

    for key, patterns in rules:
        for pattern in patterns:
            if re.search(accent_insensitive(pattern), text, re.IGNORECASE):
                return key

    # Fallbacks por protocolo (sem marca explícita no corpo).
    if re.search(r"\bRES\d", normalized):
        return "resolve_assist"
    if re.search(r"PROTOCOLO\s*[:=]\s*202", normalized):
        return "tato_assist"

    return "unknown"
