"""Três modelos de cálculo/extração de KM (briefing seção 8).

- Modelo A: somente KM explícito no texto (senão vazio).
- Modelo B: prioriza "Percurso Total"/"Distância Total", depois "KM Total",
  depois soma de componentes apenas se inequívoca.
- Modelo C: 40 (saída) + KM deslocamento + KM excedente, somente quando todos
  os componentes estão presentes.

Todas as funções retornam ``(km, obs)`` onde ``obs`` é uma flag para a coluna
OBS (string vazia quando não há alerta).
"""

from .helpers import extract_number


def model_a(text):
    """KM somente se explícito no texto."""
    for label in ("KM TOTAL", "PERCURSO TOTAL", "DISTANCIA TOTAL", "QUILOMETRAGEM TOTAL"):
        value = extract_number(text, label)
        if value is not None:
            return value, ""
    return "", ""


def model_b(text):
    """Percurso Total > Distância Total > KM Total > soma inequívoca."""
    percurso = extract_number(text, "PERCURSO TOTAL")
    if percurso is None:
        percurso = extract_number(text, "DISTANCIA TOTAL")
    if percurso is not None:
        return percurso, ""

    km_total = extract_number(text, "KM TOTAL")
    if km_total is not None:
        return km_total, ""

    # Soma de componentes apenas se inequívoca e sem Percurso Total.
    components = _sum_components(text)
    if components is not None:
        return components, ""

    return "", "ANALISE MANUAL - KM nao identificado"


def model_c(text):
    """40 (saída) + KM deslocamento + KM excedente."""
    deslocamento = extract_number(text, "KM DESLOCAMENTO")
    excedente = extract_number(text, "KM EXCEDENTE")
    if deslocamento is None or excedente is None:
        return "", "ANALISE MANUAL - componentes de KM ausentes"
    return str(40 + int(deslocamento) + int(excedente)), ""


def _sum_components(text):
    """Soma KM deslocamento + KM excedente (+ saída 40) se ambos existirem."""
    deslocamento = extract_number(text, "KM DESLOCAMENTO")
    excedente = extract_number(text, "KM EXCEDENTE")
    if deslocamento is None or excedente is None:
        return None
    return str(int(deslocamento) + int(excedente))
