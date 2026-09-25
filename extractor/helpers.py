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
            r"(?:^|[\n\r\t,;-])[ \t]*" + accent_insensitive(label) + r"\s*[:=]?\s*([^\r\n]*)",
            re.IGNORECASE,
        )
        match = pattern.search(text)
        if not match:
            continue
        value = match.group(1).strip()
        if value:
            return value
        # Valor vazio: tenta a próxima linha não vazia.
        rest = text[match.end():].lstrip("\r\n\t ")
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
        r"(?:^|[\n\r\t,;-])[ \t]*" + accent_insensitive(label) + r"\s*[:=]?\s*([^\r\n]*)",
        re.IGNORECASE,
    )
    results = []
    for m in pattern.finditer(text):
        val = m.group(1).strip()
        if not val:
            # Pega da próxima linha não vazia
            rest = text[m.end():].lstrip("\r\n\t ")
            if rest:
                candidate = rest.splitlines()[0].strip()
                if not any(k in candidate.lower() for k in ["bairro", "estado", "cep", "regiao", "complemento", "referencia", "referencias"]):
                    val = candidate
        if val:
            results.append(val)
    return results


# ---------------------------------------------------------------------------
# Cidades
# ---------------------------------------------------------------------------

_UF_PATTERN = (
    r"AC|AL|AP|AM|BA|CE|DF|ES|GO|MA|MT|MS|MG|PA|PB|PR|PE|PI|RJ|RN|RS|RO|RR|SC|SP|SE|TO|"
    r"Acre|Alagoas|Amapa|Amapá|Amazonas|Bahia|Ceara|Ceará|Distrito Federal|Espirito Santo|Espírito Santo|"
    r"Goias|Goiás|Maranhao|Maranhão|Mato Grosso do Sul|Mato Grosso|Minas Gerais|Para|Pará|"
    r"Paraiba|Paraíba|Parana|Paraná|Pernambuco|Piaui|Piauí|Rio de Janeiro|Rio Grande do Norte|"
    r"Rio Grande do Sul|Rondonia|Rondônia|Roraima|Santa Catarina|Sao Paulo|São Paulo|Sergipe|Tocantins"
)

_NON_CITY_PATTERN = re.compile(
    r"\b(rua|av|avenida|rod|rodovia|estrada|travessa|alameda|praca|praça|cep|numero|número|s/n|"
    r"bairro|centro|complemento|referencia|referência|referencias|referências|latitude|longitude|"
    r"senha|tarifa|quantidade|subtotal|importante|problema|solicitante|cliente|veiculo|veículo|placa|ano|cor|combustivel|combustível|"
    r"nao cadastrada|não cadastrada|n inf|local seguro|facil acesso|fácil acesso|toda a cidade|proibida|alteracao|alteração|alterada|"
    r"comunicar|operacao|operação|facil assist|fácil assist|prestador|acionamento|"
    r"origem|destino|atendimento|partida|retorno|localidade|ocorrencia|ocorrência|waze|google|maps|"
    r"endereco|endereço|visao|visão|geral|dados|servico|serviço|anexos|observacoes|observações|"
    r"historico|histórico|situacao|situação|previa|prévia|chegada|motivo|checklist|informacoes|informações|"
    r"vazamento|oleo|óleo|agua|água|pane|oficina|concessionaria|concessionária)\b",
    re.IGNORECASE,
)


def is_valid_city(val):
    """Valida se uma string é um nome legítimo de cidade."""
    if not val:
        return False
    val_clean = val.strip()
    if val_clean.upper() == "BASE DO PRESTADOR":
        return True
    # Uma cidade não contém pontuação de formulário (: ; , / \t | = () [] {} " ? ! * ~)
    if re.search(r"[:;,/\t|=()\[\]{}\"?*!~\\_]", val_clean):
        return False
    if " - " in val_clean:
        return False
    if re.search(r"\d", val_clean):
        return False
    val_ascii = strip_accents(val_clean).lower()
    if _NON_CITY_PATTERN.search(val_ascii):
        return False
    return 2 <= len(val_clean) <= 45


def clean_city(value):
    """Limpa um valor de cidade: remove UF e pontuação pendente.

    Ex.: ``"Itamogi - MG"`` -> ``"Itamogi"``; ``"Ituverava/MG"`` -> ``"Ituverava"``.
    """
    if not value:
        return ""
    value = value.strip()
    if value.upper() == "BASE DO PRESTADOR":
        return "BASE DO PRESTADOR"
    value = re.sub(r"\s*[-/,]\s*[A-Za-z]{2}\s*$", "", value)
    value = re.sub(r"\s*-\s*$", "", value)
    value = value.strip(" -,\t\r\n")
    if not is_valid_city(value):
        return ""
    return value


