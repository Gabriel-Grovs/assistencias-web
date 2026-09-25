"""Gravação de linhas no Google Sheets via Service Account (gspread).

As credenciais são fornecidas pela variável de ambiente ``GOOGLE_CREDENTIALS_JSON``
(JSON do Service Account serializado em string) e nunca ficam em arquivo no
repositório. A planilha e a aba são configuradas por ``GOOGLE_SHEET_ID`` e
``GOOGLE_SHEET_TAB``.
"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

from extractor.helpers import COLUMNS

_SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def _authorized_client():
    """Cria o cliente gspread autenticado via Service Account."""
    creds_raw = os.environ.get("GOOGLE_CREDENTIALS_JSON", "").strip()
    if not creds_raw:
        raise RuntimeError("GOOGLE_CREDENTIALS_JSON nao configurada")

    try:
        creds_info = json.loads(creds_raw, strict=False)
    except Exception:
        # Se contiver quebras de linha literais não escapadas
        cleaned = creds_raw.replace("\r\n", "\\n").replace("\n", "\\n")
        creds_info = json.loads(cleaned, strict=False)

    if isinstance(creds_info.get("private_key"), str) and "\\n" in creds_info["private_key"]:
        creds_info["private_key"] = creds_info["private_key"].replace("\\n", "\n")

    credentials = Credentials.from_service_account_info(creds_info, scopes=_SCOPES)
    return gspread.authorize(credentials)


def append_row(record):
    """Anexa uma linha ao final da planilha.

    Retorna ``{"ok": True, "linha": N}`` em caso de sucesso ou
    ``{"ok": False, "erro": ...}`` em caso de falha (sem lançar exceção).
    """
    sheet_id = os.environ.get("GOOGLE_SHEET_ID", "")
    tab = os.environ.get("GOOGLE_SHEET_TAB", "Assistencias")

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
