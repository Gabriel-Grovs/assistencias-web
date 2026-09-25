"""Funções auxiliares compartilhadas pelos extratores de produto.

Centraliza lógica de parsing de texto (campos rotulados, cidades, números,
datas e KM) para evitar duplicação entre os módulos de produto.

As mensagens recebidas são textos copiados de portais de seguradoras. Elas
variam de formato, então as helpers abaixo cobrem os padrões mais comuns:

- Campo rotulado: ``Assistencia: 123456``
- Cidade: ``Cidade: Itamogi`` ou ``Itamogi - MG``
- Números: ``KM Total: 413``, ``Valor Total: 250,00``
- Data: ``11/08/2026``
"""

import re
import unicodedata


# ---------------------------------------------------------------------------
# Normalização
# ---------------------------------------------------------------------------

def strip_accents(value):
    """Remove acentos e cedilha, retornando uma string ASCII."""
    if value is None:
        return ""
    normalized = unicodedata.normalize("NFKD", str(value))
    return "".join(c for c in normalized if not unicodedata.combining(c))


def accent_insensitive(word):
    """Gera um regex que casa ``word`` ignorando acentos e caixa.

    Ex.: ``accent_insensitive("Assistência")`` casa "Assistência", "assistencia",
    "ASSISTENCIA", etc.
    """
    mapping = {
        "a": "[aáàâãä]",
        "e": "[eéèêë]",
        "i": "[iíìîï]",
        "o": "[oóòôõö]",
        "u": "[uúùûü]",
        "c": "[cç]",
        "n": "[nñ]",
    }
    out = []
    for ch in word:
        low = ch.lower()
        if low in mapping:
            out.append(mapping[low])
        else:
            out.append(re.escape(ch))
    return "".join(out)


# ---------------------------------------------------------------------------
# Campos rotulados
# ---------------------------------------------------------------------------