def extract_city_field(text, occurrence=1):
    """Retorna a n-ésima ocorrência válida do campo ``Cidade:`` no texto."""
    if text is None:
        return None
    values = labeled_values(text, "Cidade")
    valid_cities = [clean_city(v) for v in values if clean_city(v)]
    if len(valid_cities) >= occurrence:
        return valid_cities[occurrence - 1]
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


def _is_plain_city(value):
    """Indica se uma linha parece conter apenas um nome de cidade."""
    if not value:
        return False
    return is_valid_city(value)


def city_from_line(line):
    """Extrai a cidade de uma linha de endereço, se identificável."""
    if not line:
        return None

    line_clean = re.sub(
        r"^(?:location_on|origem|destino|localidade)\s*[:=-]?\s*",
        "",
        line.strip(),
        flags=re.IGNORECASE,
    )

    # Padrão 1: "..., Cidade - MG - BR" ou "..., Cidade - Minas Gerais -" ou "... - Bairro, Cidade - SP"
    m_city_uf = re.search(
        r",\s*([A-Za-zÀ-ú' ]{2,35})\s*-\s*(?:" + _UF_PATTERN + r")\b",
        line_clean,
        re.IGNORECASE,
    )
    if m_city_uf:
        cand = clean_city(m_city_uf.group(1))
        if cand:
            return cand

    # Padrão 2: "Nome da Cidade - UF" ou "Nome da Cidade/UF" no fim da linha ou antes de - BR.
    match = re.search(
        r"([A-Za-zÀ-ú][A-Za-zÀ-ú' ]{1,45})\s*[-/]\s*(?:" + _UF_PATTERN + r")(?:\s*-\s*BR)?\s*$",
        line_clean,
        re.IGNORECASE,
    )
    if match:
        cand = clean_city(match.group(1))
        if cand:
            return cand

    # Fallback: linha com apenas um nome de cidade (ex.: "Origem: São Paulo").
    if _is_plain_city(line_clean):
        return clean_city(line_clean)
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
    lbl_lower = block_label.lower().strip()

    # 1. Particiona pelas seções ORIGEM / DESTINO quando presentes
    if lbl_lower in ("origem", "destino"):
        parts = re.split(r"^[ \t]*DESTINO\b", text or "", flags=re.IGNORECASE | re.MULTILINE)
        if lbl_lower == "origem":
            m_orig = re.search(r"^[ \t]*ORIGEM\b.*$", parts[0], flags=re.IGNORECASE | re.MULTILINE)
            section = parts[0][m_orig.end():] if m_orig else ""
        else:
            section = parts[1] if len(parts) > 1 else ""

        if section:
            tabular_city = extract_city_from_tabular_block(section)
            if tabular_city:
                return tabular_city
            city_vals = labeled_values(section, "Cidade")
            if city_vals:
                cand = clean_city(city_vals[0])
                if cand and cand != "BASE DO PRESTADOR":
                    return cand
            for line in section.splitlines()[:20]:
                cand = city_from_line(line)
                if cand and cand != "BASE DO PRESTADOR":
                    return cand
            if re.search(r"\bBASE\s+DO\s+PRESTADOR\b", section, re.IGNORECASE):
                return "BASE DO PRESTADOR"

    block = _block_after(text, block_label)
    if not block:
        return None

    tabular_city = extract_city_from_tabular_block(block)
    if tabular_city:
        return tabular_city

    city = extract_city_field(block, 1)
    if city and city != "BASE DO PRESTADOR":
        return city
    for line in block.splitlines():
        city = city_from_line(line)
        if city and city != "BASE DO PRESTADOR":
            return city

    if re.search(r"\bBASE\s+DO\s+PRESTADOR\b", block, re.IGNORECASE):
        return "BASE DO PRESTADOR"

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
        # Se tem ponto, verificar se é decimal (ex: 107.00 ou 5.2) ou milhar (ex: 1.000)
        if re.search(r"^\d+\.\d{1,2}$", value):
            pass  # Float decimal válido
        elif re.search(r"^\d+\.\d{3}$", value):
            value = value.replace(".", "")
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
