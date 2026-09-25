"""Normalização de categorias de serviço para o vocabulário padrão.

Mapeamento universal (briefing seção 7 + regras por produto):

- REBOQUE/PLATAFORMA, PATINS, GUINCHO PLATAFORMA -> LEVE
- UTILITÁRIO -> UTILITARIO
- PESADO -> PESADO
- EXTRA PESADO -> EXTRA PESADO
- TAXI / TRANSPORTE -> TAXI
- CHAVEIRO -> CHAVEIRO
- PNEU -> TROCA PNEU
- PANE / SOCORRO / MECÂNICA / ELÉTRICA -> SOCORRO MECANICO
- REBOQUE/GUINCHO sem porte claro -> ANALISE MANUAL
"""

import re

from .helpers import strip_accents


def normalize_category(raw):
    """Normaliza uma descrição de serviço.

    Retorna ``(categoria, obs)``. Quando a categoria não pode ser determinada,
    ``categoria`` é ``""`` e ``obs`` recebe o motivo para ``ANALISE MANUAL``.
    """
    if not raw:
        return "", "ANALISE MANUAL - categoria nao identificada"

    value = strip_accents(raw).upper()
    value = re.sub(r"\s+", " ", value).strip()

    if "EXTRA PESADO" in value:
        return "EXTRA PESADO", ""
    if "UTILITARIO" in value or "UTILITARIOS" in value:
        return "UTILITARIO", ""
    if "PESADO" in value:
        return "PESADO", ""
    if "PLATAFORMA" in value or "PATINS" in value:
        return "LEVE", ""
    if "LEVE" in value:
        return "LEVE", ""
    if "MOTO" in value or "MOTOCICLETA" in value:
        return "LEVE", ""
    if "TAXI" in value or "TRANSPORTE" in value:
        return "TAXI", ""
    if "CHAVEIRO" in value:
        return "CHAVEIRO", ""
    if "PNEU" in value:
        return "TROCA PNEU", ""
    if "BATERIA" in value or "RECARGA" in value:
        return "CARGA DE BATERIA", ""
    if "ELETRIC" in value or "LAMPADA" in value or "TOMADA" in value or "INTERRUPTOR" in value or "DISJUNTOR" in value:
        if "REPARO" in value or "DOMICIL" in value or "RESIDENC" in value or "LAMPADA" in value or "TOMADA" in value:
            return "ELETRICISTA", ""
        return "SOCORRO MECANICO", ""
    if "ENCANADOR" in value or "HIDRAULIC" in value or "DESENTUP" in value or "VAZAMENTO" in value:
        return "RESIDENCIAL", ""
    if "DOMICIL" in value or "RESIDENC" in value or "FIXACO" in value or "CASA" in value or "VIDRACEIRO" in value:
        return "RESIDENCIAL", ""
    if "PANE" in value or "SOCORRO" in value or "MECANIC" in value:
        return "SOCORRO MECANICO", ""
    if "REBOQUE" in value or "GUINCHO" in value:
        return "", "ANALISE MANUAL - porte do reboque nao identificado"
    return "", "ANALISE MANUAL - categoria nao identificada"
