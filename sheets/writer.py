"""Gravação de linhas no Google Sheets via Service Account (gspread).

As credenciais são fornecidas pela variável de ambiente ``GOOGLE_CREDENTIALS_JSON``
(JSON do Service Account serializado em string) e nunca ficam em arquivo no
repositório. A planilha e a aba são configuradas por ``GOOGLE_SHEET_ID`` e
``GOOGLE_SHEET_TAB``.
"""

import base64
import json
import os
import re

from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

from extractor.helpers import COLUMNS

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _normalize_private_key(pk):
    """Normaliza a chave privada PEM para o formato canônico.

    Corrige quebras de linha substituídas por espaços, caracteres de escape
    múltiplos (\\n, \\\\n), cabeçalhos ausentes ou quebras CRLF do Windows.
    """
    if not isinstance(pk, str):
        return pk

    pk = pk.strip()
    while "\\\\n" in pk:
        pk = pk.replace("\\\\n", "\n")
    pk = pk.replace("\\n", "\n").replace("\r", "\n")

    # Extrai o corpo base64 entre cabeçalho e rodapé
    match = re.search(r"-----BEGIN [A-Z ]+KEY-----(.*?)-----END [A-Z ]+KEY-----", pk, re.DOTALL)
    if match:
        body = re.sub(r"[^A-Za-z0-9+/=]", "", match.group(1))
    else:
        body = re.sub(r"[^A-Za-z0-9+/=]", "", pk)

    # Quebra o base64 em linhas padrão de 64 caracteres
    lines = [body[i : i + 64] for i in range(0, len(body), 64)]
    return "-----BEGIN PRIVATE KEY-----\n" + "\n".join(lines) + "\n-----END PRIVATE KEY-----\n"


def _parse_credentials_info():
    """Lê e sanitiza o JSON das credenciais do Google Service Account."""
    creds_raw = os.environ.get("GOOGLE_CREDENTIALS_JSON", "").strip()
    if not creds_raw:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON nao configurada no Render")

    text = creds_raw
    # Remove aspas externas se a variável foi colada entre aspas
    if text.startswith("'") and text.endswith("'"):
        text = text[1:-1].strip()
    elif text.startswith('"') and text.endswith('"'):
        try:
            text = json.loads(text)
        except Exception:
            text = text[1:-1].strip()

    # Suporte a credenciais codificadas em base64
    if not text.startswith("{"):
        try:
            decoded = base64.b64decode(text).decode("utf-8")
            if decoded.strip().startswith("{"):
                text = decoded.strip()
        except Exception:
            pass

    try:
        creds_info = json.loads(text, strict=False)
    except Exception:
        cleaned = text.replace("\r\n", "\\n").replace("\n", "\\n")
        creds_info = json.loads(cleaned, strict=False)

    if "private_key" in creds_info:
        creds_info["private_key"] = _normalize_private_key(creds_info["private_key"])

    return creds_info


def _authorized_client():
    """Cria o cliente gspread autenticado via Service Account."""
    creds_info = _parse_credentials_info()
    credentials = Credentials.from_service_account_info(creds_info, scopes=_SCOPES)
    return gspread.authorize(credentials)


def append_row(record):
    """Anexa uma linha ao final da planilha.

    Retorna ``{"ok": True, "linha": N}`` em caso de sucesso ou
    ``{"ok": False, "erro": ...}`` em caso de falha (sem lançar exceção).
    """
    sheet_id = os.environ.get("GOOGLE_SHEET_ID") or "1OMof37tDGTYj0JKV2A34QN42OB49en6B0Ro1w5tDwl8"
    tab = os.environ.get("GOOGLE_SHEET_TAB") or "Assistencias"

    if not sheet_id:
        return {"ok": False, "erro": "GOOGLE_SHEET_ID nao configurada"}

    try:
        client = _authorized_client()
        sheet = client.open_by_key(sheet_id)
        worksheet = sheet.worksheet(tab)
        row = [record.get(col, "") for col in COLUMNS]
        worksheet.append_row(row, value_input_option="USER_ENTERED")
        total = len(worksheet.get_all_values())
        return {"ok": True, "linha": total}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "erro": str(exc)}