def labeled_value(text, labels, value_regex=r"[^\n\r]+"):
    """Retorna o valor após o primeiro rótulo encontrado (``Rótulo: valor``).

    ``labels`` pode ser uma string ou uma lista. Se o valor na mesma linha
    estiver vazio, tenta capturar a linha seguinte.
    """
    if text is None:
        return None
    if isinstance(labels, str):
        labels = [labels]
    for label in labels:
        pattern = re.compile(
            accent_insensitive(label) + r"\s*[:=]\s*(" + value_regex + r")",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            continue
        value = match.group(1).strip()
        if value:
            return value
        # Valor vazio: tenta a próxima linha não vazia.
        rest = text[match.end():].lstrip("\r\n")
        if rest:
            first_line = rest.splitlines()[0].strip()
            if first_line:
                return first_line
    return None


def labeled_values(text, label, value_regex=r"[^\n\r]+"):
    """Retorna todos os valores após um rótulo (ex.: múltiplos ``Cidade:``)."""
    if text is None:
        return []
    pattern = re.compile(
        accent_insensitive(label) + r"\s*[:=]\s*(" + value_regex + r")",
        re.IGNORECASE,
    )
    return [m.group(1).strip() for m in pattern.finditer(text)]


# ---------------------------------------------------------------------------
# Cidades
# ---------------------------------------------------------------------------

def clean_city(value):
    """Limpa um valor de cidade: remove UF e pontuação pendente.

    Ex.: ``"Itamogi - MG"`` -> ``"Itamogi"``; ``"Ituverava/MG"`` -> ``"Ituverava"``.
    """
    if not value:
        return ""
    value = value.strip()
    value = re.sub(r"\s*[-/,]\s*[A-Z]{2}\s*$", "", value)
    value = re.sub(r"\s*-\s*$", "", value)
    value = value.strip(" -,\t\r\n")
    return value


def extract_city_field(text, occurrence=1):
    """Retorna a n-ésima ocorrência do campo ``Cidade:`` no texto."""
    if text is None:
        return None
    values = labeled_values(text, "Cidade")
    if len(values) >= occurrence:
        city = clean_city(values[occurrence - 1])
        return city or None
    return None


def assistencia_laudo(text):
    """Número após ``SERVIÇO`` (Laudo Digital), ignorando ``Tipo de Serviço``.

    No padrão Laudo Digital o campo ``SERVIÇO`` carrega o número da assistência,
    enquanto ``Tipo de Serviço`` carrega a categoria. Evita casar o rótulo
    ``Serviço`` dentro de ``Tipo de Serviço``.
    """
    if not text:
        return None
    pattern = re.compile(
        accent_insensitive("Servico") + r"\s*[:=]?\s*(\d[\w/.\-]*)", re.IGNORECASE
    )
    for match in pattern.finditer(text):
        prefix = strip_accents(text[max(0, match.start() - 15):match.start()]).upper()
        if "TIPO" in prefix:
            continue
        return match.group(1).strip()
    return None


_ADDRESS_KEYWORDS = (
    "rua", "av ", "avenida", "rod", "rodovia", "estrada", "travessa",
    "alameda", "praca", "cep", "numero", "base do prestador",
    "s/n", "bairro", "complemento", "referencia", "latitude", "longitude",
)


def _is_plain_city(value):
    """Indica se uma linha parece conter apenas um nome de cidade."""
    if not value:
        return False
    if re.search(r"\d", value):
        return False
    if not re.fullmatch(r"[A-Za-zÀ-ú][A-Za-zÀ-ú .'-]{0,60}", value):
        return False
    low = strip_accents(value).lower()
    return not any(kw in low for kw in _ADDRESS_KEYWORDS)


def city_from_line(line):
    """Extrai a cidade de uma linha de endereço, se identificável."""
    if not line:
        return None
    city = extract_city_field(line, 1)
    if city:
        return city
    # Padrão "Nome da Cidade - UF" ou "Nome da Cidade/UF" no fim da linha.
    # O hífen não faz parte do nome da cidade, evitando capturar o endereço.
    match = re.search(
        r"([A-Za-zÀ-ú][A-Za-zÀ-ú' ]{1,45})\s*[-/]\s*([A-Z]{2})\s*$", line.strip()
    )
    if match:
        return clean_city(match.group(1))
    # Fallback: linha com apenas um nome de cidade (ex.: "Origem: São Paulo").
    if _is_plain_city(line.strip()):
        return clean_city(line.strip())
    return None


def extract_city_from_tabular_block(block):
    """Extrai a cidade de uma tabela com colunas Bairro / Cidade / Estado."""
    if not block:
        return None
    lines = [l.strip() for l in block.splitlines() if l.strip()]
    for i, line in enumerate(lines):
        if re.search(r"\bCidade\b", line, re.IGNORECASE) and re.search(r"\b(Bairro|Estado|CEP)\b", line, re.IGNORECASE):
            cols = [c.strip() for c in re.split(r"\t+|\s{2,}", line) if c.strip()]
            cidade_idx = next((idx for idx, c in enumerate(cols) if re.search(r"\bCidade\b", c, re.IGNORECASE)), None)
            if cidade_idx is not None:
                # Caso 1: Valores tab-separated na linha seguinte
                if i + 1 < len(lines):
                    next_cols = [c.strip() for c in re.split(r"\t+|\s{2,}", lines[i + 1]) if c.strip()]
                    if len(next_cols) > cidade_idx:
                        return clean_city(next_cols[cidade_idx])
                # Caso 2: Cada coluna numa linha subsequente
                if i + 1 + cidade_idx < len(lines):
                    candidate = lines[i + 1 + cidade_idx]
                    if not re.search(r"\d", candidate) and len(candidate) <= 50:
                        return clean_city(candidate)
    return None


def _block_after(text, block_label):
    """Retorna o texto imediatamente após um rótulo de bloco (até ~15 linhas)."""
    if not text:
        return ""
    pattern = re.compile(accent_insensitive(block_label) + r"\s*[:=]?", re.IGNORECASE)
    match = pattern.search(text)
    if not match:
        return ""
    rest = text[match.end():]
    return "\n".join(rest.splitlines()[:15])


def city_in_block(text, block_label):
    """Extrai a cidade de dentro de um bloco rotulado (``Origem``/``Destino``)."""
    block = _block_after(text, block_label)
    if not block:
        return None

    tabular_city = extract_city_from_tabular_block(block)
    if tabular_city:
        return tabular_city

    city = extract_city_field(block, 1)
    if city:
        return city
    for line in block.splitlines():
        city = city_from_line(line)
        if city:
            return city
    return None


def city_from_block(text, block_label):
    """Extrai a cidade de um bloco de endereço (ex.: ``Endereço Ocorrência``)."""
    block = _block_after(text, block_label)
    if not block:
        return None
    city = extract_city_field(block, 1)
    if city:
        return city
    for line in block.splitlines()[:6]:
        line = line.strip()
        if not line:
            continue
        city = city_from_line(line)
        if city:
            return city
    return None


# ---------------------------------------------------------------------------
# Números e valores
# ---------------------------------------------------------------------------

def _parse_number(value):
    """Converte uma string numérica (BR ou US) em string normalizada."""
    if not value:
        return None
    value = re.sub(r"[^\d.,-]", "", value)
    if not value:
        return None
    if "," in value:
        # Formato brasileiro: ponto = milhar, vírgula = decimal.
        value = value.replace(".", "").replace(",", ".")
    else:
        value = value.replace(".", "")
    try:
        number = float(value)
    except ValueError:
        return None
    if number == int(number):
        return str(int(number))
    return ("%.2f" % number).rstrip("0").rstrip(".")


def extract_number(text, label):
    """Extrai o número que segue um rótulo (``KM Total: 413``)."""
    if not text:
        return None
    pattern = re.compile(
        accent_insensitive(label) + r"\s*[:=]?\s*([0-9][0-9.,]*)", re.IGNORECASE
    )
    match = pattern.search(text)
    if not match:
        return None
    return _parse_number(match.group(1))


# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------

# Rótulos que NÃO devem ser usados como DATA (regra 00 — fonte da data).
_IGNORED_DATE_LABELS = (
    "abertura",
    "aceito",
    "solicitacao",
    "combinada",
    "agendamento",
    "previsao",
)


def extract_data(text):
    """Extrai uma data DD/MM/AAAA do texto, evitando rótulos proibidos."""
    if not text:
        return ""
    for line in text.splitlines():
        if re.search(
            "|".join(accent_insensitive(lbl) for lbl in _IGNORED_DATE_LABELS),
            line,
            re.IGNORECASE,
        ):
            continue
        match = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", line)
        if match:
            return "{}/{}/{}".format(match.group(1), match.group(2), match.group(3))
    match = re.search(r"\b(\d{2})/(\d{2})/(\d{4})\b", text)
    if match:
        return "{}/{}/{}".format(match.group(1), match.group(2), match.group(3))
    return ""


# ---------------------------------------------------------------------------
# Registro
# ---------------------------------------------------------------------------

COLUMNS = [
    "DATA",
    "CLIENTE",
    "ASSISTENCIA",
    "CATEGORIA",
    "ORIGEM",
    "DESTINO",
    "KM TOTAL",
    "VALOR",
    "MOTORISTA",
    "VEICULO",
    "OBS",
]


def make_record(cliente):
    """Cria um registro vazio no schema padrão."""
    return {
        "DATA": "",
        "CLIENTE": cliente,
        "ASSISTENCIA": "",
        "CATEGORIA": "",
        "ORIGEM": "",
        "DESTINO": "",
        "KM TOTAL": "",
        "VALOR": "",
        "MOTORISTA": "",
        "VEICULO": "",
        "OBS": [],
    }


def flatten_record(record):
    """Une a lista de OBS em uma única string separada por `` | ``."""
    record = dict(record)
    record["OBS"] = " | ".join(record.get("OBS", []))
    return record
